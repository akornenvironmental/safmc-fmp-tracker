-- SAFMC Workplan Tables
-- Phase 1: Foundation for tracking amendments, milestones, and integration

-- Main workplan items table
CREATE TABLE IF NOT EXISTS workplan_items (
    id SERIAL PRIMARY KEY,
    amendment_number VARCHAR(50),  -- SG 55, CMP 13, etc.
    amendment_name TEXT NOT NULL,
    category VARCHAR(50) CHECK (category IN ('underway', 'planned', 'other')),
    safmc_lead VARCHAR(100),
    fmp VARCHAR(100), -- Snapper Grouper, CMP, Dolphin Wahoo, Coral
    workload_points DECIMAL(4,2) DEFAULT 0,
    target_start_date DATE,
    statutory_deadline DATE,
    has_statutory_deadline BOOLEAN DEFAULT FALSE,
    is_stock_assessment BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workplan milestones/status by quarter
CREATE TABLE IF NOT EXISTS workplan_milestones (
    id SERIAL PRIMARY KEY,
    workplan_item_id INTEGER REFERENCES workplan_items(id) ON DELETE CASCADE,
    quarter VARCHAR(10) NOT NULL, -- 'Dec-23', 'Mar-24', 'Jun-24', 'Sep-24', etc.
    quarter_date DATE, -- First day of the quarter for sorting
    status_code VARCHAR(20), -- 'DOC', 'PH', 'A', 'O/S', 'AR', '(AP)', '(SSC)', etc.
    status_description TEXT,
    workload_value DECIMAL(4,2), -- 0.5, 1, 1.5, 2, etc.
    is_complete BOOLEAN DEFAULT FALSE,
    is_pending BOOLEAN DEFAULT FALSE,
    actual_completion_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workplan_item_id, quarter)
);

-- Link workplan items to existing actions
CREATE TABLE IF NOT EXISTS workplan_action_links (
    id SERIAL PRIMARY KEY,
    workplan_item_id INTEGER REFERENCES workplan_items(id) ON DELETE CASCADE,
    action_id INTEGER REFERENCES actions(id) ON DELETE CASCADE,
    link_type VARCHAR(50), -- 'exact_match', 'related', 'parent', 'child'
    confidence DECIMAL(3,2), -- 0.0 to 1.0 confidence score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workplan_item_id, action_id)
);

-- Link workplan items to meetings
CREATE TABLE IF NOT EXISTS workplan_meeting_links (
    id SERIAL PRIMARY KEY,
    workplan_item_id INTEGER REFERENCES workplan_items(id) ON DELETE CASCADE,
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    milestone_type VARCHAR(50), -- 'public_hearing', 'council_review', 'ssc_review', 'discussion'
    is_scheduled BOOLEAN DEFAULT FALSE,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workplan_item_id, meeting_id)
);

-- Link workplan items to SSC recommendations
CREATE TABLE IF NOT EXISTS workplan_ssc_links (
    id SERIAL PRIMARY KEY,
    workplan_item_id INTEGER REFERENCES workplan_items(id) ON DELETE CASCADE,
    ssc_meeting_id INTEGER, -- Reference to SSC meetings when we have that table
    recommendation_text TEXT,
    recommendation_date DATE,
    status VARCHAR(50), -- 'pending', 'received', 'incorporated'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workplan upload history (track Excel uploads)
CREATE TABLE IF NOT EXISTS workplan_uploads (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    uploaded_by INTEGER REFERENCES users(id),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quarter_label VARCHAR(20), -- 'Q3 2023', 'Q4 2025', etc.
    items_imported INTEGER DEFAULT 0,
    milestones_imported INTEGER DEFAULT 0,
    notes TEXT
);

-- Status code definitions (for reference)
CREATE TABLE IF NOT EXISTS workplan_status_codes (
    code VARCHAR(20) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    description TEXT,
    color_hex VARCHAR(7), -- For UI display
    category VARCHAR(50), -- 'document', 'meeting', 'approval', 'pending'
    display_order INTEGER
);

-- Insert standard status codes
INSERT INTO workplan_status_codes (code, label, description, color_hex, category, display_order) VALUES
('DOC', 'Document', 'Document preparation/review', '#FDE047', 'document', 1),
('PH', 'Public Hearing', 'Public hearing scheduled or held', '#FB7185', 'meeting', 2),
('A', 'Approved', 'Approved/completed', '#86EFAC', 'approval', 3),
('O/S', 'Outstanding', 'Outstanding/in progress', '#FDE047', 'pending', 4),
('AR', 'Approved for Review', 'Approved for review', '#BFDBFE', 'approval', 5),
('(AP)', 'AP Review', 'Advisory Panel review', '#C4B5FD', 'meeting', 6),
('(SSC)', 'SSC Review', 'Scientific and Statistical Committee review', '#FCA5A5', 'meeting', 7)
ON CONFLICT (code) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_workplan_items_category ON workplan_items(category);
CREATE INDEX IF NOT EXISTS idx_workplan_items_fmp ON workplan_items(fmp);
CREATE INDEX IF NOT EXISTS idx_workplan_items_lead ON workplan_items(safmc_lead);
CREATE INDEX IF NOT EXISTS idx_workplan_milestones_quarter ON workplan_milestones(quarter_date);
CREATE INDEX IF NOT EXISTS idx_workplan_milestones_status ON workplan_milestones(status_code);
CREATE INDEX IF NOT EXISTS idx_workplan_action_links_item ON workplan_action_links(workplan_item_id);
CREATE INDEX IF NOT EXISTS idx_workplan_action_links_action ON workplan_action_links(action_id);
CREATE INDEX IF NOT EXISTS idx_workplan_meeting_links_item ON workplan_meeting_links(workplan_item_id);
CREATE INDEX IF NOT EXISTS idx_workplan_meeting_links_meeting ON workplan_meeting_links(meeting_id);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_workplan_items_updated_at BEFORE UPDATE ON workplan_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workplan_milestones_updated_at BEFORE UPDATE ON workplan_milestones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
