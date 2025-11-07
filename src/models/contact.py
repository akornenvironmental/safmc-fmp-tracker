"""
Contact Model - Tracks individuals who submit comments or participate in processes
"""

from datetime import datetime
from src.config.extensions import db

class Contact(db.Model):
    """Represents an individual who engages with SAFMC processes"""

    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.String(100), unique=True, nullable=False, index=True)

    # Personal information
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    full_name = db.Column(db.String(400), index=True)
    email = db.Column(db.String(200), index=True)
    phone = db.Column(db.String(50))

    # Location
    city = db.Column(db.String(200))
    state = db.Column(db.String(50), index=True)
    zip_code = db.Column(db.String(20))
    address = db.Column(db.Text)

    # Professional information
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
    title = db.Column(db.String(200))
    sector = db.Column(db.String(100))  # Commercial, For-Hire, Recreational, NGO, Government, etc.

    # Engagement tracking
    total_comments = db.Column(db.Integer, default=0)
    total_meetings_attended = db.Column(db.Integer, default=0)
    first_engagement_date = db.Column(db.DateTime)
    last_engagement_date = db.Column(db.DateTime)

    # Data quality
    data_source = db.Column(db.String(300))
    verified = db.Column(db.Boolean, default=False)

    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = db.relationship('Organization', backref='contacts')

    def to_dict(self):
        """Convert contact to dictionary for JSON serialization"""
        return {
            'id': self.contact_id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'fullName': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'city': self.city,
            'state': self.state,
            'zipCode': self.zip_code,
            'organizationId': self.organization_id,
            'title': self.title,
            'sector': self.sector,
            'totalComments': self.total_comments,
            'totalMeetingsAttended': self.total_meetings_attended,
            'firstEngagementDate': self.first_engagement_date.isoformat() if self.first_engagement_date else None,
            'lastEngagementDate': self.last_engagement_date.isoformat() if self.last_engagement_date else None,
            'verified': self.verified,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Contact {self.contact_id}: {self.full_name}>'
