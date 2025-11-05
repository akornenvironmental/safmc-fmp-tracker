-- Add council and organization tracking fields to meetings table
-- Migration: add_meeting_council_fields
-- Date: 2025-11-05

-- Add new columns
ALTER TABLE meetings
ADD COLUMN IF NOT EXISTS council VARCHAR(100),
ADD COLUMN IF NOT EXISTS organization_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS rss_feed_url VARCHAR(500);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_meetings_council ON meetings(council);
CREATE INDEX IF NOT EXISTS idx_meetings_org_type ON meetings(organization_type);

-- Update existing meetings to have SAFMC as default council
UPDATE meetings
SET council = 'SAFMC', organization_type = 'Regional Council'
WHERE council IS NULL;
