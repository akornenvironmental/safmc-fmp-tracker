"""
ScrapeLog Model - Tracks web scraping activity and results
"""

from datetime import datetime
from src.config.extensions import db

class ScrapeLog(db.Model):
    """Represents a scraping operation log entry"""

    __tablename__ = 'scrape_logs'

    id = db.Column(db.Integer, primary_key=True)

    # Scrape details
    source = db.Column(db.String(200), nullable=False)  # amendments, meetings, documents, etc.
    action_type = db.Column(db.String(100))  # scrape_amendments, scrape_meetings, etc.
    status = db.Column(db.String(50))  # success, error, partial

    # Results
    items_found = db.Column(db.Integer, default=0)
    items_updated = db.Column(db.Integer, default=0)
    items_new = db.Column(db.Integer, default=0)

    # Error information
    error_message = db.Column(db.Text)

    # Performance
    duration_ms = db.Column(db.Integer)  # Duration in milliseconds

    # Timing
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        """Convert scrape log to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'source': self.source,
            'actionType': self.action_type,
            'status': self.status,
            'itemsFound': self.items_found,
            'itemsUpdated': self.items_updated,
            'itemsNew': self.items_new,
            'errorMessage': self.error_message,
            'durationMs': self.duration_ms,
            'startedAt': self.started_at.isoformat() if self.started_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None
        }

    def __repr__(self):
        return f'<ScrapeLog {self.id}: {self.source} - {self.status}>'
