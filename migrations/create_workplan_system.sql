-- Migration: Create Workplan System with Versioning
-- Purpose: Track council workplan data including amendment status, timelines, and version history
-- Date: 2025-11-20

-- =====================================================
-- 1. WORKPLAN VERSIONS TABLE
-- =====================================================
-- Tracks different versions of the workplan (one per council meeting)
CREATE TABLE IF NOT EXISTS workplan_versions (
    id SERIAL PRIMARY KEY,

    -- Version identification
    version_name VARCHAR(200) NOT NULL,  -- e.g., "Q3 2025", "September 2025 Meeting"
    council_meeting_id VARCHAR(100),     -- Link to meeting if available

    -- Source information
    source_url VARCHAR(500),             -- URL where workplan was downloaded
    source_file_name VARCHAR(300),       -- Original filename
    upload_type VARCHAR(50),             -- 'auto_scraped' or 'manual_upload'
    uploaded_by_user_id INTEGER,        -- User who uploaded (for manual uploads)

    -- Metadata
    quarter VARCHAR(20),                 -- e.g., "Q3", "Q4"
    fiscal_year INTEGER,                 -- e.g., 2025, 2026
    effective_date DATE,                 -- When this workplan became active

    -- Tracking
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,      -- Mark latest version as active

    UNIQUE(version_name)
);

CREATE INDEX idx_workplan_versions_active ON workplan_versions(is_active);
CREATE INDEX idx_workplan_versions_date ON workplan_versions(effective_date DESC);


-- =====================================================
-- 2. WORKPLAN ITEMS TABLE
-- =====================================================
-- Individual amendments/items within each workplan version
CREATE TABLE IF NOT EXISTS workplan_items (
    id SERIAL PRIMARY KEY,

    -- Link to version
    workplan_version_id INTEGER NOT NULL REFERENCES workplan_versions(id) ON DELETE CASCADE,

    -- Amendment identification
    amendment_id VARCHAR(100) NOT NULL,  -- e.g., "SG Reg 37", "Coral 11/Shrimp 12"
    action_id VARCHAR(100),              -- FK to actions table (matched/linked)

    -- Basic info
    topic TEXT NOT NULL,                 -- Amendment description/topic
    status VARCHAR(50),                  -- 'UNDERWAY', 'PLANNED', 'COMPLETED', 'DEFERRED'

    -- Assignments
    lead_staff VARCHAR(200),             -- SAFMC lead staff (e.g., "Mike", "Kathleen & Allie")
    sero_priority VARCHAR(50),           -- 'Primary', 'Secondary', etc.

    -- Tracking
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (action_id) REFERENCES actions(action_id) ON DELETE SET NULL,
    UNIQUE(workplan_version_id, amendment_id)
);

CREATE INDEX idx_workplan_items_version ON workplan_items(workplan_version_id);
CREATE INDEX idx_workplan_items_action ON workplan_items(action_id);
CREATE INDEX idx_workplan_items_status ON workplan_items(status);


-- =====================================================
-- 3. WORKPLAN MILESTONES TABLE
-- =====================================================
-- Timeline milestones for each amendment (S, DOC, PH, A, AR, etc.)
CREATE TABLE IF NOT EXISTS workplan_milestones (
    id SERIAL PRIMARY KEY,

    -- Link to workplan item
    workplan_item_id INTEGER NOT NULL REFERENCES workplan_items(id) ON DELETE CASCADE,

    -- Milestone details
    milestone_type VARCHAR(50) NOT NULL, -- 'S', 'DOC', 'PH', 'A', 'AR', etc.
    scheduled_date DATE,                 -- When this milestone is scheduled
    scheduled_meeting VARCHAR(200),      -- e.g., "Dec 2025", "March 2026"

    -- Link to actual meeting (when available)
    meeting_id VARCHAR(100),             -- FK to meetings table

    -- Completion tracking
    is_completed BOOLEAN DEFAULT FALSE,
    completed_date DATE,

    -- Notes
    notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id) ON DELETE SET NULL
);

CREATE INDEX idx_workplan_milestones_item ON workplan_milestones(workplan_item_id);
CREATE INDEX idx_workplan_milestones_date ON workplan_milestones(scheduled_date);
CREATE INDEX idx_workplan_milestones_type ON workplan_milestones(milestone_type);
CREATE INDEX idx_workplan_milestones_meeting ON workplan_milestones(meeting_id);


-- =====================================================
-- 4. MILESTONE TYPE DEFINITIONS
-- =====================================================
-- Reference table for milestone type codes
CREATE TABLE IF NOT EXISTS milestone_types (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    typical_order INTEGER,              -- Typical sequence in amendment process
    color VARCHAR(20)                   -- For UI display
);

