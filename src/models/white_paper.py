"""
White Paper and Scoping Models
"""
from datetime import datetime
from src.config.extensions import db

class WhitePaper(db.Model):
    """White paper model"""
    __tablename__ = 'white_papers'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    fmp = db.Column(db.String(100))
    topic = db.Column(db.String(255))
    description = db.Column(db.Text)
    requested_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    status = db.Column(db.String(50))  # Requested, In Progress, Completed, No Action Taken
    staff_lead = db.Column(db.String(200))
    council_action = db.Column(db.String(100))  # Amendment Initiated, No Action, Deferred
    document_url = db.Column(db.String(500))
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'))
    source_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'fmp': self.fmp,
            'topic': self.topic,
            'description': self.description,
            'requested_date': self.requested_date.isoformat() if self.requested_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'status': self.status,
            'staff_lead': self.staff_lead,
            'council_action': self.council_action,
            'document_url': self.document_url,
            'meeting_id': self.meeting_id,
            'source_url': self.source_url
        }


class ScopingItem(db.Model):
    """Scoping item model"""
    __tablename__ = 'scoping_items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    fmp = db.Column(db.String(100))
    scoping_type = db.Column(db.String(100))  # General, Amendment, Framework
    description = db.Column(db.Text)
    action_id = db.Column(db.String(100))  # NULL if no action taken
    comment_period_start = db.Column(db.Date)
    comment_period_end = db.Column(db.Date)
    status = db.Column(db.String(50))  # Open, Closed, Action Initiated, No Action
    source_url = db.Column(db.String(500))
    document_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'fmp': self.fmp,
            'scoping_type': self.scoping_type,
            'description': self.description,
            'action_id': self.action_id,
            'comment_period_start': self.comment_period_start.isoformat() if self.comment_period_start else None,
            'comment_period_end': self.comment_period_end.isoformat() if self.comment_period_end else None,
            'status': self.status,
            'source_url': self.source_url,
            'document_url': self.document_url
        }
