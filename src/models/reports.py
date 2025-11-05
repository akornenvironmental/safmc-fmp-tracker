"""
AP and SSC Report Models
"""
from datetime import datetime
from src.config.extensions import db

class APReport(db.Model):
    """Advisory Panel Report model"""
    __tablename__ = 'ap_reports'

    id = db.Column(db.Integer, primary_key=True)
    report_title = db.Column(db.String(500), nullable=False)
    advisory_panel = db.Column(db.String(200), nullable=False)  # Snapper Grouper AP, Shrimp AP, etc.
    fmp = db.Column(db.String(100))
    meeting_date = db.Column(db.Date)
    report_date = db.Column(db.Date)
    summary = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    document_url = db.Column(db.String(500), nullable=False)
    meeting_location = db.Column(db.String(255))
    related_action_id = db.Column(db.String(100))
    related_meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'))
    council_action_taken = db.Column(db.Text)
    fishery_performance_report = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'report_title': self.report_title,
            'advisory_panel': self.advisory_panel,
            'fmp': self.fmp,
            'meeting_date': self.meeting_date.isoformat() if self.meeting_date else None,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'summary': self.summary,
            'recommendations': self.recommendations,
            'document_url': self.document_url,
            'meeting_location': self.meeting_location,
            'related_action_id': self.related_action_id,
            'related_meeting_id': self.related_meeting_id,
            'council_action_taken': self.council_action_taken,
            'fishery_performance_report': self.fishery_performance_report
        }


class SSCReport(db.Model):
    """Scientific and Statistical Committee Report model"""
    __tablename__ = 'ssc_reports'

    id = db.Column(db.Integer, primary_key=True)
    report_title = db.Column(db.String(500), nullable=False)
    meeting_date = db.Column(db.Date)
    report_date = db.Column(db.Date)
    summary = db.Column(db.Text)
    abc_recommendation = db.Column(db.Numeric)
    abc_units = db.Column(db.String(50))
    abc_rationale = db.Column(db.Text)
    overfishing_limit = db.Column(db.Numeric)
    acceptable_catch_range_min = db.Column(db.Numeric)
    acceptable_catch_range_max = db.Column(db.Numeric)
    uncertainty_assessment = db.Column(db.Text)
    species = db.Column(db.String(200))
    stock_name = db.Column(db.String(255))
    fmp = db.Column(db.String(100))
    document_url = db.Column(db.String(500), nullable=False)
    related_assessment_id = db.Column(db.Integer, db.ForeignKey('stock_assessments.id'))
    related_action_id = db.Column(db.String(100))
    council_action_taken = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'report_title': self.report_title,
            'meeting_date': self.meeting_date.isoformat() if self.meeting_date else None,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'summary': self.summary,
            'abc_recommendation': float(self.abc_recommendation) if self.abc_recommendation else None,
            'abc_units': self.abc_units,
            'abc_rationale': self.abc_rationale,
            'overfishing_limit': float(self.overfishing_limit) if self.overfishing_limit else None,
            'acceptable_catch_range_min': float(self.acceptable_catch_range_min) if self.acceptable_catch_range_min else None,
            'acceptable_catch_range_max': float(self.acceptable_catch_range_max) if self.acceptable_catch_range_max else None,
            'uncertainty_assessment': self.uncertainty_assessment,
            'species': self.species,
            'stock_name': self.stock_name,
            'fmp': self.fmp,
            'document_url': self.document_url,
            'related_assessment_id': self.related_assessment_id,
            'related_action_id': self.related_action_id,
            'council_action_taken': self.council_action_taken
        }
