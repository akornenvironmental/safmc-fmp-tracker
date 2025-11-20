"""
Workplan Models - Track council workplan data with versioning
"""

from datetime import datetime
from src.config.extensions import db


class WorkplanVersion(db.Model):
    """Represents a version of the council workplan (one per meeting/quarter)"""

    __tablename__ = 'workplan_versions'

    id = db.Column(db.Integer, primary_key=True)

    # Version identification
    version_name = db.Column(db.String(200), nullable=False, unique=True)
    council_meeting_id = db.Column(db.String(100))

    # Source information
    source_url = db.Column(db.String(500))
    source_file_name = db.Column(db.String(300))
    upload_type = db.Column(db.String(50))  # 'auto_scraped' or 'manual_upload'
    uploaded_by_user_id = db.Column(db.Integer)

    # Metadata
    quarter = db.Column(db.String(20))
    fiscal_year = db.Column(db.Integer)
    effective_date = db.Column(db.Date)

    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    items = db.relationship('WorkplanItem', back_populates='version', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'versionName': self.version_name,
            'councilMeetingId': self.council_meeting_id,
            'sourceUrl': self.source_url,
            'sourceFileName': self.source_file_name,
            'uploadType': self.upload_type,
            'quarter': self.quarter,
            'fiscalYear': self.fiscal_year,
            'effectiveDate': self.effective_date.isoformat() if self.effective_date else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'isActive': self.is_active,
            'itemCount': len(self.items) if self.items else 0
        }


class WorkplanItem(db.Model):
    """Individual amendment/item within a workplan version"""

    __tablename__ = 'workplan_items'

    id = db.Column(db.Integer, primary_key=True)

    # Link to version
    workplan_version_id = db.Column(db.Integer, db.ForeignKey('workplan_versions.id'), nullable=False)

    # Amendment identification
    amendment_id = db.Column(db.String(100), nullable=False)
    action_id = db.Column(db.String(100), db.ForeignKey('actions.action_id'))

    # Basic info
    topic = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50))  # 'UNDERWAY', 'PLANNED', 'COMPLETED', 'DEFERRED'

    # Assignments
    lead_staff = db.Column(db.String(200))
    sero_priority = db.Column(db.String(50))

    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    version = db.relationship('WorkplanVersion', back_populates='items')
    milestones = db.relationship('WorkplanMilestone', back_populates='item', cascade='all, delete-orphan')

    def to_dict(self, include_milestones=False):
        data = {
            'id': self.id,
            'workplanVersionId': self.workplan_version_id,
            'amendmentId': self.amendment_id,
            'actionId': self.action_id,
            'topic': self.topic,
            'status': self.status,
            'leadStaff': self.lead_staff,
            'seroPriority': self.sero_priority,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_milestones and self.milestones:
            data['milestones'] = [m.to_dict() for m in self.milestones]

        return data


class WorkplanMilestone(db.Model):
    """Timeline milestone for an amendment (S, DOC, PH, A, etc.)"""

    __tablename__ = 'workplan_milestones'

    id = db.Column(db.Integer, primary_key=True)

    # Link to workplan item
    workplan_item_id = db.Column(db.Integer, db.ForeignKey('workplan_items.id'), nullable=False)

    # Milestone details
    milestone_type = db.Column(db.String(50), nullable=False)
    scheduled_date = db.Column(db.Date)
    scheduled_meeting = db.Column(db.String(200))

    # Link to actual meeting
    meeting_id = db.Column(db.String(100), db.ForeignKey('meetings.meeting_id'))

    # Completion tracking
    is_completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.Date)

    # Notes
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    item = db.relationship('WorkplanItem', back_populates='milestones')

    def to_dict(self):
        return {
            'id': self.id,
            'workplanItemId': self.workplan_item_id,
            'milestoneType': self.milestone_type,
            'scheduledDate': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduledMeeting': self.scheduled_meeting,
            'meetingId': self.meeting_id,
            'isCompleted': self.is_completed,
            'completedDate': self.completed_date.isoformat() if self.completed_date else None,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class MilestoneType(db.Model):
    """Reference table for milestone type codes"""

    __tablename__ = 'milestone_types'

    code = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    typical_order = db.Column(db.Integer)
    color = db.Column(db.String(20))

    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'typicalOrder': self.typical_order,
            'color': self.color
        }


class WorkplanUploadLog(db.Model):
    """Audit trail for workplan uploads"""

    __tablename__ = 'workplan_upload_log'

    id = db.Column(db.Integer, primary_key=True)

    workplan_version_id = db.Column(db.Integer, db.ForeignKey('workplan_versions.id'))

    # Upload info
    upload_type = db.Column(db.String(50))
    file_name = db.Column(db.String(300))
    file_size_bytes = db.Column(db.Integer)
    uploaded_by_user_id = db.Column(db.Integer)

    # Processing results
    status = db.Column(db.String(50))
    items_found = db.Column(db.Integer)
    items_created = db.Column(db.Integer)
    items_updated = db.Column(db.Integer)
    milestones_created = db.Column(db.Integer)
    error_message = db.Column(db.Text)

    # Timing
    processing_duration_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'workplanVersionId': self.workplan_version_id,
            'uploadType': self.upload_type,
            'fileName': self.file_name,
            'fileSizeBytes': self.file_size_bytes,
            'status': self.status,
            'itemsFound': self.items_found,
            'itemsCreated': self.items_created,
            'itemsUpdated': self.items_updated,
            'milestonesCreated': self.milestones_created,
            'errorMessage': self.error_message,
            'processingDurationMs': self.processing_duration_ms,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
