"""
SSC Process Models
Tracks formal SSC processes and compares them to actual observed practices
"""
from src.config.extensions import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB


class SSCProcessStep(db.Model):
    """
    Formal process steps from SSC policy documents
    """
    __tablename__ = 'ssc_process_steps'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_type = db.Column(db.String(100), nullable=False)  # 'ABC Review', 'Stock Assessment', 'Research Priority'
    step_number = db.Column(db.Integer, nullable=False)
    step_name = db.Column(db.String(255), nullable=False)
    step_description = db.Column(db.Text)
    required_deliverables = db.Column(ARRAY(db.String))
    typical_duration_days = db.Column(db.Integer)  # Expected duration
    responsible_parties = db.Column(ARRAY(db.String))  # SSC, Council Staff, NMFS, etc.
    prerequisites = db.Column(ARRAY(db.String))  # Previous steps required
    is_required = db.Column(db.Boolean, default=True)
    source_document = db.Column(db.String(255))  # 'SSC Policy 2022', 'Peer Review Process 2013'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'process_type': self.process_type,
            'step_number': self.step_number,
            'step_name': self.step_name,
            'step_description': self.step_description,
            'required_deliverables': self.required_deliverables or [],
            'typical_duration_days': self.typical_duration_days,
            'responsible_parties': self.responsible_parties or [],
            'prerequisites': self.prerequisites or [],
            'is_required': self.is_required,
            'source_document': self.source_document
        }


class SSCObservedPractice(db.Model):
    """
    Actual observed practices from meeting analysis
    Adaptive model that learns from real SSC activities
    """
    __tablename__ = 'ssc_observed_practices'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_type = db.Column(db.String(100), nullable=False)
    practice_pattern = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    frequency_count = db.Column(db.Integer, default=1)  # How often observed
    first_observed = db.Column(db.DateTime, default=datetime.utcnow)
    last_observed = db.Column(db.DateTime, default=datetime.utcnow)
    confidence_score = db.Column(db.Float, default=0.5)  # 0-1, increases with frequency
    typical_duration_observed = db.Column(db.Integer)  # Actual observed duration
    deviation_from_formal = db.Column(db.Boolean, default=False)
    deviation_reason = db.Column(db.Text)
    examples = db.Column(JSONB)  # Array of meeting IDs and details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'process_type': self.process_type,
            'practice_pattern': self.practice_pattern,
            'description': self.description,
            'frequency_count': self.frequency_count,
            'first_observed': self.first_observed.isoformat() if self.first_observed else None,
            'last_observed': self.last_observed.isoformat() if self.last_observed else None,
            'confidence_score': self.confidence_score,
            'typical_duration_observed': self.typical_duration_observed,
            'deviation_from_formal': self.deviation_from_formal,
            'deviation_reason': self.deviation_reason,
            'examples': self.examples or []
        }


class SSCMeetingCompliance(db.Model):
    """
    Compliance tracking for individual SSC meetings
    Links meetings to formal process steps and flags deviations
    """
    __tablename__ = 'ssc_meeting_compliance'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ssc_meetings.id', ondelete='CASCADE'), nullable=False)
    process_type = db.Column(db.String(100), nullable=False)

    # Compliance metrics
    steps_completed = db.Column(ARRAY(db.String))  # Step IDs completed
    steps_skipped = db.Column(ARRAY(db.String))  # Required steps not done
    steps_added = db.Column(ARRAY(db.String))  # Extra steps not in formal process

    # Timeline analysis
    expected_duration_days = db.Column(db.Integer)
    actual_duration_days = db.Column(db.Integer)
    timeline_variance_days = db.Column(db.Integer)  # Negative = early, positive = late

    # Compliance scores
    compliance_score = db.Column(db.Float)  # 0-1, percentage of required steps completed
    timeline_score = db.Column(db.Float)  # 0-1, how close to expected timeline
    overall_score = db.Column(db.Float)  # Weighted average

    # Flags and notes
    has_deviations = db.Column(db.Boolean, default=False)
    deviation_notes = db.Column(db.Text)
    compliance_flags = db.Column(ARRAY(db.String))  # 'missing_deliverables', 'timeline_delay', etc.

    # AI analysis
    ai_insights = db.Column(db.Text)  # AI-generated explanation of patterns
    recommendations = db.Column(ARRAY(db.String))  # Suggested improvements

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    meeting = db.relationship('SSCMeeting', backref='compliance_records')

    def to_dict(self):
        return {
            'id': str(self.id),
            'meeting_id': str(self.meeting_id),
            'process_type': self.process_type,
            'steps_completed': self.steps_completed or [],
            'steps_skipped': self.steps_skipped or [],
            'steps_added': self.steps_added or [],
            'expected_duration_days': self.expected_duration_days,
            'actual_duration_days': self.actual_duration_days,
            'timeline_variance_days': self.timeline_variance_days,
            'compliance_score': self.compliance_score,
            'timeline_score': self.timeline_score,
            'overall_score': self.overall_score,
            'has_deviations': self.has_deviations,
            'deviation_notes': self.deviation_notes,
            'compliance_flags': self.compliance_flags or [],
            'ai_insights': self.ai_insights,
            'recommendations': self.recommendations or []
        }


class SSCProcessDocument(db.Model):
    """
    SSC process documents (policy docs, SOPs, review protocols)
    """
    __tablename__ = 'ssc_process_documents'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(500), nullable=False)
    document_type = db.Column(db.String(100))  # 'Policy', 'SOP', 'Peer Review Protocol'
    url = db.Column(db.Text)
    version_date = db.Column(db.Date)
    content_text = db.Column(db.Text)  # Extracted text from PDF
    extracted_processes = db.Column(JSONB)  # Structured process steps extracted
    is_current = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'document_type': self.document_type,
            'url': self.url,
            'version_date': self.version_date.isoformat() if self.version_date else None,
            'is_current': self.is_current,
            'extracted_processes': self.extracted_processes or {}
        }
