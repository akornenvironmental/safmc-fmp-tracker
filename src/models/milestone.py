"""
Milestone Model - Tracks milestones for fishery management actions
"""

from datetime import datetime
from src.config.extensions import db

class Milestone(db.Model):
    """Represents a milestone in a fishery management action"""

    __tablename__ = 'milestones'

    id = db.Column(db.Integer, primary_key=True)
    milestone_id = db.Column(db.String(100), unique=True, nullable=False, index=True)

    # Associated action
    action_id = db.Column(db.String(100), db.ForeignKey('actions.action_id'), nullable=False)

    # Milestone details
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)

    # Status
    status = db.Column(db.String(100))  # Pending, In Progress, Completed, Delayed

    # Dependencies (comma-separated milestone IDs)
    dependencies = db.Column(db.Text)

    # Notes
    notes = db.Column(db.Text)

    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert milestone to dictionary for JSON serialization"""
        return {
            'id': self.milestone_id,
            'actionId': self.action_id,
            'title': self.title,
            'description': self.description,
            'targetDate': self.target_date.isoformat() if self.target_date else None,
            'completionDate': self.completion_date.isoformat() if self.completion_date else None,
            'status': self.status,
            'dependencies': self.dependencies.split(',') if self.dependencies else [],
            'notes': self.notes,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Milestone {self.milestone_id}: {self.title}>'
