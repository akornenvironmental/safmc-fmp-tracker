"""Database models for SAFMC FMP Tracker"""

# Existing models
from src.models.action import Action
from src.models.meeting import Meeting
from src.models.comment import Comment

# Voting models
from src.models.council_member import CouncilMember, Motion, Vote

# White paper and scoping models
from src.models.white_paper import WhitePaper, ScopingItem

# Executive order model
from src.models.executive_order import ExecutiveOrder

# Legislative and regulatory models
from src.models.legislation import Legislation, Regulation

# Stock assessment models
from src.models.stock_assessment import StockAssessment, AssessmentComment

# Report models
from src.models.reports import APReport, SSCReport

# Document management models
from src.models.document import (
    Document,
    ActionDocument,
    MeetingDocument,
    ActionTopic,
    MeetingTopic,
    AuditLog
)

# SSC models
from src.models.ssc import (
    SSCMember,
    SSCMeeting,
    SSCRecommendation,
    SSCCouncilConnection,
    SSCDocument
)

__all__ = [
    # Existing
    'Action',
    'Meeting',
    'Comment',
    # Voting
    'CouncilMember',
    'Motion',
    'Vote',
    # White papers and scoping
    'WhitePaper',
    'ScopingItem',
    # Executive orders
    'ExecutiveOrder',
    # Legislative tracking
    'Legislation',
    'Regulation',
    # Stock assessments
    'StockAssessment',
    'AssessmentComment',
    # Reports
    'APReport',
    'SSCReport',
    # Document management
    'Document',
    'ActionDocument',
    'MeetingDocument',
    'ActionTopic',
    'MeetingTopic',
    'AuditLog',
    # SSC
    'SSCMember',
    'SSCMeeting',
    'SSCRecommendation',
    'SSCCouncilConnection',
    'SSCDocument',
]
