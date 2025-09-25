"""
Challenge routes for browsing, submitting, and managing CTF challenges
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import json

from models import User, Challenge, Category, Submission, db
from utils.validators import validate_flag_format, sanitize_input, validate_multi_flag

challenges_bp = Blueprint('challenges', __name__)

# Rate limiting for challenge submissions
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@challenges_bp.route('/', methods=['GET'])
def get_challenges():
    """Get all active challenges"""
    try:
        # Query parameters
        category_id = request.args.get('category_id', type=int)
        difficulty = request.args.get('difficulty')
        search = request.args.get('search', '').strip()
        include_hidden = request.args.get('include_hidden', 'false').lower() == 'true'
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Base query
        if include_hidden:
            # For admin panel - show all challenges including hidden ones
            query = Challenge.query.filter_by(is_active=True)
        else:
            # For regular users - only show visible challenges
            query = Challenge.query.filter_by(is_active=True, is_hidden=False)
        
        # Apply filters
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        
        if search:
            query = query.filter(
                Challenge.title.contains(search) | 
                Challenge.description.contains(search)
            )
        
        # Order by points (ascending for easier challenges first)
        query = query.order_by(Challenge.points.asc(), Challenge.created_at.desc())
        
        # Pagination
        challenges = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Convert to dict
        challenges_data = [challenge.to_dict() for challenge in challenges.items]
        
        return jsonify({
            'challenges': challenges_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': challenges.total,
                'pages': challenges.pages,
                'has_next': challenges.has_next,
                'has_prev': challenges.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get challenges error: {str(e)}")
        return jsonify({'error': 'Failed to fetch challenges'}), 500

@challenges_bp.route('/<int:challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    """Get specific challenge details"""
    try:
        challenge = Challenge.query.filter_by(
            id=challenge_id, 
            is_active=True, 
            is_hidden=False
        ).first()
        
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        # Get user's submission history for this challenge
        user_submissions = []
        if request.headers.get('Authorization'):
            try:
                from flask_jwt_extended import verify_jwt_in_request
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                submissions = Submission.query.filter_by(
                    user_id=current_user_id,
                    challenge_id=challenge_id
                ).order_by(Submission.submitted_at.desc()).all()
                
                user_submissions = [sub.to_dict() for sub in submissions]
            except:
                pass  # User not authenticated or invalid token
        
        challenge_data = challenge.to_dict()
        challenge_data['user_submissions'] = user_submissions
        
        return jsonify({'challenge': challenge_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get challenge error: {str(e)}")
        return jsonify({'error': 'Failed to fetch challenge'}), 500

@challenges_bp.route('/<int:challenge_id>/submit', methods=['POST'])
@jwt_required()
@limiter.limit("30 per hour")
def submit_flag(challenge_id):
    """Submit flag for a challenge"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        # Debug logging
        current_app.logger.info(f"Submission attempt - User ID: {current_user_id}, Username: {user.username if user else 'None'}")
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        challenge = Challenge.query.filter_by(
            id=challenge_id, 
            is_active=True
        ).first()
        
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        data = request.get_json()
        if not data or 'flag' not in data:
            return jsonify({'error': 'Flag is required'}), 400
        
        submitted_flag = sanitize_input(data['flag'].strip())
        
        if not validate_flag_format(submitted_flag):
            return jsonify({'error': 'Invalid flag format'}), 400
        
        # Check if flag is correct and determine flag type (support multi-part flags)
        is_correct = False
        flag_type = None
        if challenge.multi_flags:
            try:
                expected_flags = json.loads(challenge.multi_flags)
                is_correct = validate_multi_flag(submitted_flag, expected_flags)
                # Determine which flag type was submitted
                if is_correct:
                    for flag_key, flag_value in expected_flags.items():
                        if submitted_flag == f"{flag_key}{{{flag_value}}}":
                            flag_type = flag_key
                            break
            except (json.JSONDecodeError, TypeError):
                # Fallback to single flag if multi_flags is invalid
                is_correct = submitted_flag == challenge.flag
                flag_type = 'flag'
        else:
            # Single flag format
            is_correct = submitted_flag == challenge.flag
            flag_type = 'flag'
        
        # Check for duplicate submissions
        if is_correct:
            if challenge.multi_flags and flag_type:
                # For multi-part challenges, check if this specific flag type was already submitted
                existing_correct = Submission.query.filter_by(
                    user_id=current_user_id,
                    challenge_id=challenge_id,
                    is_correct=True,
                    flag_type=flag_type
                ).first()
                
                if existing_correct:
                    return jsonify({'error': f'Flag type {flag_type} already submitted correctly'}), 409
            else:
                # For single-flag challenges, check if already solved
                existing_correct = Submission.query.filter_by(
                    user_id=current_user_id,
                    challenge_id=challenge_id,
                    is_correct=True
                ).first()
                
                if existing_correct:
                    return jsonify({'error': 'Challenge already solved'}), 409
        
        # Create submission record
        submission = Submission(
            user_id=current_user_id,
            challenge_id=challenge_id,
            submitted_flag=submitted_flag,
            is_correct=is_correct,
            flag_type=flag_type,
            submitted_at=datetime.utcnow(),
            ip_address=request.remote_addr
        )
        
        db.session.add(submission)
        
        # Update user score if correct
        if is_correct:
            # For multi-part challenges, only add score when all parts are completed
            if challenge.multi_flags and flag_type:
                try:
                    expected_flags = json.loads(challenge.multi_flags)
                    # Check if all flag types have been submitted correctly
                    all_parts_completed = True
                    for flag_key in expected_flags.keys():
                        existing_part = Submission.query.filter_by(
                            user_id=current_user_id,
                            challenge_id=challenge_id,
                            is_correct=True,
                            flag_type=flag_key
                        ).first()
                        if not existing_part:
                            all_parts_completed = False
                            break
                    
                    if all_parts_completed:
                        user.total_score += challenge.points
                        current_app.logger.info(f"User {user.username} solved challenge {challenge.title} (+{challenge.points} points)")
                    else:
                        current_app.logger.info(f"User {user.username} submitted correct {flag_type} for {challenge.title}")
                except (json.JSONDecodeError, TypeError):
                    # Fallback to single flag logic
                    user.total_score += challenge.points
                    current_app.logger.info(f"User {user.username} solved challenge {challenge.title} (+{challenge.points} points)")
            else:
                # Single flag challenge
                user.total_score += challenge.points
                current_app.logger.info(f"User {user.username} solved challenge {challenge.title} (+{challenge.points} points)")
        
        db.session.commit()
        
        # Determine response message
        if is_correct:
            if challenge.multi_flags and flag_type:
                try:
                    expected_flags = json.loads(challenge.multi_flags)
                    # Check if all parts are completed
                    all_parts_completed = True
                    for flag_key in expected_flags.keys():
                        existing_part = Submission.query.filter_by(
                            user_id=current_user_id,
                            challenge_id=challenge_id,
                            is_correct=True,
                            flag_type=flag_key
                        ).first()
                        if not existing_part:
                            all_parts_completed = False
                            break
                    
                    if all_parts_completed:
                        message = f'Challenge completed! All parts solved!'
                        points_earned = challenge.points
                    else:
                        message = f'Correct {flag_type}! Submit the remaining parts to complete the challenge.'
                        points_earned = 0
                except (json.JSONDecodeError, TypeError):
                    message = 'Correct flag!'
                    points_earned = challenge.points
            else:
                message = 'Correct flag!'
                points_earned = challenge.points
        else:
            message = 'Incorrect flag'
            points_earned = 0
        
        return jsonify({
            'correct': is_correct,
            'message': message,
            'points_earned': points_earned,
            'new_total_score': user.total_score
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Flag submission error: {str(e)}")
        return jsonify({'error': 'Submission failed'}), 500

@challenges_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all challenge categories"""
    try:
        categories = Category.query.order_by(Category.name.asc()).all()
        categories_data = [category.to_dict() for category in categories]
        
        return jsonify({'categories': categories_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get categories error: {str(e)}")
        return jsonify({'error': 'Failed to fetch categories'}), 500

@challenges_bp.route('/test-submit', methods=['POST'])
def test_submit():
    """Test submission endpoint without authentication"""
    try:
        data = request.get_json()
        if not data or 'flag' not in data:
            return jsonify({'error': 'Flag is required'}), 400
        
        submitted_flag = data['flag'].strip()
        
        # Test with Base64 challenge (ID 2)
        challenge = Challenge.query.filter_by(id=2, is_active=True).first()
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        is_correct = submitted_flag == challenge.flag
        
        return jsonify({
            'correct': is_correct,
            'message': 'Correct flag!' if is_correct else 'Incorrect flag',
            'submitted': submitted_flag,
            'expected': challenge.flag
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Test submission error: {str(e)}")
        return jsonify({'error': 'Test submission failed'}), 500

@challenges_bp.route('/stats', methods=['GET'])
def get_challenge_stats():
    """Get challenge statistics"""
    try:
        stats = {
            'total_challenges': Challenge.query.filter_by(is_active=True, is_hidden=False).count(),
            'total_categories': Category.query.count(),
            'total_submissions': Submission.query.count(),
            'total_correct_submissions': Submission.query.filter_by(is_correct=True).count(),
            'challenges_by_difficulty': {},
            'challenges_by_category': {}
        }
        
        # Count by difficulty
        for difficulty in ['Easy', 'Medium', 'Hard']:
            count = Challenge.query.filter_by(
                difficulty=difficulty, 
                is_active=True, 
                is_hidden=False
            ).count()
            stats['challenges_by_difficulty'][difficulty] = count
        
        # Count by category
        categories = Category.query.all()
        for category in categories:
            count = Challenge.query.filter_by(
                category_id=category.id, 
                is_active=True, 
                is_hidden=False
            ).count()
            stats['challenges_by_category'][category.name] = count
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get stats error: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@challenges_bp.route('/user-progress', methods=['GET'])
@jwt_required()
def get_user_progress():
    """Get current user's progress across all challenges"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get solved challenges
        solved_submissions = Submission.query.filter_by(
            user_id=current_user_id,
            is_correct=True
        ).all()
        
        solved_challenge_ids = [sub.challenge_id for sub in solved_submissions]
        
        # Get all challenges
        all_challenges = Challenge.query.filter_by(is_active=True, is_hidden=False).all()
        
        progress_data = {
            'total_challenges': len(all_challenges),
            'solved_challenges': len(solved_challenge_ids),
            'completion_percentage': round((len(solved_challenge_ids) / len(all_challenges)) * 100, 2) if all_challenges else 0,
            'total_score': user.total_score,
            'solved_challenge_ids': solved_challenge_ids,
            'progress_by_category': {},
            'progress_by_difficulty': {}
        }
        
        # Progress by category
        categories = Category.query.all()
        for category in categories:
            category_challenges = [c for c in all_challenges if c.category_id == category.id]
            solved_in_category = len([c for c in category_challenges if c.id in solved_challenge_ids])
            
            progress_data['progress_by_category'][category.name] = {
                'total': len(category_challenges),
                'solved': solved_in_category,
                'percentage': round((solved_in_category / len(category_challenges)) * 100, 2) if category_challenges else 0
            }
        
        # Progress by difficulty
        for difficulty in ['Easy', 'Medium', 'Hard']:
            difficulty_challenges = [c for c in all_challenges if c.difficulty == difficulty]
            solved_in_difficulty = len([c for c in difficulty_challenges if c.id in solved_challenge_ids])
            
            progress_data['progress_by_difficulty'][difficulty] = {
                'total': len(difficulty_challenges),
                'solved': solved_in_difficulty,
                'percentage': round((solved_in_difficulty / len(difficulty_challenges)) * 100, 2) if difficulty_challenges else 0
            }
        
        return jsonify({'progress': progress_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get user progress error: {str(e)}")
        return jsonify({'error': 'Failed to fetch progress'}), 500
