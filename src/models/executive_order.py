"""
Executive Order Model
"""
from src.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY

class ExecutiveOrder(db.Model):
    """Executive Order model"""
    __tablename__ = 'executive_orders'

    id = db.Column(db.Integer, primary_key=True)
    eo_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    issuing_authority = db.Column(db.String(100))  # President, Secretary of Commerce, etc.
    issue_date = db.Column(db.Date, nullable=False)
    summary = db.Column(db.Text)
    full_text_url = db.Column(db.String(500))
    federal_register_url = db.Column(db.String(500))
    impacts_council = db.Column(db.Boolean, default=True)
    fmps_affected = db.Column(ARRAY(db.Text))
    council_response_required = db.Column(db.Boolean, default=False)
    response_deadline = db.Column(db.Date)
    status = db.Column(db.String(50))  # Received, Under Review, Response Submitted, Completed
    council_response_text = db.Column(db.Text)
    council_response_date = db.Column(db.Date)
    council_response_url = db.Column(db.String(500))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'eo_number': self.eo_number,
            'title': self.title,
            'issuing_authority': self.issuing_authority,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'summary': self.summary,
            'full_text_url': self.full_text_url,
            'federal_register_url': self.federal_register_url,
            'impacts_council': self.impacts_council,
            'fmps_affected': self.fmps_affected or [],
            'council_response_required': self.council_response_required,
            'response_deadline': self.response_deadline.isoformat() if self.response_deadline else None,
            'status': self.status,
            'council_response_text': self.council_response_text,
            'council_response_date': self.council_response_date.isoformat() if self.council_response_date else None,
            'council_response_url': self.council_response_url,
            'notes': self.notes
        }