INSERT INTO milestone_types (code, name, description, typical_order, color) VALUES
('AR', 'Assessment Report', 'Stock assessment report presented or FMP formally initiated', 1, '#3B82F6'),
('S', 'Scoping', 'Approve for public scoping', 2, '#8B5CF6'),
('DOC', 'Document Review', 'Review actions, alternatives, and supporting documentation', 3, '#10B981'),
('PH', 'Public Hearing', 'Hold public hearings on draft amendment', 4, '#F59E0B'),
('A', 'Approval', 'Final approval for submission', 5, '#22C55E'),
('SUBMIT', 'Submitted', 'Amendment submitted to NMFS', 6, '#06B6D4'),
('IMPL', 'Implementation', 'Rule implemented by NMFS', 7, '#14B8A6')
ON CONFLICT (code) DO NOTHING;


-- =====================================================
-- 5. ENHANCE ACTIONS TABLE
-- =====================================================
-- Add workplan-related fields to existing actions table
ALTER TABLE actions
ADD COLUMN IF NOT EXISTS current_workplan_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS lead_staff VARCHAR(200),
ADD COLUMN IF NOT EXISTS sero_priority VARCHAR(50),
ADD COLUMN IF NOT EXISTS next_milestone_type VARCHAR(20),
ADD COLUMN IF NOT EXISTS next_milestone_date DATE;

CREATE INDEX IF NOT EXISTS idx_actions_workplan_status ON actions(current_workplan_status);


-- =====================================================
-- 6. ENHANCE COMMENTS TABLE
-- =====================================================
-- Add milestone tracking to comments
ALTER TABLE comments
ADD COLUMN IF NOT EXISTS milestone_type VARCHAR(20),  -- Which phase was this comment from?
ADD COLUMN IF NOT EXISTS workplan_item_id INTEGER REFERENCES workplan_items(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_comments_milestone_type ON comments(milestone_type);
CREATE INDEX IF NOT EXISTS idx_comments_workplan_item ON comments(workplan_item_id);


-- =====================================================
-- 7. WORKPLAN UPLOAD LOG
-- =====================================================
-- Audit trail for workplan uploads and processing
CREATE TABLE IF NOT EXISTS workplan_upload_log (
    id SERIAL PRIMARY KEY,

    workplan_version_id INTEGER REFERENCES workplan_versions(id) ON DELETE SET NULL,

    -- Upload info
    upload_type VARCHAR(50),             -- 'auto_scraped', 'manual_upload'
    file_name VARCHAR(300),
    file_size_bytes INTEGER,
    uploaded_by_user_id INTEGER,

    -- Processing results
    status VARCHAR(50),                  -- 'success', 'error', 'partial'
    items_found INTEGER,
    items_created INTEGER,
    items_updated INTEGER,
    milestones_created INTEGER,
    error_message TEXT,

    -- Timing
    processing_duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_workplan_upload_log_version ON workplan_upload_log(workplan_version_id);
CREATE INDEX idx_workplan_upload_log_created ON workplan_upload_log(created_at DESC);


-- =====================================================
-- VIEWS FOR EASY QUERYING
-- =====================================================

-- View: Current active workplan with all items
CREATE OR REPLACE VIEW v_current_workplan AS
SELECT
    wv.id as version_id,
    wv.version_name,
    wv.effective_date,
    wi.id as item_id,
    wi.amendment_id,
    wi.action_id,
    wi.topic,
    wi.status,
    wi.lead_staff,
    wi.sero_priority,
    a.title as action_title,
    a.fmp,
    COUNT(DISTINCT wm.id) as milestone_count,
    MIN(CASE WHEN wm.is_completed = FALSE THEN wm.scheduled_date END) as next_milestone_date,
    MIN(CASE WHEN wm.is_completed = FALSE THEN wm.milestone_type END) as next_milestone_type
FROM workplan_versions wv
JOIN workplan_items wi ON wi.workplan_version_id = wv.id
LEFT JOIN actions a ON a.action_id = wi.action_id
LEFT JOIN workplan_milestones wm ON wm.workplan_item_id = wi.id
WHERE wv.is_active = TRUE
GROUP BY wv.id, wv.version_name, wv.effective_date, wi.id, wi.amendment_id,
         wi.action_id, wi.topic, wi.status, wi.lead_staff, wi.sero_priority,
         a.title, a.fmp;


-- View: Amendment timeline changes across versions
CREATE OR REPLACE VIEW v_workplan_history AS
SELECT
    wi.amendment_id,
    wi.topic,
    wv.version_name,
    wv.effective_date,
    wi.status,
    wi.lead_staff,
    wi.sero_priority,
    wv.created_at
FROM workplan_items wi
JOIN workplan_versions wv ON wv.id = wi.workplan_version_id
ORDER BY wi.amendment_id, wv.effective_date DESC;


COMMENT ON TABLE workplan_versions IS 'Tracks different versions of the council workplan (one per meeting/quarter)';
COMMENT ON TABLE workplan_items IS 'Individual amendments/items within each workplan version';
COMMENT ON TABLE workplan_milestones IS 'Timeline milestones for amendments (Scoping, Public Hearing, Approval, etc.)';
COMMENT ON TABLE milestone_types IS 'Reference table for milestone type codes and their meanings';
COMMENT ON TABLE workplan_upload_log IS 'Audit trail for workplan file uploads and processing';
