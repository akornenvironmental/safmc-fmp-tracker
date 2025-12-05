"""
CMOD (Council Member Ongoing Development) Workshop Models
Tracks CMOD workshops, materials, and cross-council collaboration
"""
from src.config.extensions import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB


class CMODWorkshop(db.Model):
    """
    CMOD Workshop events
    """
    __tablename__ = 'cmod_workshops'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    theme = db.Column(db.String(500))  # Main workshop theme
    description = db.Column(db.Text)

    # Event details
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    location = db.Column(db.String(255))
    host_council = db.Column(db.String(100))  # 'New England', 'North Pacific', 'South Atlantic', etc.

    # Workshop structure
    focus_areas = db.Column(ARRAY(db.String))  # ['EBFM', 'Climate Resilience', 'Communications']
    skills_components = db.Column(ARRAY(db.String))  # ['Motion Crafting', 'Risk Communication']

    # Status
    status = db.Column(db.String(50), default='scheduled')  # 'scheduled', 'completed', 'cancelled'

    # Materials and outcomes
    agenda_url = db.Column(db.Text)
    summary_url = db.Column(db.Text)
    materials_url = db.Column(db.Text)

    # Participation
    participating_councils = db.Column(ARRAY(db.String))
    participant_count = db.Column(db.Integer)

    # Outcomes and impacts
    key_outcomes = db.Column(JSONB)  # Structured outcomes data
    recommendations = db.Column(ARRAY(db.String))

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sessions = db.relationship('CMODSession', back_populates='workshop', lazy='dynamic')
    documents = db.relationship('CMODDocument', back_populates='workshop', lazy='dynamic')

    def to_dict(self):
        return {
            'id': str(self.id),
            'year': self.year,
            'title': self.title,
            'theme': self.theme,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location': self.location,
            'host_council': self.host_council,
            'focus_areas': self.focus_areas or [],
            'skills_components': self.skills_components or [],
            'status': self.status,
            'agenda_url': self.agenda_url,
            'summary_url': self.summary_url,
            'materials_url': self.materials_url,
            'participating_councils': self.participating_councils or [],
            'participant_count': self.participant_count,
            'key_outcomes': self.key_outcomes or {},
            'recommendations': self.recommendations or []
        }


class CMODSession(db.Model):
    """
    Individual sessions within CMOD workshops
    """
    __tablename__ = 'cmod_sessions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workshop_id = db.Column(UUID(as_uuid=True), db.ForeignKey('cmod_workshops.id', ondelete='CASCADE'), nullable=False)

    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    session_type = db.Column(db.String(100))  # 'Presentation', 'Panel', 'Discussion', 'Skills Training'

    # Timing
    session_date = db.Column(db.Date)
    session_order = db.Column(db.Integer)  # Order within workshop

    # Content
    topics = db.Column(ARRAY(db.String))
    councils_presented = db.Column(ARRAY(db.String))  # Which councils presented
    speakers = db.Column(JSONB)  # Array of {name, affiliation, role}

    # Materials
    presentation_url = db.Column(db.Text)
    video_url = db.Column(db.Text)
    notes = db.Column(db.Text)

    # Outcomes
    key_takeaways = db.Column(ARRAY(db.String))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    workshop = db.relationship('CMODWorkshop', back_populates='sessions')

    def to_dict(self):
        return {
            'id': str(self.id),
            'workshop_id': str(self.workshop_id),
            'title': self.title,
            'description': self.description,
            'session_type': self.session_type,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'session_order': self.session_order,
            'topics': self.topics or [],
            'councils_presented': self.councils_presented or [],
            'speakers': self.speakers or [],
            'presentation_url': self.presentation_url,
            'video_url': self.video_url,
            'notes': self.notes,
            'key_takeaways': self.key_takeaways or []
        }


class CMODDocument(db.Model):
    """
    CMOD workshop documents and materials
    """
    __tablename__ = 'cmod_documents'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workshop_id = db.Column(UUID(as_uuid=True), db.ForeignKey('cmod_workshops.id', ondelete='CASCADE'), nullable=False)

    title = db.Column(db.String(500), nullable=False)
    document_type = db.Column(db.String(100))  # 'Agenda', 'Summary', 'Presentation', 'Background Document', 'Resource'
    description = db.Column(db.Text)

    # Document details
    url = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(50))  # 'PDF', 'PPTX', 'DOCX'
    file_size = db.Column(db.String(50))

    # Content
    council_source = db.Column(db.String(100))  # Which council provided this
    topics = db.Column(ARRAY(db.String))
    content_text = db.Column(db.Text)  # Extracted text from document

    # Metadata
    upload_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    workshop = db.relationship('CMODWorkshop', back_populates='documents')

    def to_dict(self):
        return {
            'id': str(self.id),
            'workshop_id': str(self.workshop_id),
            'title': self.title,
            'document_type': self.document_type,
            'description': self.description,
            'url': self.url,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'council_source': self.council_source,
            'topics': self.topics or [],
            'upload_date': self.upload_date.isoformat() if self.upload_date else None
        }


class CMODTopicTracking(db.Model):
    """
    Track how CMOD topics relate to Council actions and priorities
    Links CMOD workshop themes to actual Council activities
    """
    __tablename__ = 'cmod_topic_tracking'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workshop_id = db.Column(UUID(as_uuid=True), db.ForeignKey('cmod_workshops.id', ondelete='CASCADE'))

    topic = db.Column(db.String(255), nullable=False)  # 'EBFM', 'Climate Adaptation', etc.
    description = db.Column(db.Text)

    # Council implementation tracking
    council_name = db.Column(db.String(100))  # 'South Atlantic', 'New England', etc.
    implementation_status = db.Column(db.String(100))  # 'Not Started', 'Planning', 'In Progress', 'Implemented'

    # Linkages to actual work
    related_actions = db.Column(ARRAY(db.String))  # Action IDs from actions table
    related_meetings = db.Column(ARRAY(db.String))  # Meeting IDs
    related_amendments = db.Column(ARRAY(db.String))

    # Progress tracking
    first_discussed = db.Column(db.Date)
    last_updated_council = db.Column(db.Date)
    implementation_notes = db.Column(db.Text)

    # Outcomes
    outcomes_achieved = db.Column(ARRAY(db.String))
    challenges = db.Column(ARRAY(db.String))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'workshop_id': str(self.workshop_id) if self.workshop_id else None,
            'topic': self.topic,
            'description': self.description,
            'council_name': self.council_name,
            'implementation_status': self.implementation_status,
            'related_actions': self.related_actions or [],
            'related_meetings': self.related_meetings or [],
            'related_amendments': self.related_amendments or [],
            'first_discussed': self.first_discussed.isoformat() if self.first_discussed else None,
            'last_updated_council': self.last_updated_council.isoformat() if self.last_updated_council else None,
            'implementation_notes': self.implementation_notes,
            'outcomes_achieved': self.outcomes_achieved or [],
            'challenges': self.challenges or []
        }
