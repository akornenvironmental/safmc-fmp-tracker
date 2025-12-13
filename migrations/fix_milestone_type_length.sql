-- Increase milestone_type column length from VARCHAR(50) to VARCHAR(255)
-- to accommodate longer milestone descriptions

ALTER TABLE workplan_milestones
ALTER COLUMN milestone_type TYPE VARCHAR(255);

-- Also increase notes field if needed
ALTER TABLE workplan_milestones
ALTER COLUMN notes TYPE TEXT;
