"""
User routes for profile management and leaderboard
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import func, desc

from models import User, Submission, Challenge, db

users_bp = Blueprint('users', __name__)

@users_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get user leaderboard"""
    try:
        # Query parameters
        limit = request.args.get('limit', 50, type=int)
        category_id = request.args.get('category_id', type=int)
        
        # Base query for users with scores
        query = db.session.query(
            User.id,
            User.username,
            User.total_score,
            User.created_at,
            func.count(Submission.id).label('solved_count')
        ).join(Submission, User.id == Submission.user_id, isouter=True).filter(
            Submission.is_correct == True
        ).group_by(User.id).order_by(desc(User.total_score), desc('solved_count'))
        
        # If category filter is applied
        if category_id:
            query = query.join(Challenge, Submission.challenge_id == Challenge.id).filter(
                Challenge.category_id == category_id
            )
        
        # Execute query
        leaderboard_data = query.limit(limit).all()
        
        # Format response
        leaderboard = []
        for rank, (user_id, username, total_score, created_at, solved_count) in enumerate(leaderboard_data, 1):
            leaderboard.append({
                'rank': rank,
                'user_id': user_id,
                'username': username,
                'total_score': total_score or 0,
                'solved_count': solved_count or 0,
                'joined_at': created_at.isoformat() if created_at else None
            })
        
        return jsonify({
            'leaderboard': leaderboard,
            'total_users': len(leaderboard)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Leaderboard error: {str(e)}")
        return jsonify({'error': 'Failed to fetch leaderboard'}), 500

@users_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """Get platform statistics"""
    try:
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_challenges': Challenge.query.filter_by(is_active=True, is_hidden=False).count(),
            'total_submissions': Submission.query.count(),
            'total_solves': Submission.query.filter_by(is_correct=True).count(),
            'recent_registrations': User.query.filter(
                User.created_at >= datetime.utcnow().replace(day=1)
            ).count()
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        current_app.logger.error(f"User stats error: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@users_bp.route('/my-stats', methods=['GET'])
@jwt_required()
def get_my_stats():
    """Get current user's statistics"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's solved challenges
        solved_submissions = Submission.query.filter_by(
            user_id=current_user_id,
            is_correct=True
        ).all()
        
        # Calculate stats
        total_solves = len(solved_submissions)
        total_points = user.total_score
        recent_solves = Submission.query.filter_by(
            user_id=current_user_id,
            is_correct=True
        ).filter(
            Submission.submitted_at >= datetime.utcnow().replace(day=1)
        ).count()
        
        stats = {
            'total_solves': total_solves,
            'total_points': total_points,
            'recent_solves': recent_solves,
            'rank': get_user_rank(current_user_id)
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        current_app.logger.error(f"My stats error: {str(e)}")
        return jsonify({'error': 'Failed to fetch user statistics'}), 500

def get_user_rank(user_id):
    """Get user's rank based on total score"""
    try:
        user_scores = db.session.query(User.id, User.total_score).order_by(
            desc(User.total_score)
        ).all()
        
        for rank, (uid, score) in enumerate(user_scores, 1):
            if uid == user_id:
                return rank
        
        return len(user_scores) + 1
    except:
        return None

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get public user profile"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's solved challenges
        solved_submissions = Submission.query.filter_by(
            user_id=user_id,
            is_correct=True
        ).order_by(Submission.submitted_at.desc()).all()
        
        solved_challenges = []
        for submission in solved_submissions:
            challenge_data = submission.challenge.to_dict()
            challenge_data['solved_at'] = submission.submitted_at.isoformat()
            solved_challenges.append(challenge_data)
        
        # Get recent activity
        recent_submissions = Submission.query.filter_by(user_id=user_id).order_by(
            Submission.submitted_at.desc()
        ).limit(10).all()
        
        recent_activity = [sub.to_dict() for sub in recent_submissions]
        
        profile_data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'total_score': user.total_score,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'solved_count': len(solved_challenges)
            },
            'solved_challenges': solved_challenges,
            'recent_activity': recent_activity
        }
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Get user profile error: {str(e)}")
        return jsonify({'error': 'Failed to fetch user profile'}), 500
