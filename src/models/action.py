"""
Action Model - Tracks amendments, frameworks, and regulatory actions
"""

from datetime import datetime
from src.config.extensions import db

class Action(db.Model):
    """Represents a fishery management action (amendment, framework, etc.)"""

    __tablename__ = 'actions'

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(100))  # Amendment, Framework, Regulatory Amendment, etc.
    fmp = db.Column(db.String(200))  # Fishery Management Plan
    status = db.Column(db.String(100))
    progress_stage = db.Column(db.String(100))  # Pre-Scoping, Scoping, Public Hearing, etc.
    progress_percentage = db.Column(db.Integer, default=0)
    phase = db.Column(db.String(100))  # Development, Review, Federal Review, Implementation

    # Dates
    start_date = db.Column(db.Date)
    target_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)

    # Details
    description = db.Column(db.Text)
    lead_staff = db.Column(db.String(200))
    committee = db.Column(db.String(200))

    # Source information
    source_url = db.Column(db.String(500))
    documents_found = db.Column(db.Integer, default=0)

    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = db.Column(db.DateTime)

    # Relationships
    milestones = db.relationship('Milestone', backref='action', lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='action', lazy='dynamic',
                              cascade='all, delete-orphan')

    def to_dict(self):
        """Convert action to dictionary for JSON serialization"""
        return {
            'id': self.action_id,
            'title': self.title,
            'type': self.type,
            'fmp': self.fmp,
            'status': self.status,
            'progress_stage': self.progress_stage,
            'progress': self.progress_percentage,
            'phase': self.phase,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'description': self.description,
            'lead_staff': self.lead_staff,
            'committee': self.committee,
            'source_url': self.source_url,
            'documents_found': self.documents_found,
            'last_scraped': self.last_scraped.isoformat() if self.last_scraped else None,
            'last_updated': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Action {self.action_id}: {self.title}>'
