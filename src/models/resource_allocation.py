"""
Resource Allocation Models - Track and analyze resource allocation across fishery management councils
"""

from datetime import datetime
from src.config.extensions import db


class ResourceCouncil(db.Model):
    """Reference data for fishery management councils"""

    __tablename__ = 'resource_councils'

    id = db.Column(db.Integer, primary_key=True)

    # Identification
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)

    # Location & Scope
    headquarters_city = db.Column(db.String(100))
    headquarters_state = db.Column(db.String(50))
    geographic_scope = db.Column(db.Text)
    eez_square_miles = db.Column(db.Numeric(12, 2))

    # Jurisdictions
    states_covered = db.Column(db.ARRAY(db.Text))

    # Organizational info
    website_url = db.Column(db.String(500))
    established_year = db.Column(db.Integer)

    # Metadata
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    budgets = db.relationship('ResourceCouncilBudget', back_populates='council', cascade='all, delete-orphan')
    staffing = db.relationship('ResourceCouncilStaffing', back_populates='council', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'headquarters': {
                'city': self.headquarters_city,
                'state': self.headquarters_state
            },
            'geographicScope': self.geographic_scope,
            'eezSquareMiles': float(self.eez_square_miles) if self.eez_square_miles else None,
            'statesCovered': self.states_covered,
            'websiteUrl': self.website_url,
            'establishedYear': self.established_year,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class ResourceRegionalOffice(db.Model):
    """NMFS Regional Offices"""

    __tablename__ = 'resource_regional_offices'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    councils_served = db.Column(db.ARRAY(db.Text))
    website_url = db.Column(db.String(500))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    capacity = db.relationship('ResourceROCapacity', back_populates='regional_office', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'councilsServed': self.councils_served,
            'websiteUrl': self.website_url,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class ResourceScienceCenter(db.Model):
    """NMFS Science Centers"""

    __tablename__ = 'resource_science_centers'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    councils_served = db.Column(db.ARRAY(db.Text))
    website_url = db.Column(db.String(500))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    capacity = db.relationship('ResourceSCCapacity', back_populates='science_center', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'councilsServed': self.councils_served,
            'websiteUrl': self.website_url,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class ResourceCouncilBudget(db.Model):
    """Council budget data over time"""

    __tablename__ = 'resource_council_budgets'

    id = db.Column(db.Integer, primary_key=True)
    council_id = db.Column(db.Integer, db.ForeignKey('resource_councils.id'), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)
    budget_period = db.Column(db.String(20))

    # Budget amounts
    operating_budget = db.Column(db.Numeric(12, 2))
    programmatic_funding = db.Column(db.Numeric(12, 2))
    total_budget = db.Column(db.Numeric(12, 2))
    inflation_adjusted_total = db.Column(db.Numeric(12, 2))
    base_year = db.Column(db.Integer)

    # Source tracking
    source_document = db.Column(db.String(500))
    source_page = db.Column(db.String(50))
    data_quality = db.Column(db.String(20))

    # Metadata
    notes = db.Column(db.Text)
    entered_by_user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    council = db.relationship('ResourceCouncil', back_populates='budgets')

    def to_dict(self):
        return {
            'id': self.id,
            'councilId': self.council_id,
            'fiscalYear': self.fiscal_year,
            'budgetPeriod': self.budget_period,
            'operatingBudget': float(self.operating_budget) if self.operating_budget else None,
            'programmaticFunding': float(self.programmatic_funding) if self.programmatic_funding else None,
            'totalBudget': float(self.total_budget) if self.total_budget else None,
            'inflationAdjustedTotal': float(self.inflation_adjusted_total) if self.inflation_adjusted_total else None,
            'baseYear': self.base_year,
            'sourceDocument': self.source_document,
            'sourcePage': self.source_page,
            'dataQuality': self.data_quality,
            'notes': self.notes,
            'enteredByUserId': self.entered_by_user_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class ResourceCouncilStaffing(db.Model):
    """Council staffing data over time"""

    __tablename__ = 'resource_council_staffing'

    id = db.Column(db.Integer, primary_key=True)
    council_id = db.Column(db.Integer, db.ForeignKey('resource_councils.id'), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)
    as_of_date = db.Column(db.Date)

    # Staff counts
    total_fte = db.Column(db.Numeric(5, 2))
    professional_staff = db.Column(db.Numeric(5, 2))
    administrative_staff = db.Column(db.Numeric(5, 2))
    executive_staff = db.Column(db.Integer)
    unfilled_positions = db.Column(db.Integer)

    # Source tracking
    source_document = db.Column(db.String(500))
    data_quality = db.Column(db.String(20))

    # Metadata
    notes = db.Column(db.Text)
    entered_by_user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    council = db.relationship('ResourceCouncil', back_populates='staffing')

    def to_dict(self):
        return {
            'id': self.id,
            'councilId': self.council_id,
            'fiscalYear': self.fiscal_year,
            'asOfDate': self.as_of_date.isoformat() if self.as_of_date else None,
            'totalFte': float(self.total_fte) if self.total_fte else None,
            'professionalStaff': float(self.professional_staff) if self.professional_staff else None,
            'administrativeStaff': float(self.administrative_staff) if self.administrative_staff else None,
            'executiveStaff': self.executive_staff,
            'unfilledPositions': self.unfilled_positions,
            'sourceDocument': self.source_document,
            'dataQuality': self.data_quality,
            'notes': self.notes,
            'enteredByUserId': self.entered_by_user_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class ResourceROCapacity(db.Model):
    """Regional office capacity over time"""

    __tablename__ = 'resource_ro_capacity'

    id = db.Column(db.Integer, primary_key=True)
    regional_office_id = db.Column(db.Integer, db.ForeignKey('resource_regional_offices.id'), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)

    # Budget
    operations_budget = db.Column(db.Numeric(12, 2))

    # Staffing by division
    sustainable_fisheries_fte = db.Column(db.Numeric(5, 2))
    protected_resources_fte = db.Column(db.Numeric(5, 2))
    habitat_conservation_fte = db.Column(db.Numeric(5, 2))
    law_enforcement_fte = db.Column(db.Numeric(5, 2))
    administrative_fte = db.Column(db.Numeric(5, 2))
    total_fte = db.Column(db.Numeric(5, 2))

    # Source tracking
    source_document = db.Column(db.String(500))
    data_quality = db.Column(db.String(20))

    # Metadata
    notes = db.Column(db.Text)
    entered_by_user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    regional_office = db.relationship('ResourceRegionalOffice', back_populates='capacity')

    def to_dict(self):
        return {
            'id': self.id,
            'regionalOfficeId': self.regional_office_id,
            'fiscalYear': self.fiscal_year,
            'operationsBudget': float(self.operations_budget) if self.operations_budget else None,
            'sustainableFisheriesFte': float(self.sustainable_fisheries_fte) if self.sustainable_fisheries_fte else None,
            'protectedResourcesFte': float(self.protected_resources_fte) if self.protected_resources_fte else None,
            'habitatConservationFte': float(self.habitat_conservation_fte) if self.habitat_conservation_fte else None,
            'lawEnforcementFte': float(self.law_enforcement_fte) if self.law_enforcement_fte else None,
            'administrativeFte': float(self.administrative_fte) if self.administrative_fte else None,
            'totalFte': float(self.total_fte) if self.total_fte else None,
            'sourceDocument': self.source_document,
            'dataQuality': self.data_quality,
            'notes': self.notes,
            'enteredByUserId': self.entered_by_user_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class ResourceSCCapacity(db.Model):
    """Science center capacity over time"""

    __tablename__ = 'resource_sc_capacity'

    id = db.Column(db.Integer, primary_key=True)
    science_center_id = db.Column(db.Integer, db.ForeignKey('resource_science_centers.id'), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)

    # Budget
    research_budget = db.Column(db.Numeric(12, 2))
    operations_budget = db.Column(db.Numeric(12, 2))

    # Staffing
    research_scientists_fte = db.Column(db.Numeric(5, 2))
    survey_staff_fte = db.Column(db.Numeric(5, 2))
    laboratory_staff_fte = db.Column(db.Numeric(5, 2))
    administrative_fte = db.Column(db.Numeric(5, 2))
    total_fte = db.Column(db.Numeric(5, 2))

    # Facilities
    research_vessels = db.Column(db.Integer)
    laboratories = db.Column(db.Integer)

    # Source tracking
    source_document = db.Column(db.String(500))
    data_quality = db.Column(db.String(20))

    # Metadata
    notes = db.Column(db.Text)
    entered_by_user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    science_center = db.relationship('ResourceScienceCenter', back_populates='capacity')

    def to_dict(self):
        return {
            'id': self.id,
            'scienceCenterId': self.science_center_id,
            'fiscalYear': self.fiscal_year,
            'researchBudget': float(self.research_budget) if self.research_budget else None,
            'operationsBudget': float(self.operations_budget) if self.operations_budget else None,
            'researchScientistsFte': float(self.research_scientists_fte) if self.research_scientists_fte else None,
            'surveyStaffFte': float(self.survey_staff_fte) if self.survey_staff_fte else None,
            'laboratoryStaffFte': float(self.laboratory_staff_fte) if self.laboratory_staff_fte else None,
            'administrativeFte': float(self.administrative_fte) if self.administrative_fte else None,
            'totalFte': float(self.total_fte) if self.total_fte else None,
            'researchVessels': self.research_vessels,
            'laboratories': self.laboratories,
            'sourceDocument': self.source_document,
            'dataQuality': self.data_quality,
            'notes': self.notes,
            'enteredByUserId': self.entered_by_user_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class ResourceWorkloadMetric(db.Model):
    """Workload metrics for councils, regional offices, and science centers"""

    __tablename__ = 'resource_workload_metrics'

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(20), nullable=False)  # 'COUNCIL', 'REGIONAL_OFFICE', 'SCIENCE_CENTER'
    entity_id = db.Column(db.Integer, nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)

    # Council-specific metrics
    managed_species = db.Column(db.Integer)
    active_fmps = db.Column(db.Integer)
    amendments_in_development = db.Column(db.Integer)
    regulatory_actions_completed = db.Column(db.Integer)

    # Regional Office metrics
    final_rules_published = db.Column(db.Integer)
    avg_days_to_final_rule = db.Column(db.Numeric(8, 2))
    section7_consultations = db.Column(db.Integer)

    # Science Center metrics
    stock_assessments_requested = db.Column(db.Integer)
    stock_assessments_completed = db.Column(db.Integer)
    stock_assessments_backlog = db.Column(db.Integer)
    survey_days = db.Column(db.Integer)

    # Source tracking
    source_document = db.Column(db.String(500))
    data_quality = db.Column(db.String(20))

    # Metadata
    notes = db.Column(db.Text)
    entered_by_user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'entityType': self.entity_type,
            'entityId': self.entity_id,
            'fiscalYear': self.fiscal_year,
            'managedSpecies': self.managed_species,
            'activeFmps': self.active_fmps,
            'amendmentsInDevelopment': self.amendments_in_development,
            'regulatoryActionsCompleted': self.regulatory_actions_completed,
            'finalRulesPublished': self.final_rules_published,
            'avgDaysToFinalRule': float(self.avg_days_to_final_rule) if self.avg_days_to_final_rule else None,
            'section7Consultations': self.section7_consultations,
            'stockAssessmentsRequested': self.stock_assessments_requested,
            'stockAssessmentsCompleted': self.stock_assessments_completed,
            'stockAssessmentsBacklog': self.stock_assessments_backlog,
            'surveyDays': self.survey_days,
            'sourceDocument': self.source_document,
            'dataQuality': self.data_quality,
            'notes': self.notes,
            'enteredByUserId': self.entered_by_user_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class ResourceDataSource(db.Model):
    """Track data collection progress"""

    __tablename__ = 'resource_data_sources'

    id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(255), nullable=False)
    source_type = db.Column(db.String(50))
    source_url = db.Column(db.String(500))
    document_name = db.Column(db.String(500))

    # Coverage
    fiscal_years = db.Column(db.ARRAY(db.Integer))
    councils_covered = db.Column(db.ARRAY(db.Text))
    data_categories = db.Column(db.ARRAY(db.Text))

    # Collection status
    collection_status = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    assigned_to_user_id = db.Column(db.Integer)

    # Progress tracking
    percent_complete = db.Column(db.Integer, default=0)
    data_entered_date = db.Column(db.Date)
    verified_date = db.Column(db.Date)
    verified_by_user_id = db.Column(db.Integer)

    # Metadata
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'sourceName': self.source_name,
            'sourceType': self.source_type,
            'sourceUrl': self.source_url,
            'documentName': self.document_name,
            'fiscalYears': self.fiscal_years,
            'councilsCovered': self.councils_covered,
            'dataCategories': self.data_categories,
            'collectionStatus': self.collection_status,
            'priority': self.priority,
            'assignedToUserId': self.assigned_to_user_id,
            'percentComplete': self.percent_complete,
            'dataEnteredDate': self.data_entered_date.isoformat() if self.data_entered_date else None,
            'verifiedDate': self.verified_date.isoformat() if self.verified_date else None,
            'verifiedByUserId': self.verified_by_user_id,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class ResourceAnalysisDocument(db.Model):
    """Repository of analysis documents"""

    __tablename__ = 'resource_analysis_documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    document_type = db.Column(db.String(100))
    file_name = db.Column(db.String(300))
    file_path = db.Column(db.String(500))
    file_type = db.Column(db.String(20))
    file_size_bytes = db.Column(db.Integer)

    # Content
    description = db.Column(db.Text)
    summary = db.Column(db.Text)

    # Categorization
    tags = db.Column(db.ARRAY(db.Text))
    fiscal_years = db.Column(db.ARRAY(db.Integer))

    # Versioning
    version = db.Column(db.String(50))
    is_current = db.Column(db.Boolean, default=True)
    superseded_by_id = db.Column(db.Integer, db.ForeignKey('resource_analysis_documents.id'))

    # Access
    is_public = db.Column(db.Boolean, default=False)
    uploaded_by_user_id = db.Column(db.Integer)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'documentType': self.document_type,
            'fileName': self.file_name,
            'filePath': self.file_path,
            'fileType': self.file_type,
            'fileSizeBytes': self.file_size_bytes,
            'description': self.description,
            'summary': self.summary,
            'tags': self.tags,
            'fiscalYears': self.fiscal_years,
            'version': self.version,
            'isCurrent': self.is_current,
            'supersededById': self.superseded_by_id,
            'isPublic': self.is_public,
            'uploadedByUserId': self.uploaded_by_user_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
