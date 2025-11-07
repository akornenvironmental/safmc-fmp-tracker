"""
Organization Model - Tracks organizations engaged in fishery management
"""

from datetime import datetime
from src.config.extensions import db

class Organization(db.Model):
    """Represents an organization involved in SAFMC processes"""

    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.String(100), unique=True, nullable=False, index=True)

    # Organization information
    name = db.Column(db.String(500), nullable=False, index=True)
    name_normalized = db.Column(db.String(500), index=True)  # For fuzzy matching
    acronym = db.Column(db.String(50))
    org_type = db.Column(db.String(100))  # NGO, Commercial, For-Hire, Government, Academic, etc.

    # Contact information
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    website = db.Column(db.String(500))

    # Location
    city = db.Column(db.String(200))
    state = db.Column(db.String(50), index=True)
    zip_code = db.Column(db.String(20))
    address = db.Column(db.Text)

    # Details
    description = db.Column(db.Text)
    sectors = db.Column(db.JSON)  # Array of sectors they represent

    # Engagement tracking
    total_comments = db.Column(db.Integer, default=0)
    total_members_active = db.Column(db.Integer, default=0)
    first_engagement_date = db.Column(db.DateTime)
    last_engagement_date = db.Column(db.DateTime)

    # Data quality
    data_source = db.Column(db.String(300))
    verified = db.Column(db.Boolean, default=False)

    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert organization to dictionary for JSON serialization"""
        return {
            'id': self.org_id,
            'name': self.name,
            'acronym': self.acronym,
            'orgType': self.org_type,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'city': self.city,
            'state': self.state,
            'zipCode': self.zip_code,
            'description': self.description,
            'sectors': self.sectors,
            'totalComments': self.total_comments,
            'totalMembersActive': self.total_members_active,
            'firstEngagementDate': self.first_engagement_date.isoformat() if self.first_engagement_date else None,
            'lastEngagementDate': self.last_engagement_date.isoformat() if self.last_engagement_date else None,
            'verified': self.verified,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Organization {self.org_id}: {self.name}>'
