-- ===================================================================
-- SAFMC FMP Tracker - User Favorites/Flagging System Migration
-- ===================================================================
-- This migration adds:
-- 1. user_favorites table for flagging research items
-- ===================================================================

BEGIN;

-- ============================================================
-- STEP 1: Create user_favorites table
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_name = 'user_favorites'
    ) THEN
        -- Create user_favorites table
        CREATE TABLE user_favorites (
            id SERIAL PRIMARY KEY,

            -- User who favorited the item
            user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,

            -- Polymorphic fields for any item type
            item_type VARCHAR(50) NOT NULL,  -- 'action', 'meeting', 'assessment', 'document', 'legislation', 'cmod_workshop', 'workplan_item', 'ssc_meeting', 'ssc_recommendation', 'comment'
            item_id VARCHAR(100) NOT NULL,   -- action_id, meeting_id, sedar_number, etc.

            -- User's categorization and notes
            notes TEXT,                      -- User's private notes about this item
            flagged_as VARCHAR(50),          -- 'important', 'review', 'action_needed', 'reference', 'followup'

            -- Timestamps
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

            -- Constraints
            CONSTRAINT uq_user_favorite UNIQUE (user_id, item_type, item_id)
        );

        -- Create indexes for efficient querying
        CREATE INDEX idx_user_favorites_lookup ON user_favorites(user_id, created_at, flagged_as);
        CREATE INDEX idx_user_favorites_type ON user_favorites(user_id, item_type);
        CREATE INDEX idx_user_favorites_user ON user_favorites(user_id);

        -- Create trigger to update updated_at
        CREATE OR REPLACE FUNCTION update_user_favorites_updated_at()
        RETURNS TRIGGER AS $func$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;

        CREATE TRIGGER user_favorites_updated_at
            BEFORE UPDATE ON user_favorites
            FOR EACH ROW
            EXECUTE FUNCTION update_user_favorites_updated_at();

        RAISE NOTICE 'Created user_favorites table with indexes and triggers';
    ELSE
        RAISE NOTICE 'user_favorites table already exists';
    END IF;
END $$;

COMMIT;

-- ===================================================================
-- Rollback script (for reference, run manually if needed)
-- ===================================================================
-- BEGIN;
-- DROP TABLE IF EXISTS user_favorites CASCADE;
-- DROP FUNCTION IF EXISTS update_user_favorites_updated_at() CASCADE;
-- COMMIT;
