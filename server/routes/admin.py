"""
Admin routes for challenge and user management
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json

from models import User, Challenge, Category, Submission, db
from utils.validators import validate_flag_format, sanitize_input

admin_bp = Blueprint('admin', __name__)

def admin_required():
    """Decorator to check if user is admin"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    return None

@admin_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new challenge category"""
    admin_check = admin_required()
    if admin_check:
        return admin_check
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = sanitize_input(data.get('name', ''))
        description = sanitize_input(data.get('description', ''))
        icon = sanitize_input(data.get('icon', ''))
        color = sanitize_input(data.get('color', ''))
        
        if not name:
            return jsonify({'error': 'Category name is required'}), 400
        
        # Check if category already exists
        existing = Category.query.filter_by(name=name).first()
        if existing:
            return jsonify({'error': 'Category already exists'}), 409
        
        category = Category(
            name=name,
            description=description,
            icon=icon,
            color=color
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create category error: {str(e)}")
        return jsonify({'error': 'Failed to create category'}), 500

@admin_bp.route('/challenges', methods=['POST'])
@jwt_required()
def create_challenge():
    """Create a new challenge"""
    admin_check = admin_required()
    if admin_check:
        return admin_check
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'description', 'flag', 'category_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate flag format
        flag = sanitize_input(data['flag'])
        if not validate_flag_format(flag):
            return jsonify({'error': 'Invalid flag format'}), 400
        
        # Check if category exists
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        current_user_id = int(get_jwt_identity())
        
        challenge = Challenge(
            title=sanitize_input(data['title']),
            description=sanitize_input(data['description']),
            flag=flag,
            points=data.get('points', 100),
            difficulty=data.get('difficulty', 'Easy'),
            category_id=data['category_id'],
            author_id=current_user_id,
            hints=json.dumps(data.get('hints', [])),
            attachments=json.dumps(data.get('attachments', [])),
            challenge_type=data.get('challenge_type', 'static'),
            execution_script=data.get('execution_script', ''),
            environment_config=json.dumps(data.get('environment_config', {}))
        )
        
        db.session.add(challenge)
        db.session.commit()
        
        return jsonify({
            'message': 'Challenge created successfully',
            'challenge': challenge.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create challenge error: {str(e)}")
        return jsonify({'error': 'Failed to create challenge'}), 500

@admin_bp.route('/challenges/<int:challenge_id>', methods=['PUT'])
@jwt_required()
def update_challenge(challenge_id):
    """Update an existing challenge"""
    admin_check = admin_required()
    if admin_check:
        return admin_check
    
    try:
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'title' in data:
            challenge.title = sanitize_input(data['title'])
        if 'description' in data:
            challenge.description = sanitize_input(data['description'])
        if 'flag' in data:
            flag = sanitize_input(data['flag'])
            if not validate_flag_format(flag):
                return jsonify({'error': 'Invalid flag format'}), 400
            challenge.flag = flag
        if 'points' in data:
            challenge.points = data['points']
        if 'difficulty' in data:
            challenge.difficulty = data['difficulty']
        if 'category_id' in data:
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({'error': 'Category not found'}), 404
            challenge.category_id = data['category_id']
        if 'is_active' in data:
            challenge.is_active = bool(data['is_active'])
        if 'is_hidden' in data:
            challenge.is_hidden = bool(data['is_hidden'])
        if 'hints' in data:
            challenge.hints = json.dumps(data['hints'])
        if 'attachments' in data:
            challenge.attachments = json.dumps(data['attachments'])
        if 'challenge_type' in data:
            challenge.challenge_type = data['challenge_type']
        if 'execution_script' in data:
            challenge.execution_script = data['execution_script']
        if 'environment_config' in data:
            challenge.environment_config = json.dumps(data['environment_config'])
        
        challenge.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Challenge updated successfully',
            'challenge': challenge.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update challenge error: {str(e)}")
        return jsonify({'error': 'Failed to update challenge'}), 500


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (admin only)"""
    admin_check = admin_required()
    if admin_check:
        return admin_check
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '').strip()
        
        query = User.query
        
        if search:
            query = query.filter(
                User.username.contains(search) |
                User.email.contains(search)
            )
        
        users = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        users_data = [user.to_dict() for user in users.items]
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get users error: {str(e)}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    """Get admin statistics"""
    admin_check = admin_required()
    if admin_check:
        return admin_check
    
    try:
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'admin_users': User.query.filter_by(is_admin=True).count(),
            'total_challenges': Challenge.query.count(),
            'active_challenges': Challenge.query.filter_by(is_active=True).count(),
            'hidden_challenges': Challenge.query.filter_by(is_hidden=True).count(),
            'total_submissions': Submission.query.count(),
            'correct_submissions': Submission.query.filter_by(is_correct=True).count(),
            'categories': Category.query.count(),
            'recent_registrations': User.query.filter(
                User.created_at >= datetime.utcnow().replace(day=1)
            ).count()
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        current_app.logger.error(f"Admin stats error: {str(e)}")
        return jsonify({'error': 'Failed to fetch admin statistics'}), 500

