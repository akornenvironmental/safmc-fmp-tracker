"""
Stock Assessment Models
"""
from src.database import db
from datetime import datetime

class StockAssessment(db.Model):
    """Stock Assessment model for SEDAR data"""
    __tablename__ = 'stock_assessments'

    id = db.Column(db.Integer, primary_key=True)
    sedar_number = db.Column(db.String(50), unique=True, nullable=False)
    species_common_name = db.Column(db.String(200), nullable=False)
    species_scientific_name = db.Column(db.String(200))
    stock_region = db.Column(db.String(100))  # South Atlantic, Gulf, Caribbean, etc.
    assessment_type = db.Column(db.String(100))  # Benchmark, Standard, Update, Research Track
    status = db.Column(db.String(100))  # Planning, In Progress, Review, Completed
    start_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    review_workshop_date = db.Column(db.Date)
    council_review_date = db.Column(db.Date)
    sedar_url = db.Column(db.String(500))
    assessment_report_url = db.Column(db.String(500))
    executive_summary_url = db.Column(db.String(500))
    stock_status = db.Column(db.String(100))  # Overfished, Not Overfished, etc.
    overfishing_limit = db.Column(db.Numeric)
    acceptable_biological_catch = db.Column(db.Numeric)
    annual_catch_limit = db.Column(db.Numeric)
    optimum_yield = db.Column(db.Numeric)
    units = db.Column(db.String(50))  # pounds, numbers, etc.
    fmp = db.Column(db.String(100))
    lead_scientist = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    comments = db.relationship('AssessmentComment', backref='assessment', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_comments=False):
        result = {
            'id': self.id,
            'sedar_number': self.sedar_number,
            'species_common_name': self.species_common_name,
            'species_scientific_name': self.species_scientific_name,
            'stock_region': self.stock_region,
            'assessment_type': self.assessment_type,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'review_workshop_date': self.review_workshop_date.isoformat() if self.review_workshop_date else None,
            'council_review_date': self.council_review_date.isoformat() if self.council_review_date else None,
            'sedar_url': self.sedar_url,
            'assessment_report_url': self.assessment_report_url,
            'executive_summary_url': self.executive_summary_url,
            'stock_status': self.stock_status,
            'overfishing_limit': float(self.overfishing_limit) if self.overfishing_limit else None,
            'acceptable_biological_catch': float(self.acceptable_biological_catch) if self.acceptable_biological_catch else None,
            'annual_catch_limit': float(self.annual_catch_limit) if self.annual_catch_limit else None,
            'optimum_yield': float(self.optimum_yield) if self.optimum_yield else None,
            'units': self.units,
            'fmp': self.fmp,
            'lead_scientist': self.lead_scientist,
            'notes': self.notes
        }

        if include_comments:
            result['comments'] = [comment.to_dict() for comment in self.comments]
            result['comment_count'] = len(self.comments)

        return result


class AssessmentComment(db.Model):
    """Comments on stock assessments"""
    __tablename__ = 'assessment_comments'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('stock_assessments.id'), nullable=False)
    commenter_name = db.Column(db.String(200))
    commenter_organization = db.Column(db.String(255))
    comment_text = db.Column(db.Text, nullable=False)
    comment_date = db.Column(db.Date)
    comment_type = db.Column(db.String(50))  # Public, Peer Review, SSC, Council
    source_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'commenter_name': self.commenter_name,
            'commenter_organization': self.commenter_organization,
            'comment_text': self.comment_text,
            'comment_date': self.comment_date.isoformat() if self.comment_date else None,
            'comment_type': self.comment_type,
            'source_url': self.source_url
        }
