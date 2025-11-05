"""
Council Member and Voting Models
"""
from datetime import datetime
from src.config.extensions import db

class CouncilMember(db.Model):
    """Council member model"""
    __tablename__ = 'council_members'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(50))
    seat_type = db.Column(db.String(100))  # Commercial, Recreational, State Agency, etc.
    term_start = db.Column(db.Date)
    term_end = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    organization = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    votes = db.relationship('Vote', backref='council_member', lazy=True)
    motions_made = db.relationship('Motion', foreign_keys='Motion.maker_id', backref='maker', lazy=True)
    motions_seconded = db.relationship('Motion', foreign_keys='Motion.second_id', backref='seconder', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'seat_type': self.seat_type,
            'term_start': self.term_start.isoformat() if self.term_start else None,
            'term_end': self.term_end.isoformat() if self.term_end else None,
            'is_active': self.is_active,
            'organization': self.organization,
            'email': self.email,
            'phone': self.phone
        }


class Motion(db.Model):
    """Motion model for council votes"""
    __tablename__ = 'motions'

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'))
    action_id = db.Column(db.String(100))
    motion_number = db.Column(db.String(50))
    motion_text = db.Column(db.Text, nullable=False)
    motion_type = db.Column(db.String(100))  # Main Motion, Amendment, Substitute, etc.
    maker_id = db.Column(db.Integer, db.ForeignKey('council_members.id'))
    second_id = db.Column(db.Integer, db.ForeignKey('council_members.id'))
    vote_result = db.Column(db.String(50))  # Passed, Failed, Tabled, Withdrawn
    vote_date = db.Column(db.Date)
    fmp = db.Column(db.String(100))
    topic = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    votes = db.relationship('Vote', backref='motion', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_votes=False):
        result = {
            'id': self.id,
            'meeting_id': self.meeting_id,
            'action_id': self.action_id,
            'motion_number': self.motion_number,
            'motion_text': self.motion_text,
            'motion_type': self.motion_type,
            'maker_id': self.maker_id,
            'maker_name': self.maker.name if self.maker else None,
            'second_id': self.second_id,
            'seconder_name': self.seconder.name if self.seconder else None,
            'vote_result': self.vote_result,
            'vote_date': self.vote_date.isoformat() if self.vote_date else None,
            'fmp': self.fmp,
            'topic': self.topic
        }

        if include_votes:
            result['votes'] = [vote.to_dict() for vote in self.votes]
            result['vote_summary'] = self.get_vote_summary()

        return result

    def get_vote_summary(self):
        """Get summary of votes"""
        yes_votes = sum(1 for v in self.votes if v.vote == 'Yes')
        no_votes = sum(1 for v in self.votes if v.vote == 'No')
        abstain_votes = sum(1 for v in self.votes if v.vote == 'Abstain')
        absent_votes = sum(1 for v in self.votes if v.vote == 'Absent')
        recused_votes = sum(1 for v in self.votes if v.vote == 'Recused')

        return {
            'yes': yes_votes,
            'no': no_votes,
            'abstain': abstain_votes,
            'absent': absent_votes,
            'recused': recused_votes,
            'total': len(self.votes)
        }


class Vote(db.Model):
    """Individual vote record"""
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    motion_id = db.Column(db.Integer, db.ForeignKey('motions.id'), nullable=False)
    council_member_id = db.Column(db.Integer, db.ForeignKey('council_members.id'), nullable=False)
    vote = db.Column(db.String(20), nullable=False)  # Yes, No, Abstain, Absent, Recused
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'motion_id': self.motion_id,
            'council_member_id': self.council_member_id,
            'council_member_name': self.council_member.name if self.council_member else None,
            'vote': self.vote,
            'notes': self.notes
        }
