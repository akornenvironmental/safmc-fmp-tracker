"""
SQLAlchemy Models for SAFE Reports and SEDAR Assessments System
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from src.config.extensions import db


class SAFEReport(db.Model):
    """SAFE (Stock Assessment and Fishery Evaluation) Report metadata"""
    __tablename__ = 'safe_reports'

    id = db.Column(db.Integer, primary_key=True)

    # Report identification
    fmp = db.Column(db.String(100), nullable=False)  # 'Dolphin Wahoo', 'Shrimp', 'Snapper Grouper'
    report_year = db.Column(db.Integer, nullable=False)
    report_date = db.Column(db.Date)
    version = db.Column(db.String(50))
    report_title = db.Column(db.Text)

    # Source information
    source_url = db.Column(db.String(500))
    source_format = db.Column(db.String(50))  # 'html', 'pdf', 'rpubs', 'hybrid'

    # Content storage
    html_content = db.Column(db.Text)
    pdf_file_path = db.Column(db.String(500))

    # Status
    is_current = db.Column(db.Boolean, default=True)
    is_draft = db.Column(db.Boolean, default=False)

    # Metadata
    last_scraped = db.Column(db.TIMESTAMP, default=datetime.now)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    # Relationships
    stocks = relationship('SAFEReportStock', back_populates='report', cascade='all, delete-orphan')
    sections = relationship('SAFEReportSection', back_populates='report', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'fmp': self.fmp,
            'reportYear': self.report_year,
            'reportDate': self.report_date.isoformat() if self.report_date else None,
            'version': self.version,
            'reportTitle': self.report_title,
            'sourceUrl': self.source_url,
            'sourceFormat': self.source_format,
            'isCurrent': self.is_current,
            'isDraft': self.is_draft,
            'lastScraped': self.last_scraped.isoformat() if self.last_scraped else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'stocksCount': len(self.stocks) if self.stocks else 0
        }


class SAFEReportStock(db.Model):
    """Individual stock/species data from SAFE reports"""
    __tablename__ = 'safe_report_stocks'

    id = db.Column(db.Integer, primary_key=True)
    safe_report_id = db.Column(db.Integer, db.ForeignKey('safe_reports.id', ondelete='CASCADE'), nullable=False)

    # Species identification
    species_name = db.Column(db.String(200), nullable=False)
    common_name = db.Column(db.String(200))
    scientific_name = db.Column(db.String(200))
    stock_id = db.Column(db.String(100))

    # Stock status determination
    stock_status = db.Column(db.String(50))
    overfishing_status = db.Column(db.String(50))
    stock_status_year = db.Column(db.Integer)

    # Catch limits (in pounds unless specified)
    acl = db.Column(db.DECIMAL(15, 2))
    abc = db.Column(db.DECIMAL(15, 2))
    ofl = db.Column(db.DECIMAL(15, 2))
    msy = db.Column(db.DECIMAL(15, 2))
    acl_units = db.Column(db.String(50), default='pounds')

    # Sector allocations
    commercial_acl = db.Column(db.DECIMAL(15, 2))
    recreational_acl = db.Column(db.DECIMAL(15, 2))

    # Actual landings
    commercial_landings = db.Column(db.DECIMAL(15, 2))
    recreational_landings = db.Column(db.DECIMAL(15, 2))
    total_landings = db.Column(db.DECIMAL(15, 2))
    total_discards = db.Column(db.DECIMAL(15, 2))
    dead_discards = db.Column(db.DECIMAL(15, 2))

    # Compliance metrics
    acl_utilization = db.Column(db.DECIMAL(5, 2))
    acl_exceeded = db.Column(db.Boolean, default=False)
    commercial_acl_utilization = db.Column(db.DECIMAL(5, 2))
    recreational_acl_utilization = db.Column(db.DECIMAL(5, 2))

    # Assessment information
    last_assessment_year = db.Column(db.Integer)
    assessment_type = db.Column(db.String(100))
    sedar_number = db.Column(db.String(50))

    # Economic data
    ex_vessel_value = db.Column(db.DECIMAL(15, 2))
    ex_vessel_price_per_pound = db.Column(db.DECIMAL(10, 2))

    # Biological reference points
    ssb = db.Column(db.DECIMAL(15, 2))
    ssb_msy = db.Column(db.DECIMAL(15, 2))
    f = db.Column(db.DECIMAL(10, 4))
    f_msy = db.Column(db.DECIMAL(10, 4))

    # Notes and flags
    notes = db.Column(db.Text)
    data_quality_flag = db.Column(db.String(50))

    # Metadata
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    # Relationships
    report = relationship('SAFEReport', back_populates='stocks')

    def to_dict(self):
        return {
            'id': self.id,
            'safeReportId': self.safe_report_id,
            'speciesName': self.species_name,
            'commonName': self.common_name,
            'scientificName': self.scientific_name,
            'stockId': self.stock_id,
            'stockStatus': self.stock_status,
            'overfishingStatus': self.overfishing_status,
            'stockStatusYear': self.stock_status_year,
            'acl': float(self.acl) if self.acl else None,
            'abc': float(self.abc) if self.abc else None,
            'ofl': float(self.ofl) if self.ofl else None,
            'msy': float(self.msy) if self.msy else None,
            'aclUnits': self.acl_units,
            'commercialAcl': float(self.commercial_acl) if self.commercial_acl else None,
            'recreationalAcl': float(self.recreational_acl) if self.recreational_acl else None,
            'commercialLandings': float(self.commercial_landings) if self.commercial_landings else None,
            'recreationalLandings': float(self.recreational_landings) if self.recreational_landings else None,
            'totalLandings': float(self.total_landings) if self.total_landings else None,
            'totalDiscards': float(self.total_discards) if self.total_discards else None,
            'aclUtilization': float(self.acl_utilization) if self.acl_utilization else None,
            'aclExceeded': self.acl_exceeded,
            'commercialAclUtilization': float(self.commercial_acl_utilization) if self.commercial_acl_utilization else None,
            'recreationalAclUtilization': float(self.recreational_acl_utilization) if self.recreational_acl_utilization else None,
            'lastAssessmentYear': self.last_assessment_year,
            'assessmentType': self.assessment_type,
            'sedarNumber': self.sedar_number,
            'exVesselValue': float(self.ex_vessel_value) if self.ex_vessel_value else None,
            'exVesselPricePerPound': float(self.ex_vessel_price_per_pound) if self.ex_vessel_price_per_pound else None,
            'ssb': float(self.ssb) if self.ssb else None,
            'ssbMsy': float(self.ssb_msy) if self.ssb_msy else None,
            'f': float(self.f) if self.f else None,
            'fMsy': float(self.f_msy) if self.f_msy else None,
            'notes': self.notes,
            'dataQualityFlag': self.data_quality_flag
        }


class SAFEReportSection(db.Model):
    """Extracted sections from SAFE reports for search and analysis"""
    __tablename__ = 'safe_report_sections'

    id = db.Column(db.Integer, primary_key=True)
    safe_report_id = db.Column(db.Integer, db.ForeignKey('safe_reports.id', ondelete='CASCADE'), nullable=False)

    # Section identification
    section_type = db.Column(db.String(100))
    section_title = db.Column(db.Text)
    section_number = db.Column(db.String(50))
    page_number = db.Column(db.Integer)

    # Content
    content = db.Column(db.Text, nullable=False)
    html_content = db.Column(db.Text)

    # AI-generated analysis
    summary = db.Column(db.Text)
    key_points = db.Column(JSONB)
    entities_mentioned = db.Column(JSONB)

    # Tables and figures
    contains_tables = db.Column(db.Boolean, default=False)
    table_data = db.Column(JSONB)
    figure_captions = db.Column(ARRAY(db.Text))

    # Metadata
    word_count = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)

    # Relationships
    report = relationship('SAFEReport', back_populates='sections')

    def to_dict(self):
        return {
            'id': self.id,
            'safeReportId': self.safe_report_id,
            'sectionType': self.section_type,
            'sectionTitle': self.section_title,
            'sectionNumber': self.section_number,
            'pageNumber': self.page_number,
            'content': self.content,
            'summary': self.summary,
            'keyPoints': self.key_points,
            'entitiesMentioned': self.entities_mentioned,
            'containsTables': self.contains_tables,
            'tableData': self.table_data,
            'figureCaptions': self.figure_captions,
            'wordCount': self.word_count
        }


class SEDARAssessment(db.Model):
    """SEDAR stock assessment tracking"""
    __tablename__ = 'sedar_assessments'

    id = db.Column(db.Integer, primary_key=True)

    # SEDAR identification
    sedar_number = db.Column(db.String(50), nullable=False, unique=True)
    full_title = db.Column(db.Text)

    # Species information
    species_name = db.Column(db.String(200))
    common_name = db.Column(db.String(200))
    scientific_name = db.Column(db.String(200))
    stock_area = db.Column(db.String(200))

    # Associated FMP
    fmp = db.Column(db.String(100))
    council = db.Column(db.String(100))

    # Assessment classification
    assessment_status = db.Column(db.String(50))
    assessment_type = db.Column(db.String(100))

    # Timeline
    kickoff_date = db.Column(db.Date)
    data_workshop_date = db.Column(db.Date)
    assessment_workshop_date = db.Column(db.Date)
    review_workshop_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    expected_completion_date = db.Column(db.Date)
    council_review_date = db.Column(db.Date)

    # URLs and documents
    sedar_url = db.Column(db.String(500))
    final_report_url = db.Column(db.String(500))
    executive_summary_url = db.Column(db.String(500))
    data_report_url = db.Column(db.String(500))

    # File paths
    final_report_path = db.Column(db.String(500))
    executive_summary_path = db.Column(db.String(500))

    # Key findings
    stock_status = db.Column(db.String(50))
    overfishing_status = db.Column(db.String(50))

    # Catch recommendations
    abc_recommendation = db.Column(db.DECIMAL(15, 2))
    abc_units = db.Column(db.String(50), default='pounds')
    ofl_recommendation = db.Column(db.DECIMAL(15, 2))

    # Rebuilding
    rebuilding_required = db.Column(db.Boolean)
    rebuilding_timeline = db.Column(db.String(100))
    rebuilding_plan_url = db.Column(db.String(500))

    # Biological reference points
    ssb_current = db.Column(db.DECIMAL(15, 2))
    ssb_msy = db.Column(db.DECIMAL(15, 2))
    ssb_ratio = db.Column(db.DECIMAL(5, 3))
    f_current = db.Column(db.DECIMAL(10, 4))
    f_msy = db.Column(db.DECIMAL(10, 4))
    f_ratio = db.Column(db.DECIMAL(5, 3))

    # Extracted text content
    executive_summary = db.Column(db.Text)
    key_recommendations = db.Column(db.Text)
    management_implications = db.Column(db.Text)
    data_limitations = db.Column(db.Text)

    # Metadata
    last_scraped = db.Column(db.TIMESTAMP, default=datetime.now)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    # Relationships
    action_links = relationship('AssessmentActionLink', back_populates='assessment', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'sedarNumber': self.sedar_number,
            'fullTitle': self.full_title,
            'speciesName': self.species_name,
            'commonName': self.common_name,
            'scientificName': self.scientific_name,
            'stockArea': self.stock_area,
            'fmp': self.fmp,
            'council': self.council,
            'assessmentStatus': self.assessment_status,
            'assessmentType': self.assessment_type,
            'kickoffDate': self.kickoff_date.isoformat() if self.kickoff_date else None,
            'dataWorkshopDate': self.data_workshop_date.isoformat() if self.data_workshop_date else None,
            'assessmentWorkshopDate': self.assessment_workshop_date.isoformat() if self.assessment_workshop_date else None,
            'reviewWorkshopDate': self.review_workshop_date.isoformat() if self.review_workshop_date else None,
            'completionDate': self.completion_date.isoformat() if self.completion_date else None,
            'expectedCompletionDate': self.expected_completion_date.isoformat() if self.expected_completion_date else None,
            'councilReviewDate': self.council_review_date.isoformat() if self.council_review_date else None,
            'sedarUrl': self.sedar_url,
            'finalReportUrl': self.final_report_url,
            'executiveSummaryUrl': self.executive_summary_url,
            'dataReportUrl': self.data_report_url,
            'stockStatus': self.stock_status,
            'overfishingStatus': self.overfishing_status,
            'abcRecommendation': float(self.abc_recommendation) if self.abc_recommendation else None,
            'abcUnits': self.abc_units,
            'oflRecommendation': float(self.ofl_recommendation) if self.ofl_recommendation else None,
            'rebuildingRequired': self.rebuilding_required,
            'rebuildingTimeline': self.rebuilding_timeline,
            'rebuildingPlanUrl': self.rebuilding_plan_url,
            'ssbCurrent': float(self.ssb_current) if self.ssb_current else None,
            'ssbMsy': float(self.ssb_msy) if self.ssb_msy else None,
            'ssbRatio': float(self.ssb_ratio) if self.ssb_ratio else None,
            'fCurrent': float(self.f_current) if self.f_current else None,
            'fMsy': float(self.f_msy) if self.f_msy else None,
            'fRatio': float(self.f_ratio) if self.f_ratio else None,
            'executiveSummary': self.executive_summary,
            'keyRecommendations': self.key_recommendations,
            'managementImplications': self.management_implications,
            'dataLimitations': self.data_limitations,
            'lastScraped': self.last_scraped.isoformat() if self.last_scraped else None,
            'linkedActionsCount': len(self.action_links) if self.action_links else 0
        }


class AssessmentActionLink(db.Model):
    """Links SEDAR assessments to management actions/amendments"""
    __tablename__ = 'assessment_action_links'

    id = db.Column(db.Integer, primary_key=True)

    # References
    sedar_assessment_id = db.Column(db.Integer, db.ForeignKey('sedar_assessments.id', ondelete='CASCADE'))
    action_id = db.Column(db.String(100), db.ForeignKey('actions.action_id', ondelete='CASCADE'))

    # Link metadata
    link_type = db.Column(db.String(50))
    confidence = db.Column(db.String(20), default='medium')

    # Details
    notes = db.Column(db.Text)
    specific_recommendation = db.Column(db.Text)

    # Tracking
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    created_by = db.Column(db.String(100))
    verified = db.Column(db.Boolean, default=False)

    # Relationships
    assessment = relationship('SEDARAssessment', back_populates='action_links')

    def to_dict(self):
        return {
            'id': self.id,
            'sedarAssessmentId': self.sedar_assessment_id,
            'actionId': self.action_id,
            'linkType': self.link_type,
            'confidence': self.confidence,
            'notes': self.notes,
            'specificRecommendation': self.specific_recommendation,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'createdBy': self.created_by,
            'verified': self.verified
        }


class SAFESEDARScrapeLog(db.Model):
    """Tracks SAFE and SEDAR scraping operations"""
    __tablename__ = 'safe_sedar_scrape_log'

    id = db.Column(db.Integer, primary_key=True)

    # Scrape information
    scrape_type = db.Column(db.String(50), nullable=False)
    scrape_target = db.Column(db.String(200))

    # Status
    status = db.Column(db.String(50), nullable=False)

    # Statistics
    items_found = db.Column(db.Integer, default=0)
    items_processed = db.Column(db.Integer, default=0)
    items_created = db.Column(db.Integer, default=0)
    items_updated = db.Column(db.Integer, default=0)
    errors_count = db.Column(db.Integer, default=0)

    # Details
    error_messages = db.Column(ARRAY(db.Text))
    warnings = db.Column(ARRAY(db.Text))

    # Timing
    started_at = db.Column(db.TIMESTAMP, default=datetime.now)
    completed_at = db.Column(db.TIMESTAMP)
    duration_seconds = db.Column(db.Integer)

    # Triggered by
    triggered_by = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'scrapeType': self.scrape_type,
            'scrapeTarget': self.scrape_target,
            'status': self.status,
            'itemsFound': self.items_found,
            'itemsProcessed': self.items_processed,
            'itemsCreated': self.items_created,
            'itemsUpdated': self.items_updated,
            'errorsCount': self.errors_count,
            'errorMessages': self.error_messages,
            'warnings': self.warnings,
            'startedAt': self.started_at.isoformat() if self.started_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
            'durationSeconds': self.duration_seconds,
            'triggeredBy': self.triggered_by
        }


class StockStatusDefinition(db.Model):
    """Reference table for stock status codes"""
    __tablename__ = 'stock_status_definitions'

    status_code = db.Column(db.String(50), primary_key=True)
    status_type = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    severity_level = db.Column(db.Integer)
    color_code = db.Column(db.String(7))

    def to_dict(self):
        return {
            'statusCode': self.status_code,
            'statusType': self.status_type,
            'displayName': self.display_name,
            'description': self.description,
            'severityLevel': self.severity_level,
            'colorCode': self.color_code
        }
