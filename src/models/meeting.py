"""
Meeting Model - Tracks SAFMC meetings and events
"""

from datetime import datetime
from src.config.extensions import db

class Meeting(db.Model):
    """Represents a SAFMC meeting or event"""

    __tablename__ = 'meetings'

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(100))  # Council Meeting, Committee Meeting, Public Hearing, etc.

    # Date and time
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    time = db.Column(db.String(100))

    # Location
    location = db.Column(db.String(500))
    virtual_link = db.Column(db.String(500))

    # Details
    description = db.Column(db.Text)
    agenda_url = db.Column(db.String(500))
    source_url = db.Column(db.String(500))

    # Status
    status = db.Column(db.String(100))  # Scheduled, Completed, Cancelled

    # Related actions (stored as comma-separated action IDs)
    related_actions = db.Column(db.Text)

    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = db.Column(db.DateTime)

    def to_dict(self):
        """Convert meeting to dictionary for JSON serialization"""
        return {
            'id': self.meeting_id,
            'title': self.title,
            'type': self.type,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'time': self.time,
            'location': self.location,
            'virtualLink': self.virtual_link,
            'description': self.description,
            'agendaUrl': self.agenda_url,
            'sourceUrl': self.source_url,
            'status': self.status,
            'relatedActions': self.related_actions.split(',') if self.related_actions else [],
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Meeting {self.meeting_id}: {self.title}>'
