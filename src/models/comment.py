"""
Comment Model - Tracks public comments on fishery management actions
"""

from datetime import datetime
from src.config.extensions import db

class Comment(db.Model):
    """Represents a public comment on a fishery management action"""

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.String(100), unique=True, nullable=False, index=True)

    # Commenter information (kept for backward compatibility)
    name = db.Column(db.String(200))
    organization = db.Column(db.String(300))
    email = db.Column(db.String(200))
    city = db.Column(db.String(200))
    state = db.Column(db.String(50))

    # Linked entities
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)

    # Comment details
    action_id = db.Column(db.String(100), db.ForeignKey('actions.action_id'), nullable=True)
    comment_date = db.Column(db.DateTime)
    comment_type = db.Column(db.String(100))  # Written, Oral, Email, Portal, etc.
    commenter_type = db.Column(db.String(100))  # For-Hire, Commercial, NGO, Government, etc.
    position = db.Column(db.String(100))  # Support, Oppose, Concern, Neutral
    key_topics = db.Column(db.Text)  # Comma-separated topics
    comment_text = db.Column(db.Text)
    amendment_phase = db.Column(db.String(100))  # Phase when comment was made

    # Response
    response_status = db.Column(db.String(100))  # Pending, Responded, Acknowledged
    response_text = db.Column(db.Text)
    response_date = db.Column(db.DateTime)

    # Source
    source = db.Column(db.String(200))
    source_url = db.Column(db.String(500))
    data_source = db.Column(db.String(300))  # Name of the comment collection

    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert comment to dictionary for JSON serialization"""
        return {
            'id': self.comment_id,
            'name': self.name,
            'organization': self.organization,
            'email': self.email,
            'city': self.city,
            'state': self.state,
            'contactId': self.contact_id,
            'organizationId': self.organization_id,
            'actionId': self.action_id,
            'commentDate': self.comment_date.isoformat() if self.comment_date else None,
            'commentType': self.comment_type,
            'commenterType': self.commenter_type,
            'position': self.position,
            'keyTopics': self.key_topics.split(',') if self.key_topics else [],
            'commentText': self.comment_text,
            'amendmentPhase': self.amendment_phase,
            'responseStatus': self.response_status,
            'responseText': self.response_text,
            'responseDate': self.response_date.isoformat() if self.response_date else None,
            'source': self.source,
            'sourceUrl': self.source_url,
            'dataSource': self.data_source,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Comment {self.comment_id} on {self.action_id}>'
