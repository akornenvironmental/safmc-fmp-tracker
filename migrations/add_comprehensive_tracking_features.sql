-- Comprehensive FMP Tracker Enhancements
-- Migration: add_comprehensive_tracking_features
-- Date: 2025-01-05

-- ============================================
-- 1. ROLL CALL VOTES
-- ============================================

-- Council members table
CREATE TABLE IF NOT EXISTS council_members (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    state VARCHAR(50),
    seat_type VARCHAR(100), -- 'Commercial', 'Recreational', 'State Agency', 'NMFS', 'Coast Guard', etc.
    term_start DATE,
    term_end DATE,
    is_active BOOLEAN DEFAULT TRUE,
    organization VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Motions table
CREATE TABLE IF NOT EXISTS motions (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id),
    action_id VARCHAR(100),
    motion_number VARCHAR(50),
    motion_text TEXT NOT NULL,
    motion_type VARCHAR(100), -- 'Main Motion', 'Amendment', 'Substitute', 'Table', etc.
    maker_id INTEGER REFERENCES council_members(id),
    second_id INTEGER REFERENCES council_members(id),
    vote_result VARCHAR(50), -- 'Passed', 'Failed', 'Tabled', 'Withdrawn'
    vote_date DATE,
    fmp VARCHAR(100),
    topic VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual votes table
CREATE TABLE IF NOT EXISTS votes (
    id SERIAL PRIMARY KEY,
    motion_id INTEGER REFERENCES motions(id) ON DELETE CASCADE,
    council_member_id INTEGER REFERENCES council_members(id),
    vote VARCHAR(20) NOT NULL, -- 'Yes', 'No', 'Abstain', 'Absent', 'Recused'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_votes_motion ON votes(motion_id);
CREATE INDEX IF NOT EXISTS idx_votes_member ON votes(council_member_id);
CREATE INDEX IF NOT EXISTS idx_motions_meeting ON motions(meeting_id);
CREATE INDEX IF NOT EXISTS idx_motions_action ON motions(action_id);

-- ============================================
-- 2. WHITE PAPERS & SCOPING
-- ============================================

CREATE TABLE IF NOT EXISTS white_papers (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    fmp VARCHAR(100),
    topic VARCHAR(255),
    description TEXT,
    requested_date DATE,
    completed_date DATE,
    status VARCHAR(50), -- 'Requested', 'In Progress', 'Completed', 'No Action Taken'
    staff_lead VARCHAR(200),
    council_action VARCHAR(100), -- 'Amendment Initiated', 'No Action', 'Deferred', etc.
    document_url VARCHAR(500),
    meeting_id INTEGER REFERENCES meetings(id),
    source_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scoping_items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    fmp VARCHAR(100),
    scoping_type VARCHAR(100), -- 'General', 'Amendment', 'Framework'
    description TEXT,
    action_id VARCHAR(100), -- NULL if no action taken
    comment_period_start DATE,
    comment_period_end DATE,
    status VARCHAR(50), -- 'Open', 'Closed', 'Action Initiated', 'No Action'
    source_url VARCHAR(500),
    document_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_white_papers_fmp ON white_papers(fmp);
CREATE INDEX IF NOT EXISTS idx_scoping_fmp ON scoping_items(fmp);

-- ============================================
-- 3. EXECUTIVE ORDERS
-- ============================================

CREATE TABLE IF NOT EXISTS executive_orders (
    id SERIAL PRIMARY KEY,
    eo_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    issuing_authority VARCHAR(100), -- 'President', 'Secretary of Commerce', etc.
    issue_date DATE NOT NULL,
    summary TEXT,
    full_text_url VARCHAR(500),
    federal_register_url VARCHAR(500),
    impacts_council BOOLEAN DEFAULT TRUE,
    fmps_affected TEXT[], -- Array of affected FMPs
    council_response_required BOOLEAN DEFAULT FALSE,
    response_deadline DATE,
    status VARCHAR(50), -- 'Received', 'Under Review', 'Response Submitted', 'Completed', 'No Action Required'
    council_response_text TEXT,
    council_response_date DATE,
    council_response_url VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_eo_number ON executive_orders(eo_number);
CREATE INDEX IF NOT EXISTS idx_eo_date ON executive_orders(issue_date);

-- ============================================
-- 4. LEGISLATIVE & REGULATORY TRACKING
-- ============================================

CREATE TABLE IF NOT EXISTS legislation (
    id SERIAL PRIMARY KEY,
    bill_number VARCHAR(50) NOT NULL,
    congress_session VARCHAR(20),
    jurisdiction VARCHAR(50), -- 'Federal', 'NC', 'SC', 'GA', 'FL'
    chamber VARCHAR(50), -- 'House', 'Senate', 'Both'
    title TEXT NOT NULL,
    summary TEXT,
    sponsor VARCHAR(200),
    introduced_date DATE,
    status VARCHAR(100), -- 'Introduced', 'Committee', 'Passed House', 'Passed Senate', 'Enacted', 'Dead'
    last_action TEXT,
    last_action_date DATE,
    bill_url VARCHAR(500),
    full_text_url VARCHAR(500),
    relevance_score INTEGER, -- 1-10 based on keyword match
    keywords TEXT[],
    fmps_affected TEXT[],
    requires_council_action BOOLEAN DEFAULT FALSE,
    council_commented BOOLEAN DEFAULT FALSE,
    council_comment_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(bill_number, jurisdiction, congress_session)
);

CREATE TABLE IF NOT EXISTS regulations (
    id SERIAL PRIMARY KEY,
    regulation_number VARCHAR(100) NOT NULL,
    jurisdiction VARCHAR(50), -- 'Federal', 'NC', 'SC', 'GA', 'FL'
    agency VARCHAR(200),
    title TEXT NOT NULL,
    summary TEXT,
    cfr_citation VARCHAR(100), -- e.g., '50 CFR 622.183'
    effective_date DATE,
    comment_period_start DATE,
    comment_period_end DATE,
    status VARCHAR(100), -- 'Proposed', 'Final', 'Effective', 'Withdrawn'
    federal_register_citation VARCHAR(100),
    federal_register_url VARCHAR(500),
    full_text_url VARCHAR(500),
    relevance_score INTEGER,
    keywords TEXT[],
    fmps_affected TEXT[],
    requires_council_action BOOLEAN DEFAULT FALSE,
    council_commented BOOLEAN DEFAULT FALSE,
    council_comment_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(regulation_number, jurisdiction)
);

CREATE INDEX IF NOT EXISTS idx_legislation_jurisdiction ON legislation(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_legislation_status ON legislation(status);
CREATE INDEX IF NOT EXISTS idx_regulations_jurisdiction ON regulations(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_regulations_status ON regulations(status);

-- ============================================
-- 5. STOCK ASSESSMENTS (SEDAR)
-- ============================================

CREATE TABLE IF NOT EXISTS stock_assessments (
    id SERIAL PRIMARY KEY,
    sedar_number VARCHAR(50) UNIQUE NOT NULL,
    species_common_name VARCHAR(200) NOT NULL,
    species_scientific_name VARCHAR(200),
    stock_region VARCHAR(100), -- 'South Atlantic', 'Gulf', 'Caribbean', etc.
    assessment_type VARCHAR(100), -- 'Benchmark', 'Standard', 'Update', 'Research Track'
    status VARCHAR(100), -- 'Planning', 'In Progress', 'Review', 'Completed'
    start_date DATE,
    completion_date DATE,
    review_workshop_date DATE,
    council_review_date DATE,
    sedar_url VARCHAR(500),
    assessment_report_url VARCHAR(500),
    executive_summary_url VARCHAR(500),
    stock_status VARCHAR(100), -- 'Overfished', 'Not Overfished', 'Overfishing', 'Not Overfishing', 'Unknown'
    overfishing_limit DECIMAL,
    acceptable_biological_catch DECIMAL,
    annual_catch_limit DECIMAL,
    optimum_yield DECIMAL,
    units VARCHAR(50), -- 'pounds', 'numbers', etc.
    fmp VARCHAR(100),
    lead_scientist VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assessment_comments (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES stock_assessments(id) ON DELETE CASCADE,
    commenter_name VARCHAR(200),
    commenter_organization VARCHAR(255),
    comment_text TEXT NOT NULL,
    comment_date DATE,
    comment_type VARCHAR(50), -- 'Public', 'Peer Review', 'SSC', 'Council'
    source_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_assessments_species ON stock_assessments(species_common_name);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON stock_assessments(status);
CREATE INDEX IF NOT EXISTS idx_assessment_comments_assessment ON assessment_comments(assessment_id);

-- ============================================
-- 6. AP & SSC REPORTS
-- ============================================

CREATE TABLE IF NOT EXISTS ap_reports (
    id SERIAL PRIMARY KEY,
    report_title VARCHAR(500) NOT NULL,
    advisory_panel VARCHAR(200) NOT NULL, -- 'Snapper Grouper AP', 'Shrimp AP', etc.
    fmp VARCHAR(100),
    meeting_date DATE,
    report_date DATE,
    summary TEXT,
    recommendations TEXT,
    document_url VARCHAR(500) NOT NULL,
    meeting_location VARCHAR(255),
    related_action_id VARCHAR(100),
    related_meeting_id INTEGER REFERENCES meetings(id),
    council_action_taken TEXT,
    fishery_performance_report BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ssc_reports (
    id SERIAL PRIMARY KEY,
    report_title VARCHAR(500) NOT NULL,
    meeting_date DATE,
    report_date DATE,
    summary TEXT,
    abc_recommendation DECIMAL,
    abc_units VARCHAR(50),
    abc_rationale TEXT,
    overfishing_limit DECIMAL,
    acceptable_catch_range_min DECIMAL,
    acceptable_catch_range_max DECIMAL,
    uncertainty_assessment TEXT,
    species VARCHAR(200),
    stock_name VARCHAR(255),
    fmp VARCHAR(100),
    document_url VARCHAR(500) NOT NULL,
    related_assessment_id INTEGER REFERENCES stock_assessments(id),
    related_action_id VARCHAR(100),
    council_action_taken TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ap_reports_fmp ON ap_reports(fmp);
CREATE INDEX IF NOT EXISTS idx_ap_reports_panel ON ap_reports(advisory_panel);
CREATE INDEX IF NOT EXISTS idx_ssc_reports_species ON ssc_reports(species);
CREATE INDEX IF NOT EXISTS idx_ssc_reports_fmp ON ssc_reports(fmp);

-- ============================================
-- 7. DOCUMENT MANAGEMENT
-- ============================================

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    document_type VARCHAR(100), -- 'Meeting Minutes', 'Amendment', 'Report', 'Presentation', etc.
    fmp VARCHAR(100),
    file_url VARCHAR(500) NOT NULL,
    file_size_kb INTEGER,
    file_type VARCHAR(50), -- 'PDF', 'DOCX', 'XLSX', etc.
    document_date DATE,
    full_text TEXT, -- For full-text search
    summary TEXT,
    topics TEXT[], -- Array of topics/keywords
    related_action_id VARCHAR(100),
    related_meeting_id INTEGER REFERENCES meetings(id),
    related_motion_id INTEGER REFERENCES motions(id),
    related_assessment_id INTEGER REFERENCES stock_assessments(id),
    uploaded_by VARCHAR(200),
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_documents_full_text ON documents USING gin(to_tsvector('english', full_text));
CREATE INDEX IF NOT EXISTS idx_documents_fmp ON documents(fmp);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_topics ON documents USING gin(topics);

-- ============================================
-- 8. ENHANCED COMMENTS TRACKING
-- ============================================

-- Add new fields to existing comments table
ALTER TABLE comments ADD COLUMN IF NOT EXISTS comment_source VARCHAR(255); -- 'General', 'Amendment Specific', 'SEDAR', etc.
ALTER TABLE comments ADD COLUMN IF NOT EXISTS related_action_id VARCHAR(100);
ALTER TABLE comments ADD COLUMN IF NOT EXISTS related_assessment_id INTEGER REFERENCES stock_assessments(id);
ALTER TABLE comments ADD COLUMN IF NOT EXISTS stakeholder_type VARCHAR(100); -- 'Commercial', 'Recreational', 'NGO', 'Industry', 'Academic', etc.
ALTER TABLE comments ADD COLUMN IF NOT EXISTS state VARCHAR(50);
ALTER TABLE comments ADD COLUMN IF NOT EXISTS sentiment_score DECIMAL; -- -1.0 to 1.0
ALTER TABLE comments ADD COLUMN IF NOT EXISTS topics TEXT[]; -- AI-extracted topics
ALTER TABLE comments ADD COLUMN IF NOT EXISTS key_concerns TEXT[]; -- AI-extracted concerns

CREATE INDEX IF NOT EXISTS idx_comments_source ON comments(comment_source);
CREATE INDEX IF NOT EXISTS idx_comments_stakeholder ON comments(stakeholder_type);
CREATE INDEX IF NOT EXISTS idx_comments_topics ON comments USING gin(topics);

-- ============================================
-- 9. CROSS-REFERENCE RELATIONSHIPS
-- ============================================

-- Many-to-many relationship tables for complex associations

CREATE TABLE IF NOT EXISTS action_documents (
    action_id VARCHAR(100) NOT NULL,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100), -- 'Primary Document', 'Supporting Material', 'Background', etc.
    PRIMARY KEY (action_id, document_id)
);

CREATE TABLE IF NOT EXISTS meeting_documents (
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100),
    PRIMARY KEY (meeting_id, document_id)
);

CREATE TABLE IF NOT EXISTS action_topics (
    action_id VARCHAR(100) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    relevance_score INTEGER, -- 1-10
    PRIMARY KEY (action_id, topic)
);

CREATE TABLE IF NOT EXISTS meeting_topics (
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    topic VARCHAR(255) NOT NULL,
    discussion_duration_minutes INTEGER,
    PRIMARY KEY (meeting_id, topic)
);

-- ============================================
-- 10. AUDIT LOG
-- ============================================

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    changed_by VARCHAR(200),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_values JSONB,
    new_values JSONB
);

CREATE INDEX IF NOT EXISTS idx_audit_table ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_record ON audit_log(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_date ON audit_log(changed_at);

-- ============================================
-- GRANT PERMISSIONS (if using specific user)
-- ============================================

-- Uncomment and modify if you have a specific database user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
