-- =====================================================
-- SAFE Reports & SEDAR Assessments System Migration
-- =====================================================
-- Creates comprehensive tracking system for:
-- - SAFE (Stock Assessment and Fishery Evaluation) Reports
-- - SEDAR Stock Assessments
-- - Stock status data and ACL compliance
-- - Assessment-to-action linkages
--
-- Author: Claude Code
-- Date: November 20, 2025
-- =====================================================

-- =====================================================
-- 1. SAFE REPORTS TABLES
-- =====================================================

-- Main SAFE reports metadata table
CREATE TABLE IF NOT EXISTS safe_reports (
    id SERIAL PRIMARY KEY,

    -- Report identification
    fmp VARCHAR(100) NOT NULL,  -- 'Dolphin Wahoo', 'Shrimp', 'Snapper Grouper'
    report_year INTEGER NOT NULL,
    report_date DATE,
    version VARCHAR(50),
    report_title TEXT,

    -- Source information
    source_url VARCHAR(500),
    source_format VARCHAR(50),  -- 'html', 'pdf', 'rpubs', 'hybrid'

    -- Content storage
    html_content TEXT,  -- Full HTML content if available
    pdf_file_path VARCHAR(500),  -- Path to downloaded PDF

    -- Status
    is_current BOOLEAN DEFAULT TRUE,
    is_draft BOOLEAN DEFAULT FALSE,

    -- Metadata
    last_scraped TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(fmp, report_year, version)
);

CREATE INDEX idx_safe_reports_fmp ON safe_reports(fmp);
CREATE INDEX idx_safe_reports_year ON safe_reports(report_year);
CREATE INDEX idx_safe_reports_current ON safe_reports(is_current) WHERE is_current = TRUE;

COMMENT ON TABLE safe_reports IS 'Tracks SAFE report versions and metadata';
COMMENT ON COLUMN safe_reports.fmp IS 'Fishery Management Plan: Dolphin Wahoo, Shrimp, or Snapper Grouper';
COMMENT ON COLUMN safe_reports.is_current IS 'Whether this is the current/active report for the FMP';


