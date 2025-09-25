"""
Database models for the CTF Platform
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    total_score = db.Column(db.Integer, default=0)
    
    # Relationships
    submissions = db.relationship('Submission', back_populates='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'total_score': self.total_score
        }
        return data

class Category(db.Model):
    """Challenge categories (Crypto, Web, Forensics, etc.)"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))  # Icon class or URL
    color = db.Column(db.String(7))   # Hex color code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    challenges = db.relationship('Challenge', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'challenge_count': len(self.challenges)
        }

class Challenge(db.Model):
    """CTF Challenge model"""
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    flag = db.Column(db.String(500), nullable=False)
    multi_flags = db.Column(db.Text)  # JSON string for multi-part flags
    points = db.Column(db.Integer, default=100)
    difficulty = db.Column(db.String(20), default='Easy')  # Easy, Medium, Hard
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_hidden = db.Column(db.Boolean, default=False)
    hints = db.Column(db.Text)  # JSON string of hints
    attachments = db.Column(db.Text)  # JSON string of file URLs
    challenge_data = db.Column(db.Text)  # Additional challenge data (headers, files, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Challenge execution details
    challenge_type = db.Column(db.String(50), default='static')  # static, dynamic, interactive
    execution_script = db.Column(db.Text)  # Python script for dynamic challenges
    environment_config = db.Column(db.Text)  # JSON config for challenge environment
    
    # Relationships
    submissions = db.relationship('Submission', back_populates='challenge', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_flag=False):
        """Convert challenge to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'points': self.points,
            'difficulty': self.difficulty,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'author_id': self.author_id,
            'is_active': self.is_active,
            'is_hidden': self.is_hidden,
            'hints': self.hints,
            'attachments': self.attachments,
            'challenge_data': self.challenge_data,
            'multi_flags': self.multi_flags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'challenge_type': self.challenge_type,
            'submission_count': len(self.submissions)
        }
        
        if include_flag:
            data['flag'] = self.flag
            
        return data

class Submission(db.Model):
    """User submissions for challenges"""
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    submitted_flag = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    flag_type = db.Column(db.String(50))  # Track which flag type was submitted
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # Support IPv6
    
    # Relationships
    user = db.relationship('User', back_populates='submissions', lazy=True)
    challenge = db.relationship('Challenge', back_populates='submissions', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'challenge_id': self.challenge_id,
            'challenge_title': self.challenge.title if self.challenge else None,
            'submitted_flag': self.submitted_flag,
            'is_correct': self.is_correct,
            'flag_type': self.flag_type,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'ip_address': self.ip_address
        }

class Hint(db.Model):
    """Challenge hints that can be unlocked"""
    __tablename__ = 'hints'
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    hint_text = db.Column(db.Text, nullable=False)
    hint_order = db.Column(db.Integer, default=1)
    points_cost = db.Column(db.Integer, default=10)  # Points deducted for using hint
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'challenge_id': self.challenge_id,
            'hint_text': self.hint_text,
            'hint_order': self.hint_order,
            'points_cost': self.points_cost,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Initialize database if not already done
def init_db(app):
    """Initialize database with app context"""
    with app.app_context():
        db.create_all()
