"""
SSC (Scientific and Statistical Committee) Models
"""
from src.config.extensions import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, ARRAY

class SSCMember(db.Model):
    """SSC Member Model"""
    __tablename__ = 'ssc_members'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(2))
    seat_type = db.Column(db.String(100))
    expertise_area = db.Column(db.String(255))
    affiliation = db.Column(db.String(500))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    is_chair = db.Column(db.Boolean, default=False)
    is_vice_chair = db.Column(db.Boolean, default=False)
    term_start = db.Column(db.Date)
    term_end = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    bio = db.Column(db.Text)
    publications = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'state': self.state,
            'seat_type': self.seat_type,
            'expertise_area': self.expertise_area,
            'affiliation': self.affiliation,
            'email': self.email,
            'phone': self.phone,
            'is_chair': self.is_chair,
            'is_vice_chair': self.is_vice_chair,
            'term_start': self.term_start.isoformat() if self.term_start else None,
            'term_end': self.term_end.isoformat() if self.term_end else None,
            'is_active': self.is_active,
            'bio': self.bio,
            'publications': self.publications
        }


class SSCMeeting(db.Model):
    """SSC Meeting Model"""
    __tablename__ = 'ssc_meetings'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(500), nullable=False)
    meeting_date_start = db.Column(db.DateTime, nullable=False)
    meeting_date_end = db.Column(db.DateTime)
    location = db.Column(db.String(500))
    is_virtual = db.Column(db.Boolean, default=False)
    meeting_type = db.Column(db.String(100))
    status = db.Column(db.String(50), default='scheduled')
    agenda_url = db.Column(db.Text)
    briefing_book_url = db.Column(db.Text)
    report_url = db.Column(db.Text)
    webinar_link = db.Column(db.Text)
    description = db.Column(db.Text)
    topics = db.Column(ARRAY(db.String))
    species_discussed = db.Column(ARRAY(db.String))
    attendance_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recommendations = db.relationship('SSCRecommendation', back_populates='meeting', lazy='dynamic')
    documents = db.relationship('SSCDocument', back_populates='meeting', lazy='dynamic')

    def to_dict(self, include_recommendations=False):
        result = {
            'id': str(self.id),
            'title': self.title,
            'meeting_date_start': self.meeting_date_start.isoformat() if self.meeting_date_start else None,
            'meeting_date_end': self.meeting_date_end.isoformat() if self.meeting_date_end else None,
            'location': self.location,
            'is_virtual': self.is_virtual,
            'meeting_type': self.meeting_type,
            'status': self.status,
            'agenda_url': self.agenda_url,
            'briefing_book_url': self.briefing_book_url,
            'report_url': self.report_url,
            'webinar_link': self.webinar_link,
            'description': self.description,
            'topics': self.topics or [],
            'species_discussed': self.species_discussed or [],
            'attendance_count': self.attendance_count
        }

        if include_recommendations:
            result['recommendations'] = [r.to_dict() for r in self.recommendations]

        return result


class SSCRecommendation(db.Model):
    """SSC Recommendation Model"""
    __tablename__ = 'ssc_recommendations'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ssc_meetings.id', ondelete='SET NULL'))
    recommendation_number = db.Column(db.String(50))
    title = db.Column(db.String(500), nullable=False)
    recommendation_text = db.Column(db.Text, nullable=False)
    recommendation_type = db.Column(db.String(100))
    species = db.Column(ARRAY(db.String))
    fmp = db.Column(db.String(255))
    topic = db.Column(db.String(255))
    abc_value = db.Column(db.Numeric(15, 2))
    abc_units = db.Column(db.String(50))
    overfishing_limit = db.Column(db.Numeric(15, 2))
    status = db.Column(db.String(50), default='pending')
    council_response = db.Column(db.Text)
    council_action_taken = db.Column(db.String(255))
    implementation_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    meeting = db.relationship('SSCMeeting', back_populates='recommendations')
    council_connections = db.relationship('SSCCouncilConnection', back_populates='ssc_recommendation', lazy='dynamic')

    def to_dict(self, include_connections=False):
        result = {
            'id': str(self.id),
            'meeting_id': str(self.meeting_id) if self.meeting_id else None,
            'recommendation_number': self.recommendation_number,
            'title': self.title,
            'recommendation_text': self.recommendation_text,
            'recommendation_type': self.recommendation_type,
            'species': self.species or [],
            'fmp': self.fmp,
            'topic': self.topic,
            'abc_value': float(self.abc_value) if self.abc_value else None,
            'abc_units': self.abc_units,
            'overfishing_limit': float(self.overfishing_limit) if self.overfishing_limit else None,
            'status': self.status,
            'council_response': self.council_response,
            'council_action_taken': self.council_action_taken,
            'implementation_date': self.implementation_date.isoformat() if self.implementation_date else None,
            'notes': self.notes
        }

        if include_connections:
            result['council_connections'] = [c.to_dict() for c in self.council_connections]

        return result


class SSCCouncilConnection(db.Model):
    """SSC-Council Connection Model - Links SSC recommendations to Council actions"""
    __tablename__ = 'ssc_council_connections'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ssc_recommendation_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ssc_recommendations.id', ondelete='CASCADE'))
    council_meeting_id = db.Column(UUID(as_uuid=True))  # No FK constraint - different table structure
    action_id = db.Column(UUID(as_uuid=True))  # No FK constraint - different table structure
    connection_type = db.Column(db.String(100))
    influence_level = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    ssc_recommendation = db.relationship('SSCRecommendation', back_populates='council_connections')

    def to_dict(self):
        return {
            'id': str(self.id),
            'ssc_recommendation_id': str(self.ssc_recommendation_id),
            'council_meeting_id': str(self.council_meeting_id) if self.council_meeting_id else None,
            'action_id': str(self.action_id) if self.action_id else None,
            'connection_type': self.connection_type,
            'influence_level': self.influence_level,
            'notes': self.notes
        }


class SSCDocument(db.Model):
    """SSC Document Model"""
    __tablename__ = 'ssc_documents'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ssc_meetings.id', ondelete='CASCADE'))
    document_type = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    url = db.Column(db.Text, nullable=False)
    file_size = db.Column(db.String(50))
    upload_date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    meeting = db.relationship('SSCMeeting', back_populates='documents')

    def to_dict(self):
        return {
            'id': str(self.id),
            'meeting_id': str(self.meeting_id),
            'document_type': self.document_type,
            'title': self.title,
            'url': self.url,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'description': self.description
        }
