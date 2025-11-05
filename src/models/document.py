"""
Document Management and Cross-Reference Models
"""
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from src.config.extensions import db

class Document(db.Model):
    """Document model for centralized document management"""
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    document_type = db.Column(db.String(100))  # Meeting Minutes, Amendment, Report, Presentation, etc.
    fmp = db.Column(db.String(100))
    file_url = db.Column(db.String(500), nullable=False)
    file_size_kb = db.Column(db.Integer)
    file_type = db.Column(db.String(50))  # PDF, DOCX, XLSX, etc.
    document_date = db.Column(db.Date)
    full_text = db.Column(db.Text)  # For full-text search
    summary = db.Column(db.Text)
    topics = db.Column(ARRAY(db.Text))
    related_action_id = db.Column(db.String(100))
    related_meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'))
    related_motion_id = db.Column(db.Integer, db.ForeignKey('motions.id'))
    related_assessment_id = db.Column(db.Integer, db.ForeignKey('stock_assessments.id'))
    uploaded_by = db.Column(db.String(200))
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_full_text=False):
        result = {
            'id': self.id,
            'title': self.title,
            'document_type': self.document_type,
            'fmp': self.fmp,
            'file_url': self.file_url,
            'file_size_kb': self.file_size_kb,
            'file_type': self.file_type,
            'document_date': self.document_date.isoformat() if self.document_date else None,
            'summary': self.summary,
            'topics': self.topics or [],
            'related_action_id': self.related_action_id,
            'related_meeting_id': self.related_meeting_id,
            'related_motion_id': self.related_motion_id,
            'related_assessment_id': self.related_assessment_id,
            'uploaded_by': self.uploaded_by,
            'is_public': self.is_public
        }

        if include_full_text:
            result['full_text'] = self.full_text

        return result


class ActionDocument(db.Model):
    """Many-to-many relationship between actions and documents"""
    __tablename__ = 'action_documents'

    action_id = db.Column(db.String(100), primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), primary_key=True)
    relationship_type = db.Column(db.String(100))  # Primary Document, Supporting Material, Background, etc.

    document = db.relationship('Document', backref='action_links')

    def to_dict(self):
        return {
            'action_id': self.action_id,
            'document_id': self.document_id,
            'relationship_type': self.relationship_type,
            'document': self.document.to_dict() if self.document else None
        }


class MeetingDocument(db.Model):
    """Many-to-many relationship between meetings and documents"""
    __tablename__ = 'meeting_documents'

    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id', ondelete='CASCADE'), primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), primary_key=True)
    relationship_type = db.Column(db.String(100))

    document = db.relationship('Document', backref='meeting_links')

    def to_dict(self):
        return {
            'meeting_id': self.meeting_id,
            'document_id': self.document_id,
            'relationship_type': self.relationship_type,
            'document': self.document.to_dict() if self.document else None
        }


class ActionTopic(db.Model):
    """Topics associated with actions for better search"""
    __tablename__ = 'action_topics'

    action_id = db.Column(db.String(100), primary_key=True)
    topic = db.Column(db.String(255), primary_key=True)
    relevance_score = db.Column(db.Integer)  # 1-10

    def to_dict(self):
        return {
            'action_id': self.action_id,
            'topic': self.topic,
            'relevance_score': self.relevance_score
        }


class MeetingTopic(db.Model):
    """Topics discussed in meetings"""
    __tablename__ = 'meeting_topics'

    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id', ondelete='CASCADE'), primary_key=True)
    topic = db.Column(db.String(255), primary_key=True)
    discussion_duration_minutes = db.Column(db.Integer)

    def to_dict(self):
        return {
            'meeting_id': self.meeting_id,
            'topic': self.topic,
            'discussion_duration_minutes': self.discussion_duration_minutes
        }


class AuditLog(db.Model):
    """Audit log for tracking changes"""
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(50), nullable=False)  # INSERT, UPDATE, DELETE
    changed_by = db.Column(db.String(200))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)

    def to_dict(self):
        return {
            'id': self.id,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'action': self.action,
            'changed_by': self.changed_by,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
            'old_values': self.old_values,
            'new_values': self.new_values
        }
