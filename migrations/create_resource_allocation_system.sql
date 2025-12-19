-- Migration: Create Resource Allocation Analysis System
-- Purpose: Track and analyze resource allocation across fishery management councils, regional offices, and science centers
-- Date: 2025-12-19
-- Author: Aaron Kornbluth

-- =====================================================
-- 1. COUNCILS (Reference Data)
-- =====================================================
CREATE TABLE IF NOT EXISTS resource_councils (
    id SERIAL PRIMARY KEY,

    -- Identification
    code VARCHAR(20) UNIQUE NOT NULL,           -- 'SAFMC', 'GMFMC', 'MAFMC', etc.
    name VARCHAR(255) NOT NULL,                 -- Full name

    -- Location & Scope
    headquarters_city VARCHAR(100),
    headquarters_state VARCHAR(50),
    geographic_scope TEXT,                       -- Description of jurisdiction
    eez_square_miles DECIMAL(12,2),             -- EEZ area managed

    -- Jurisdictions
    states_covered TEXT[],                       -- Array of state abbreviations

    -- Organizational info
    website_url VARCHAR(500),
    established_year INTEGER,

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resource_councils_code ON resource_councils(code);

-- Insert base council data
INSERT INTO resource_councils (code, name, headquarters_city, headquarters_state, states_covered) VALUES
('SAFMC', 'South Atlantic Fishery Management Council', 'Charleston', 'SC', ARRAY['NC', 'SC', 'GA', 'FL']),
('GMFMC', 'Gulf of Mexico Fishery Management Council', 'Tampa', 'FL', ARRAY['TX', 'LA', 'MS', 'AL', 'FL']),
('MAFMC', 'Mid-Atlantic Fishery Management Council', 'Dover', 'DE', ARRAY['NY', 'NJ', 'DE', 'MD', 'VA', 'NC']),
('NEFMC', 'New England Fishery Management Council', 'Newburyport', 'MA', ARRAY['ME', 'NH', 'MA', 'RI', 'CT']),
('PFMC', 'Pacific Fishery Management Council', 'Portland', 'OR', ARRAY['WA', 'OR', 'CA', 'ID']),
('CFMC', 'Caribbean Fishery Management Council', 'San Juan', 'PR', ARRAY['PR', 'USVI']),
('NPFMC', 'North Pacific Fishery Management Council', 'Anchorage', 'AK', ARRAY['AK']),
('WPFMC', 'Western Pacific Fishery Management Council', 'Honolulu', 'HI', ARRAY['HI', 'AS', 'GU', 'CNMI'])
ON CONFLICT (code) DO NOTHING;


-- =====================================================
-- 2. REGIONAL OFFICES (Reference Data)
-- =====================================================
CREATE TABLE IF NOT EXISTS resource_regional_offices (
    id SERIAL PRIMARY KEY,

    -- Identification
    code VARCHAR(20) UNIQUE NOT NULL,           -- 'SERO', 'GARFO', 'WCR', etc.
    name VARCHAR(255) NOT NULL,

    -- Location
    city VARCHAR(100),
    state VARCHAR(50),

    -- Councils served (many-to-many relationship)
    councils_served TEXT[],                      -- Array of council codes

    -- Organizational info
    website_url VARCHAR(500),

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resource_ro_code ON resource_regional_offices(code);

-- Insert base regional office data
INSERT INTO resource_regional_offices (code, name, city, state, councils_served) VALUES
('SERO', 'Southeast Regional Office', 'St. Petersburg', 'FL', ARRAY['SAFMC', 'GMFMC', 'CFMC']),
('GARFO', 'Greater Atlantic Regional Office', 'Gloucester', 'MA', ARRAY['NEFMC', 'MAFMC']),
('WCR', 'West Coast Region', 'Seattle', 'WA', ARRAY['PFMC']),
('AKRO', 'Alaska Regional Office', 'Juneau', 'AK', ARRAY['NPFMC']),
('PIRO', 'Pacific Islands Regional Office', 'Honolulu', 'HI', ARRAY['WPFMC'])
ON CONFLICT (code) DO NOTHING;


-- =====================================================
-- 3. SCIENCE CENTERS (Reference Data)
-- =====================================================
CREATE TABLE IF NOT EXISTS resource_science_centers (
    id SERIAL PRIMARY KEY,

    -- Identification
    code VARCHAR(20) UNIQUE NOT NULL,           -- 'SEFSC', 'NEFSC', 'NWFSC', etc.
    name VARCHAR(255) NOT NULL,

    -- Location
    city VARCHAR(100),
    state VARCHAR(50),

    -- Councils served
    councils_served TEXT[],                      -- Array of council codes

    -- Organizational info
    website_url VARCHAR(500),

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resource_sc_code ON resource_science_centers(code);

-- Insert base science center data
INSERT INTO resource_science_centers (code, name, city, state, councils_served) VALUES
('SEFSC', 'Southeast Fisheries Science Center', 'Miami', 'FL', ARRAY['SAFMC', 'GMFMC', 'CFMC']),
('NEFSC', 'Northeast Fisheries Science Center', 'Woods Hole', 'MA', ARRAY['NEFMC', 'MAFMC']),
('NWFSC', 'Northwest Fisheries Science Center', 'Seattle', 'WA', ARRAY['PFMC']),
('SWFSC', 'Southwest Fisheries Science Center', 'La Jolla', 'CA', ARRAY['PFMC']),
('AFSC', 'Alaska Fisheries Science Center', 'Seattle', 'WA', ARRAY['NPFMC']),
('PIFSC', 'Pacific Islands Fisheries Science Center', 'Honolulu', 'HI', ARRAY['WPFMC'])
ON CONFLICT (code) DO NOTHING;


-- =====================================================
-- 4. COUNCIL BUDGETS (Time Series Data)
-- =====================================================
CREATE TABLE IF NOT EXISTS resource_council_budgets (
    id SERIAL PRIMARY KEY,

    -- Linkage
    council_id INTEGER NOT NULL REFERENCES resource_councils(id) ON DELETE CASCADE,

    -- Time period
    fiscal_year INTEGER NOT NULL,               -- e.g., 2024, 2025
    budget_period VARCHAR(20),                   -- 'Annual', 'Continuing Resolution'

    -- Budget amounts (in USD)
    operating_budget DECIMAL(12,2),              -- Annual operational grant
    programmatic_funding DECIMAL(12,2),          -- Research/special projects
    total_budget DECIMAL(12,2),                  -- Total funding

    -- Inflation adjustment
    inflation_adjusted_total DECIMAL(12,2),      -- Adjusted to base year (e.g., 2024 dollars)
    base_year INTEGER,                           -- Year for inflation adjustment

    -- Source tracking
    source_document VARCHAR(500),                -- URL or filename
    source_page VARCHAR(50),                     -- Page number in PDF
    data_quality VARCHAR(20),                    -- 'Verified', 'Estimated', 'Placeholder'

    -- Metadata
    notes TEXT,
    entered_by_user_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(council_id, fiscal_year)
);

CREATE INDEX idx_resource_council_budgets_council ON resource_council_budgets(council_id);
CREATE INDEX idx_resource_council_budgets_year ON resource_council_budgets(fiscal_year);


-- =====================================================
-- 5. COUNCIL STAFFING (Time Series Data)
-- =====================================================
CREATE TABLE IF NOT EXISTS resource_council_staffing (
    id SERIAL PRIMARY KEY,

    -- Linkage
    council_id INTEGER NOT NULL REFERENCES resource_councils(id) ON DELETE CASCADE,

    -- Time period
    fiscal_year INTEGER NOT NULL,
    as_of_date DATE,                            -- Specific date of staff count

    -- Staff counts
    total_fte DECIMAL(5,2),                     -- Total full-time equivalent
    professional_staff DECIMAL(5,2),            -- Scientists, analysts, planners
    administrative_staff DECIMAL(5,2),          -- Admin support
    executive_staff INTEGER,                    -- Directors, deputies

    -- Positions
    unfilled_positions INTEGER,                 -- Vacant positions

    -- Source tracking
    source_document VARCHAR(500),
    data_quality VARCHAR(20),

    -- Metadata
    notes TEXT,
    entered_by_user_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(council_id, fiscal_year)
);

CREATE INDEX idx_resource_council_staffing_council ON resource_council_staffing(council_id);
CREATE INDEX idx_resource_council_staffing_year ON resource_council_staffing(fiscal_year);


-- =====================================================
-- 6. REGIONAL OFFICE RESOURCES
-- =====================================================
CREATE TABLE IF NOT EXISTS resource_ro_capacity (
    id SERIAL PRIMARY KEY,

    -- Linkage
    regional_office_id INTEGER NOT NULL REFERENCES resource_regional_offices(id) ON DELETE CASCADE,

    -- Time period
    fiscal_year INTEGER NOT NULL,

    -- Budget
    operations_budget DECIMAL(12,2),

    -- Staffing by division
    sustainable_fisheries_fte DECIMAL(5,2),
    protected_resources_fte DECIMAL(5,2),
    habitat_conservation_fte DECIMAL(5,2),
    law_enforcement_fte DECIMAL(5,2),
    administrative_fte DECIMAL(5,2),
    total_fte DECIMAL(5,2),

    -- Source tracking
    source_document VARCHAR(500),
    data_quality VARCHAR(20),

    -- Metadata
    notes TEXT,
    entered_by_user_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(regional_office_id, fiscal_year)
);

CREATE INDEX idx_resource_ro_capacity_ro ON resource_ro_capacity(regional_office_id);
CREATE INDEX idx_resource_ro_capacity_year ON resource_ro_capacity(fiscal_year);


-- =====================================================
-- 7. SCIENCE CENTER CAPACITY
-- =====================================================
CREATE TABLE IF NOT EXISTS resource_sc_capacity (
    id SERIAL PRIMARY KEY,

    -- Linkage
    science_center_id INTEGER NOT NULL REFERENCES resource_science_centers(id) ON DELETE CASCADE,

    -- Time period
    fiscal_year INTEGER NOT NULL,

    -- Budget
    research_budget DECIMAL(12,2),
    operations_budget DECIMAL(12,2),

    -- Staffing
    research_scientists_fte DECIMAL(5,2),
    survey_staff_fte DECIMAL(5,2),
    laboratory_staff_fte DECIMAL(5,2),
    administrative_fte DECIMAL(5,2),
    total_fte DECIMAL(5,2),

    -- Facilities
    research_vessels INTEGER,
    laboratories INTEGER,

    -- Source tracking
    source_document VARCHAR(500),
    data_quality VARCHAR(20),

    -- Metadata
    notes TEXT,
    entered_by_user_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(science_center_id, fiscal_year)
);

CREATE INDEX idx_resource_sc_capacity_sc ON resource_sc_capacity(science_center_id);
CREATE INDEX idx_resource_sc_capacity_year ON resource_sc_capacity(fiscal_year);


-- =====================================================
-- 8. WORKLOAD METRICS
-- =====================================================
CREATE TABLE IF NOT EXISTS resource_workload_metrics (
    id SERIAL PRIMARY KEY,

    -- Linkage (flexible - can be council, RO, or SC)
    entity_type VARCHAR(20) NOT NULL,           -- 'COUNCIL', 'REGIONAL_OFFICE', 'SCIENCE_CENTER'
    entity_id INTEGER NOT NULL,                 -- ID in respective table

    -- Time period
    fiscal_year INTEGER NOT NULL,

    -- Council-specific metrics
    managed_species INTEGER,                    -- Number of managed species/stocks
    active_fmps INTEGER,                        -- Number of active FMPs
    amendments_in_development INTEGER,
    regulatory_actions_completed INTEGER,

    -- Regional Office metrics
    final_rules_published INTEGER,
    avg_days_to_final_rule DECIMAL(8,2),
    section7_consultations INTEGER,

    -- Science Center metrics
    stock_assessments_requested INTEGER,
    stock_assessments_completed INTEGER,
    stock_assessments_backlog INTEGER,
    survey_days INTEGER,

    -- Source tracking
    source_document VARCHAR(500),
    data_quality VARCHAR(20),

    -- Metadata
    notes TEXT,
    entered_by_user_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(entity_type, entity_id, fiscal_year)
);

CREATE INDEX idx_resource_workload_entity ON resource_workload_metrics(entity_type, entity_id);
CREATE INDEX idx_resource_workload_year ON resource_workload_metrics(fiscal_year);


-- =====================================================
-- 9. DATA COLLECTION TRACKING
-- =====================================================
CREATE TABLE IF NOT EXISTS resource_data_sources (
    id SERIAL PRIMARY KEY,

    -- Source info
    source_name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50),                    -- 'Budget Document', 'Website', 'Annual Report', 'Interview'
    source_url VARCHAR(500),
    document_name VARCHAR(500),

    -- Coverage
    fiscal_years INTEGER[],                     -- Array of years this source covers
    councils_covered TEXT[],                    -- Array of council codes
    data_categories TEXT[],                     -- 'Budget', 'Staffing', 'Workload', etc.

    -- Collection status
    collection_status VARCHAR(50),              -- 'Not Started', 'In Progress', 'Completed', 'Verified'
    priority VARCHAR(20),                       -- 'Tier 1', 'Tier 2', 'Tier 3'
    assigned_to_user_id INTEGER,

    -- Progress tracking
    percent_complete INTEGER DEFAULT 0,
    data_entered_date DATE,
    verified_date DATE,
    verified_by_user_id INTEGER,

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resource_data_sources_status ON resource_data_sources(collection_status);
CREATE INDEX idx_resource_data_sources_priority ON resource_data_sources(priority);


-- =====================================================
-- 10. ANALYSIS DOCUMENTS REPOSITORY
-- =====================================================
CREATE TABLE IF NOT EXISTS resource_analysis_documents (
    id SERIAL PRIMARY KEY,

    -- Document info
    title VARCHAR(500) NOT NULL,
    document_type VARCHAR(100),                 -- 'Framework', 'Strategic Plan', 'Data Collection Template', 'Report'
    file_name VARCHAR(300),
    file_path VARCHAR(500),                     -- Local path or cloud storage URL
    file_type VARCHAR(20),                      -- 'PDF', 'DOCX', 'XLSX', 'MD'
    file_size_bytes INTEGER,

    -- Content
    description TEXT,
    summary TEXT,

    -- Categorization
    tags TEXT[],                                -- 'Budget Analysis', 'SEDAR', 'Strategic Implications', etc.
    fiscal_years INTEGER[],                     -- Years this document covers

    -- Versioning
    version VARCHAR(50),
    is_current BOOLEAN DEFAULT TRUE,
    superseded_by_id INTEGER REFERENCES resource_analysis_documents(id),

    -- Access
    is_public BOOLEAN DEFAULT FALSE,
    uploaded_by_user_id INTEGER,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resource_docs_type ON resource_analysis_documents(document_type);
CREATE INDEX idx_resource_docs_current ON resource_analysis_documents(is_current);
CREATE INDEX idx_resource_docs_tags ON resource_analysis_documents USING GIN(tags);


-- =====================================================
-- 11. CALCULATED METRICS VIEW
-- =====================================================
-- Combines data from multiple tables to show normalized efficiency metrics
CREATE OR REPLACE VIEW v_resource_efficiency_metrics AS
SELECT
    c.code as council_code,
    c.name as council_name,
    cb.fiscal_year,

    -- Budget metrics
    cb.total_budget,
    cb.inflation_adjusted_total,

    -- Staffing metrics
    cs.total_fte as staff_fte,

    -- Workload metrics
    wm.managed_species,
    wm.active_fmps,
    wm.amendments_in_development,

    -- Normalized efficiency ratios
    CASE WHEN wm.managed_species > 0
         THEN cb.total_budget / wm.managed_species
         ELSE NULL END as budget_per_species,

    CASE WHEN wm.managed_species > 0
         THEN cs.total_fte / wm.managed_species
         ELSE NULL END as fte_per_species,

    CASE WHEN cs.total_fte > 0
         THEN cb.total_budget / cs.total_fte
         ELSE NULL END as budget_per_fte,

    CASE WHEN c.eez_square_miles > 0
         THEN cb.total_budget / c.eez_square_miles
         ELSE NULL END as budget_per_sq_mile,

    CASE WHEN c.eez_square_miles > 0
         THEN cs.total_fte / c.eez_square_miles
         ELSE NULL END as fte_per_sq_mile

FROM resource_councils c
LEFT JOIN resource_council_budgets cb ON c.id = cb.council_id
LEFT JOIN resource_council_staffing cs ON c.id = cs.council_id AND cb.fiscal_year = cs.fiscal_year
LEFT JOIN resource_workload_metrics wm ON wm.entity_type = 'COUNCIL'
    AND wm.entity_id = c.id
    AND wm.fiscal_year = cb.fiscal_year;


-- =====================================================
-- 12. REGIONAL COMPARISON VIEW
-- =====================================================
-- Shows resource allocation grouped by regional office/science center
CREATE OR REPLACE VIEW v_regional_resource_comparison AS
SELECT
    ro.code as regional_office_code,
    ro.name as regional_office_name,
    sc.code as science_center_code,
    sc.name as science_center_name,
    roc.fiscal_year,

    -- Councils served count
    array_length(ro.councils_served, 1) as councils_served_count,
    ro.councils_served,

    -- Regional office resources
    roc.total_fte as ro_total_fte,
    roc.operations_budget as ro_budget,

    -- Science center resources
    scc.total_fte as sc_total_fte,
    scc.research_budget as sc_budget,

    -- Ratios
    CASE WHEN array_length(ro.councils_served, 1) > 0
         THEN roc.total_fte / array_length(ro.councils_served, 1)
         ELSE NULL END as ro_fte_per_council,

    CASE WHEN array_length(ro.councils_served, 1) > 0
         THEN scc.total_fte / array_length(ro.councils_served, 1)
         ELSE NULL END as sc_fte_per_council

FROM resource_regional_offices ro
LEFT JOIN resource_ro_capacity roc ON ro.id = roc.regional_office_id
LEFT JOIN resource_science_centers sc ON sc.councils_served && ro.councils_served
LEFT JOIN resource_sc_capacity scc ON sc.id = scc.science_center_id
    AND scc.fiscal_year = roc.fiscal_year;


-- =====================================================
-- COMMENTS & DOCUMENTATION
-- =====================================================
COMMENT ON TABLE resource_councils IS 'Reference data for all 8 regional fishery management councils';
COMMENT ON TABLE resource_regional_offices IS 'NMFS regional offices that support councils';
COMMENT ON TABLE resource_science_centers IS 'NMFS science centers that conduct research and assessments';
COMMENT ON TABLE resource_council_budgets IS 'Annual budget data for each council';
COMMENT ON TABLE resource_council_staffing IS 'Staffing levels for each council by year';
COMMENT ON TABLE resource_ro_capacity IS 'Regional office capacity (budget and staffing) by year';
COMMENT ON TABLE resource_sc_capacity IS 'Science center capacity (budget, staff, facilities) by year';
COMMENT ON TABLE resource_workload_metrics IS 'Workload indicators (species managed, assessments, regulations) by entity and year';
COMMENT ON TABLE resource_data_sources IS 'Tracking for data collection progress and source documents';
COMMENT ON TABLE resource_analysis_documents IS 'Repository of analysis frameworks, reports, and supporting documents';

COMMENT ON VIEW v_resource_efficiency_metrics IS 'Normalized efficiency metrics for cross-council comparison';
COMMENT ON VIEW v_regional_resource_comparison IS 'Resource allocation by region showing multi-council service model impacts';
