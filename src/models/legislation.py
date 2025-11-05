"""
Legislation and Regulation Models
"""
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from src.config.extensions import db

class Legislation(db.Model):
    """Legislation model"""
    __tablename__ = 'legislation'

    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(50), nullable=False)
    congress_session = db.Column(db.String(20))
    jurisdiction = db.Column(db.String(50))  # Federal, NC, SC, GA, FL
    chamber = db.Column(db.String(50))  # House, Senate, Both
    title = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    sponsor = db.Column(db.String(200))
    introduced_date = db.Column(db.Date)
    status = db.Column(db.String(100))  # Introduced, Committee, Passed House, etc.
    last_action = db.Column(db.Text)
    last_action_date = db.Column(db.Date)
    bill_url = db.Column(db.String(500))
    full_text_url = db.Column(db.String(500))
    relevance_score = db.Column(db.Integer)  # 1-10 based on keyword match
    keywords = db.Column(ARRAY(db.Text))
    fmps_affected = db.Column(ARRAY(db.Text))
    requires_council_action = db.Column(db.Boolean, default=False)
    council_commented = db.Column(db.Boolean, default=False)
    council_comment_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('bill_number', 'jurisdiction', 'congress_session', name='uq_legislation'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'bill_number': self.bill_number,
            'congress_session': self.congress_session,
            'jurisdiction': self.jurisdiction,
            'chamber': self.chamber,
            'title': self.title,
            'summary': self.summary,
            'sponsor': self.sponsor,
            'introduced_date': self.introduced_date.isoformat() if self.introduced_date else None,
            'status': self.status,
            'last_action': self.last_action,
            'last_action_date': self.last_action_date.isoformat() if self.last_action_date else None,
            'bill_url': self.bill_url,
            'full_text_url': self.full_text_url,
            'relevance_score': self.relevance_score,
            'keywords': self.keywords or [],
            'fmps_affected': self.fmps_affected or [],
            'requires_council_action': self.requires_council_action,
            'council_commented': self.council_commented,
            'council_comment_url': self.council_comment_url
        }


class Regulation(db.Model):
    """Regulation model"""
    __tablename__ = 'regulations'

    id = db.Column(db.Integer, primary_key=True)
    regulation_number = db.Column(db.String(100), nullable=False)
    jurisdiction = db.Column(db.String(50))  # Federal, NC, SC, GA, FL
    agency = db.Column(db.String(200))
    title = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    cfr_citation = db.Column(db.String(100))  # e.g., '50 CFR 622.183'
    effective_date = db.Column(db.Date)
    comment_period_start = db.Column(db.Date)
    comment_period_end = db.Column(db.Date)
    status = db.Column(db.String(100))  # Proposed, Final, Effective, Withdrawn
    federal_register_citation = db.Column(db.String(100))
    federal_register_url = db.Column(db.String(500))
    full_text_url = db.Column(db.String(500))
    relevance_score = db.Column(db.Integer)
    keywords = db.Column(ARRAY(db.Text))
    fmps_affected = db.Column(ARRAY(db.Text))
    requires_council_action = db.Column(db.Boolean, default=False)
    council_commented = db.Column(db.Boolean, default=False)
    council_comment_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('regulation_number', 'jurisdiction', name='uq_regulation'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'regulation_number': self.regulation_number,
            'jurisdiction': self.jurisdiction,
            'agency': self.agency,
            'title': self.title,
            'summary': self.summary,
            'cfr_citation': self.cfr_citation,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'comment_period_start': self.comment_period_start.isoformat() if self.comment_period_start else None,
            'comment_period_end': self.comment_period_end.isoformat() if self.comment_period_end else None,
            'status': self.status,
            'federal_register_citation': self.federal_register_citation,
            'federal_register_url': self.federal_register_url,
            'full_text_url': self.full_text_url,
            'relevance_score': self.relevance_score,
            'keywords': self.keywords or [],
            'fmps_affected': self.fmps_affected or [],
            'requires_council_action': self.requires_council_action,
            'council_commented': self.council_commented,
            'council_comment_url': self.council_comment_url
        }