-- Individual stock/species data from SAFE reports
CREATE TABLE IF NOT EXISTS safe_report_stocks (
    id SERIAL PRIMARY KEY,
    safe_report_id INTEGER NOT NULL REFERENCES safe_reports(id) ON DELETE CASCADE,

    -- Species identification
    species_name VARCHAR(200) NOT NULL,
    common_name VARCHAR(200),
    scientific_name VARCHAR(200),
    stock_id VARCHAR(100),  -- Official stock ID if available

    -- Stock status determination
    stock_status VARCHAR(50),  -- 'Not Overfished', 'Overfished', 'Unknown', 'Rebuilding'
    overfishing_status VARCHAR(50),  -- 'No Overfishing', 'Overfishing Occurring', 'Unknown'
    stock_status_year INTEGER,  -- Year of status determination

    -- Catch limits (in pounds unless specified)
    acl DECIMAL(15,2),  -- Annual Catch Limit
    abc DECIMAL(15,2),  -- Acceptable Biological Catch
    ofl DECIMAL(15,2),  -- Overfishing Limit
    msy DECIMAL(15,2),  -- Maximum Sustainable Yield
    acl_units VARCHAR(50) DEFAULT 'pounds',  -- 'pounds', 'numbers', 'metric_tons'

    -- Sector allocations
    commercial_acl DECIMAL(15,2),
    recreational_acl DECIMAL(15,2),

    -- Actual landings (same units as ACL)
    commercial_landings DECIMAL(15,2),
    recreational_landings DECIMAL(15,2),
    total_landings DECIMAL(15,2),
    total_discards DECIMAL(15,2),
    dead_discards DECIMAL(15,2),

    -- Compliance metrics
    acl_utilization DECIMAL(5,2),  -- Percentage (landings/ACL * 100)
    acl_exceeded BOOLEAN DEFAULT FALSE,
    commercial_acl_utilization DECIMAL(5,2),
    recreational_acl_utilization DECIMAL(5,2),

    -- Assessment information
    last_assessment_year INTEGER,
    assessment_type VARCHAR(100),  -- 'SEDAR', 'Data-limited', 'Index-based', 'Research Track'
    sedar_number VARCHAR(50),  -- e.g., 'SEDAR 80'

    -- Economic data
    ex_vessel_value DECIMAL(15,2),  -- Commercial fishery value in dollars
    ex_vessel_price_per_pound DECIMAL(10,2),

    -- Biological reference points
    ssb DECIMAL(15,2),  -- Spawning Stock Biomass
    ssb_msy DECIMAL(15,2),  -- SSB at MSY
    f DECIMAL(10,4),  -- Fishing mortality rate
    f_msy DECIMAL(10,4),  -- F at MSY

    -- Notes and flags
    notes TEXT,
    data_quality_flag VARCHAR(50),  -- 'high', 'medium', 'low', 'uncertain'

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_safe_stocks_report ON safe_report_stocks(safe_report_id);
CREATE INDEX idx_safe_stocks_species ON safe_report_stocks(species_name);
CREATE INDEX idx_safe_stocks_status ON safe_report_stocks(stock_status);
CREATE INDEX idx_safe_stocks_overfishing ON safe_report_stocks(overfishing_status);
CREATE INDEX idx_safe_stocks_acl_exceeded ON safe_report_stocks(acl_exceeded) WHERE acl_exceeded = TRUE;

COMMENT ON TABLE safe_report_stocks IS 'Individual stock/species data extracted from SAFE reports';
COMMENT ON COLUMN safe_report_stocks.acl_utilization IS 'Percentage of ACL used (total_landings / acl * 100)';


-- Extracted sections from SAFE reports for search and analysis
CREATE TABLE IF NOT EXISTS safe_report_sections (
    id SERIAL PRIMARY KEY,
    safe_report_id INTEGER NOT NULL REFERENCES safe_reports(id) ON DELETE CASCADE,

    -- Section identification
    section_type VARCHAR(100),  -- 'stock_status', 'economics', 'social', 'ecosystem', 'methodology', 'executive_summary'
    section_title TEXT,
    section_number VARCHAR(50),  -- e.g., '3.2.1'
    page_number INTEGER,

    -- Content
    content TEXT NOT NULL,  -- Raw extracted text
    html_content TEXT,  -- HTML version if available

    -- AI-generated analysis
    summary TEXT,  -- AI-generated summary of section
    key_points JSONB,  -- Array of key points extracted
    entities_mentioned JSONB,  -- Species, locations, regulations, people mentioned

    -- Tables and figures
    contains_tables BOOLEAN DEFAULT FALSE,
    table_data JSONB,  -- Extracted table data if applicable
    figure_captions TEXT[],

    -- Metadata
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_safe_sections_report ON safe_report_sections(safe_report_id);
CREATE INDEX idx_safe_sections_type ON safe_report_sections(section_type);
CREATE INDEX idx_safe_sections_entities ON safe_report_sections USING GIN(entities_mentioned);

COMMENT ON TABLE safe_report_sections IS 'Stores extracted sections from SAFE reports for full-text search and AI analysis';


-- =====================================================
-- 2. SEDAR ASSESSMENTS TABLES
-- =====================================================

-- SEDAR stock assessment tracking
CREATE TABLE IF NOT EXISTS sedar_assessments (
    id SERIAL PRIMARY KEY,

    -- SEDAR identification
    sedar_number VARCHAR(50) NOT NULL UNIQUE,  -- 'SEDAR 80', 'SEDAR 81', etc.
    full_title TEXT,

    -- Species information
    species_name VARCHAR(200),
    common_name VARCHAR(200),
    scientific_name VARCHAR(200),
    stock_area VARCHAR(200),  -- 'South Atlantic', 'Gulf of Mexico', 'Atlantic-wide'

    -- Associated FMP
    fmp VARCHAR(100),  -- 'Snapper Grouper', 'Dolphin Wahoo', etc.
    council VARCHAR(100),  -- 'SAFMC', 'GMFMC', 'Joint'

    -- Assessment classification
    assessment_status VARCHAR(50),  -- 'Completed', 'In Progress', 'Scheduled', 'Cancelled', 'On Hold'
    assessment_type VARCHAR(100),  -- 'Standard', 'Update', 'Benchmark', 'Operational', 'Research Track'

    -- Timeline
    kickoff_date DATE,
    data_workshop_date DATE,
    assessment_workshop_date DATE,
    review_workshop_date DATE,
    completion_date DATE,
    expected_completion_date DATE,
    council_review_date DATE,

    -- URLs and documents
    sedar_url VARCHAR(500),  -- Link to SEDAR page
    final_report_url VARCHAR(500),
    executive_summary_url VARCHAR(500),
    data_report_url VARCHAR(500),

    -- File paths (if downloaded)
    final_report_path VARCHAR(500),
    executive_summary_path VARCHAR(500),

    -- Key findings (extracted via AI or manual entry)
    stock_status VARCHAR(50),  -- 'Not Overfished', 'Overfished', 'Unknown'
    overfishing_status VARCHAR(50),  -- 'No Overfishing', 'Overfishing Occurring', 'Unknown'

    -- Catch recommendations
    abc_recommendation DECIMAL(15,2),  -- Recommended ABC
    abc_units VARCHAR(50) DEFAULT 'pounds',
    ofl_recommendation DECIMAL(15,2),

    -- Rebuilding
    rebuilding_required BOOLEAN,
    rebuilding_timeline VARCHAR(100),  -- e.g., '10 years', '2030'
    rebuilding_plan_url VARCHAR(500),

    -- Biological reference points
    ssb_current DECIMAL(15,2),
    ssb_msy DECIMAL(15,2),
    ssb_ratio DECIMAL(5,3),  -- SSB/SSB_MSY
    f_current DECIMAL(10,4),
    f_msy DECIMAL(10,4),
    f_ratio DECIMAL(5,3),  -- F/F_MSY

    -- Extracted text content
    executive_summary TEXT,  -- Full executive summary text
    key_recommendations TEXT,  -- Management recommendations
    management_implications TEXT,  -- Management implications section
    data_limitations TEXT,  -- Key data limitations or uncertainties

    -- Metadata
    last_scraped TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sedar_number ON sedar_assessments(sedar_number);
CREATE INDEX idx_sedar_species ON sedar_assessments(species_name);
CREATE INDEX idx_sedar_status ON sedar_assessments(assessment_status);
CREATE INDEX idx_sedar_completion ON sedar_assessments(completion_date);
CREATE INDEX idx_sedar_council ON sedar_assessments(council);
CREATE INDEX idx_sedar_rebuilding ON sedar_assessments(rebuilding_required) WHERE rebuilding_required = TRUE;

COMMENT ON TABLE sedar_assessments IS 'Tracks SEDAR stock assessments with key findings and recommendations';
COMMENT ON COLUMN sedar_assessments.sedar_number IS 'Official SEDAR identifier (e.g., SEDAR 80)';


-- =====================================================
-- 3. LINKING TABLES
-- =====================================================

-- Links SEDAR assessments to management actions/amendments
CREATE TABLE IF NOT EXISTS assessment_action_links (
    id SERIAL PRIMARY KEY,

    -- References
    sedar_assessment_id INTEGER REFERENCES sedar_assessments(id) ON DELETE CASCADE,
    action_id VARCHAR(100) REFERENCES actions(action_id) ON DELETE CASCADE,

    -- Link metadata
    link_type VARCHAR(50),  -- 'basis_for_action', 'referenced_in', 'implements_recommendation', 'updates_after'
    confidence VARCHAR(20) DEFAULT 'medium',  -- 'high', 'medium', 'low' (for automatically detected links)

    -- Details
    notes TEXT,
    specific_recommendation TEXT,  -- Which specific recommendation from assessment

    -- Tracking
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),  -- User ID or 'system' for automatic links
    verified BOOLEAN DEFAULT FALSE,  -- Has this link been manually verified?

    UNIQUE(sedar_assessment_id, action_id, link_type)
);

CREATE INDEX idx_assessment_links_sedar ON assessment_action_links(sedar_assessment_id);
CREATE INDEX idx_assessment_links_action ON assessment_action_links(action_id);
CREATE INDEX idx_assessment_links_type ON assessment_action_links(link_type);
CREATE INDEX idx_assessment_links_unverified ON assessment_action_links(verified) WHERE verified = FALSE;

COMMENT ON TABLE assessment_action_links IS 'Links SEDAR assessments to management actions that use them';


-- =====================================================
-- 4. ENHANCE EXISTING TABLES
-- =====================================================

-- Add SEDAR and SAFE references to stock_assessments table
ALTER TABLE stock_assessments ADD COLUMN IF NOT EXISTS sedar_assessment_id INTEGER REFERENCES sedar_assessments(id) ON DELETE SET NULL;
ALTER TABLE stock_assessments ADD COLUMN IF NOT EXISTS safe_report_id INTEGER REFERENCES safe_reports(id) ON DELETE SET NULL;
ALTER TABLE stock_assessments ADD COLUMN IF NOT EXISTS safe_stock_id INTEGER REFERENCES safe_report_stocks(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_stock_assessments_sedar ON stock_assessments(sedar_assessment_id);
CREATE INDEX IF NOT EXISTS idx_stock_assessments_safe ON stock_assessments(safe_report_id);
CREATE INDEX IF NOT EXISTS idx_stock_assessments_safe_stock ON stock_assessments(safe_stock_id);

COMMENT ON COLUMN stock_assessments.sedar_assessment_id IS 'Link to SEDAR assessment if this is based on one';


-- Add assessment references to actions table
ALTER TABLE actions ADD COLUMN IF NOT EXISTS based_on_assessment_id INTEGER REFERENCES sedar_assessments(id) ON DELETE SET NULL;
ALTER TABLE actions ADD COLUMN IF NOT EXISTS safe_report_reference VARCHAR(100);

CREATE INDEX IF NOT EXISTS idx_actions_assessment ON actions(based_on_assessment_id);

COMMENT ON COLUMN actions.based_on_assessment_id IS 'SEDAR assessment that this action is primarily based on';
COMMENT ON COLUMN actions.safe_report_reference IS 'Reference to SAFE report (e.g., "2024 Snapper Grouper SAFE")';


-- =====================================================
-- 5. VIEWS FOR EASY QUERYING
-- =====================================================

-- View combining current SAFE data for all stocks
CREATE OR REPLACE VIEW v_current_stock_status AS
SELECT
    srs.species_name,
    srs.common_name,
    srs.scientific_name,
    sr.fmp,
    sr.report_year,
    srs.stock_status,
    srs.overfishing_status,
    srs.acl,
    srs.total_landings,
    srs.acl_utilization,
    srs.acl_exceeded,
    srs.ex_vessel_value,
    srs.last_assessment_year,
    srs.sedar_number,
    sa.sedar_number as linked_sedar,
    sa.assessment_status as sedar_status
FROM safe_report_stocks srs
JOIN safe_reports sr ON srs.safe_report_id = sr.id
LEFT JOIN sedar_assessments sa ON srs.sedar_number = sa.sedar_number
WHERE sr.is_current = TRUE
ORDER BY sr.fmp, srs.species_name;

COMMENT ON VIEW v_current_stock_status IS 'Current stock status for all species from most recent SAFE reports';


-- View showing ACL compliance summary by FMP
CREATE OR REPLACE VIEW v_acl_compliance_summary AS
SELECT
    sr.fmp,
    sr.report_year,
    COUNT(*) as total_stocks,
    COUNT(*) FILTER (WHERE srs.acl_exceeded = TRUE) as stocks_exceeding_acl,
    COUNT(*) FILTER (WHERE srs.stock_status = 'Overfished') as overfished_stocks,
    COUNT(*) FILTER (WHERE srs.overfishing_status = 'Overfishing Occurring') as overfishing_stocks,
    ROUND(AVG(srs.acl_utilization), 2) as avg_acl_utilization,
    SUM(srs.ex_vessel_value) as total_fishery_value
FROM safe_reports sr
JOIN safe_report_stocks srs ON sr.id = srs.safe_report_id
WHERE sr.is_current = TRUE
GROUP BY sr.fmp, sr.report_year
ORDER BY sr.fmp;

COMMENT ON VIEW v_acl_compliance_summary IS 'ACL compliance summary by FMP from current SAFE reports';


-- View showing SEDAR assessments with linked actions
CREATE OR REPLACE VIEW v_sedar_with_actions AS
SELECT
    sa.sedar_number,
    sa.species_name,
    sa.assessment_status,
    sa.completion_date,
    sa.stock_status,
    sa.overfishing_status,
    sa.abc_recommendation,
    COUNT(aal.action_id) as linked_actions_count,
    STRING_AGG(aal.action_id, ', ') as linked_action_ids
FROM sedar_assessments sa
LEFT JOIN assessment_action_links aal ON sa.id = aal.sedar_assessment_id
GROUP BY sa.id, sa.sedar_number, sa.species_name, sa.assessment_status,
         sa.completion_date, sa.stock_status, sa.overfishing_status, sa.abc_recommendation
ORDER BY sa.sedar_number;

COMMENT ON VIEW v_sedar_with_actions IS 'SEDAR assessments with count of linked management actions';


-- View showing stock status timeline for a species across multiple SAFE reports
CREATE OR REPLACE VIEW v_stock_status_history AS
SELECT
    srs.species_name,
    sr.fmp,
    sr.report_year,
    srs.stock_status,
    srs.overfishing_status,
    srs.acl,
    srs.total_landings,
    srs.acl_utilization,
    srs.ex_vessel_value,
    srs.last_assessment_year,
    srs.sedar_number
FROM safe_report_stocks srs
JOIN safe_reports sr ON srs.safe_report_id = sr.id
ORDER BY srs.species_name, sr.report_year DESC;

COMMENT ON VIEW v_stock_status_history IS 'Historical stock status for all species across multiple SAFE report years';


-- =====================================================
-- 6. AUDIT AND TRACKING
-- =====================================================

-- Scraping log for SAFE and SEDAR scraping operations
CREATE TABLE IF NOT EXISTS safe_sedar_scrape_log (
    id SERIAL PRIMARY KEY,

    -- Scrape information
    scrape_type VARCHAR(50) NOT NULL,  -- 'safe_reports', 'sedar_assessments'
    scrape_target VARCHAR(200),  -- Specific FMP or SEDAR range

    -- Status
    status VARCHAR(50) NOT NULL,  -- 'started', 'completed', 'failed', 'partial'

    -- Statistics
    items_found INTEGER DEFAULT 0,
    items_processed INTEGER DEFAULT 0,
    items_created INTEGER DEFAULT 0,
    items_updated INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,

    -- Details
    error_messages TEXT[],
    warnings TEXT[],

    -- Timing
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_seconds INTEGER,

    -- Triggered by
    triggered_by VARCHAR(100),  -- User ID or 'system' for scheduled scrapes

    CONSTRAINT chk_status CHECK (status IN ('started', 'completed', 'failed', 'partial'))
);

CREATE INDEX idx_scrape_log_type ON safe_sedar_scrape_log(scrape_type);
CREATE INDEX idx_scrape_log_status ON safe_sedar_scrape_log(status);
CREATE INDEX idx_scrape_log_started ON safe_sedar_scrape_log(started_at);

COMMENT ON TABLE safe_sedar_scrape_log IS 'Tracks SAFE and SEDAR scraping operations for monitoring and debugging';


-- =====================================================
-- 7. REFERENCE DATA
-- =====================================================

-- Stock status reference values
CREATE TABLE IF NOT EXISTS stock_status_definitions (
    status_code VARCHAR(50) PRIMARY KEY,
    status_type VARCHAR(50) NOT NULL,  -- 'stock_status' or 'overfishing_status'
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    severity_level INTEGER,  -- 1=good, 2=concern, 3=critical
    color_code VARCHAR(7)  -- Hex color for UI display
);

INSERT INTO stock_status_definitions (status_code, status_type, display_name, description, severity_level, color_code) VALUES
('Not Overfished', 'stock_status', 'Not Overfished', 'Stock biomass is above the overfished threshold', 1, '#10b981'),
('Overfished', 'stock_status', 'Overfished', 'Stock biomass is below the overfished threshold', 3, '#ef4444'),
('Rebuilding', 'stock_status', 'Rebuilding', 'Stock is recovering under a rebuilding plan', 2, '#f59e0b'),
('Unknown', 'stock_status', 'Unknown', 'Stock status cannot be determined', 2, '#6b7280'),
('No Overfishing', 'overfishing_status', 'No Overfishing', 'Fishing mortality is at or below sustainable levels', 1, '#10b981'),
('Overfishing Occurring', 'overfishing_status', 'Overfishing Occurring', 'Fishing mortality exceeds sustainable levels', 3, '#ef4444'),
('Unknown', 'overfishing_status', 'Unknown', 'Overfishing status cannot be determined', 2, '#6b7280')
ON CONFLICT (status_code) DO NOTHING;

COMMENT ON TABLE stock_status_definitions IS 'Reference table for stock status and overfishing status codes';


-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Log successful migration
DO $$
BEGIN
    RAISE NOTICE 'SAFE Reports & SEDAR Assessments system migration completed successfully';
    RAISE NOTICE 'Created tables: safe_reports, safe_report_stocks, safe_report_sections, sedar_assessments, assessment_action_links, safe_sedar_scrape_log, stock_status_definitions';
    RAISE NOTICE 'Created views: v_current_stock_status, v_acl_compliance_summary, v_sedar_with_actions, v_stock_status_history';
    RAISE NOTICE 'Enhanced tables: stock_assessments, actions';
END $$;
