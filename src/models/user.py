"""User Model for Authentication"""
from src.config.extensions import db
from datetime import datetime
import uuid

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=True)
    organization = db.Column(db.String(255), nullable=True)  # User's organization/affiliation
    role = db.Column(db.Enum('admin', 'editor', 'super_admin', name='user_roles'), nullable=False, default='editor')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    login_token = db.Column(db.String(255), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)

    # Refresh token for persistent sessions
    refresh_token = db.Column(db.String(255), nullable=True, index=True)
    refresh_token_expiry = db.Column(db.DateTime, nullable=True)

    # Notification preferences
    email_notifications = db.Column(db.Boolean, default=True, nullable=False)
    notify_new_comments = db.Column(db.Boolean, default=True, nullable=False)
    notify_weekly_digest = db.Column(db.Boolean, default=True, nullable=False)

    # Invitation tracking
    invitation_status = db.Column(db.Enum('pending', 'accepted', name='invitation_status'), nullable=True, default='pending')
    invitation_accepted_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'organization': self.organization,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'email_notifications': self.email_notifications,
            'notify_new_comments': self.notify_new_comments,
            'notify_weekly_digest': self.notify_weekly_digest,
            'invitation_status': self.invitation_status,
            'invitation_accepted_at': self.invitation_accepted_at.isoformat() if self.invitation_accepted_at else None
        }

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