@admin_bp.route('/challenges/<int:challenge_id>/reset', methods=['POST'])
@jwt_required()
def reset_challenge_submissions(challenge_id):
    """Reset all submissions for a specific challenge"""
    admin_check = admin_required()
    if admin_check:
        return admin_check
    
    try:
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        data = request.get_json() or {}
        user_id = data.get('user_id')  # Optional: reset for specific user
        
        if user_id:
            # Reset submissions for specific user
            submissions = Submission.query.filter_by(
                challenge_id=challenge_id,
                user_id=user_id
            ).all()
            
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
                
            # Recalculate user's total score
            for submission in submissions:
                if submission.is_correct:
                    user.total_score -= challenge.points
                    if user.total_score < 0:
                        user.total_score = 0
                db.session.delete(submission)
            
            db.session.commit()
            
            return jsonify({
                'message': f'Reset challenge submissions for user {user.username}',
                'deleted_submissions': len(submissions),
                'user_score': user.total_score
            }), 200
        else:
            # Reset all submissions for this challenge
            submissions = Submission.query.filter_by(challenge_id=challenge_id).all()
            
            # Recalculate scores for all affected users
            affected_users = {}
            for submission in submissions:
                user_id = submission.user_id
                if user_id not in affected_users:
                    affected_users[user_id] = 0
                
                if submission.is_correct:
                    affected_users[user_id] += challenge.points
                
                db.session.delete(submission)
            
            # Update user scores
            for user_id, points_to_subtract in affected_users.items():
                user = User.query.get(user_id)
                if user:
                    user.total_score -= points_to_subtract
                    if user.total_score < 0:
                        user.total_score = 0
            
            db.session.commit()
            
            return jsonify({
                'message': f'Reset all submissions for challenge: {challenge.title}',
                'deleted_submissions': len(submissions),
                'affected_users': len(affected_users)
            }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Reset challenge error: {str(e)}")
        return jsonify({'error': 'Failed to reset challenge submissions'}), 500

@admin_bp.route('/users/<int:user_id>/reset-score', methods=['POST'])
@jwt_required()
def reset_user_score(user_id):
    """Reset a user's score and clear all submissions"""
    admin_check = admin_required()
    if admin_check:
        return admin_check
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get all submissions for this user
        submissions = Submission.query.filter_by(user_id=user_id).all()
        
        # Delete all submissions
        for submission in submissions:
            db.session.delete(submission)
        
        # Reset user score
        user.total_score = 0
        
        db.session.commit()
        
        return jsonify({
            'message': f'Reset score and submissions for user {user.username}',
            'deleted_submissions': len(submissions),
            'new_score': user.total_score
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Reset user score error: {str(e)}")
        return jsonify({'error': 'Failed to reset user score'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user and all their data"""
    admin_check = admin_required()
    if admin_check:
        return admin_check
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deleting the last admin user
        if user.is_admin:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                return jsonify({'error': 'Cannot delete the last admin user'}), 400
        
        # Get user's submissions for logging
        submission_count = Submission.query.filter_by(user_id=user_id).count()
        
        # Delete user (this will cascade delete submissions due to the relationship)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': f'User {user.username} deleted successfully',
            'deleted_submissions': submission_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete user error: {str(e)}")
        return jsonify({'error': 'Failed to delete user'}), 500

@admin_bp.route('/challenges/<int:challenge_id>/toggle-visibility', methods=['PUT'])
@jwt_required()
def toggle_challenge_visibility(challenge_id):
    """Toggle challenge visibility (hide/show)"""
    admin_check = admin_required()
    if admin_check:
        return admin_check
    
    try:
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        # Toggle visibility
        challenge.is_active = not challenge.is_active
        db.session.commit()
        
        status = "shown" if challenge.is_active else "hidden"
        
        return jsonify({
            'message': f'Challenge "{challenge.title}" {status} successfully',
            'is_active': challenge.is_active
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Toggle challenge visibility error: {str(e)}")
        return jsonify({'error': 'Failed to toggle challenge visibility'}), 500

@admin_bp.route('/challenges/<int:challenge_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_challenge_admin(challenge_id):
    """Delete a challenge and all its submissions"""
    admin_check = admin_required()
    if admin_check:
        return admin_check
    
    try:
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        # Get submission count for logging
        submission_count = Submission.query.filter_by(challenge_id=challenge_id).count()
        challenge_title = challenge.title
        
        # Delete challenge (this will cascade delete submissions due to the relationship)
        db.session.delete(challenge)
        db.session.commit()
        
        return jsonify({
            'message': f'Challenge "{challenge_title}" deleted successfully',
            'deleted_submissions': submission_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete challenge error: {str(e)}")
        return jsonify({'error': 'Failed to delete challenge'}), 500
