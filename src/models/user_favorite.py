"""User Favorite Model for Flagging Research Items"""
from src.config.extensions import db
from datetime import datetime

class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)

    # Polymorphic fields for any item type
    item_type = db.Column(db.String(50), nullable=False)  # 'action', 'meeting', 'assessment', 'document', 'legislation', 'cmod_workshop', 'workplan_item', 'ssc_meeting', 'ssc_recommendation', 'comment'
    item_id = db.Column(db.String(100), nullable=False)  # action_id, meeting_id, sedar_number, etc.

    # User's categorization and notes
    notes = db.Column(db.Text)  # User's private notes about this item
    flagged_as = db.Column(db.String(50))  # 'important', 'review', 'action_needed', 'reference', 'followup'

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('favorites', lazy='dynamic'))

    # Table constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'item_type', 'item_id', name='uq_user_favorite'),
        db.Index('idx_user_favorites_lookup', 'user_id', 'created_at', 'flagged_as'),
        db.Index('idx_user_favorites_type', 'user_id', 'item_type'),
    )

    def to_dict(self):
        """Convert favorite to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'notes': self.notes,
            'flagged_as': self.flagged_as,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<UserFavorite user={self.user_id} type={self.item_type} id={self.item_id}>'
