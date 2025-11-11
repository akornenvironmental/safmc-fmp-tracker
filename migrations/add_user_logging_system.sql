-- ===================================================================
-- SAFMC FMP Tracker - User Activity Logging & Super Admin Migration
-- ===================================================================
-- This migration adds:
-- 1. 'super_admin' role to user_roles ENUM
-- 2. user_activity_logs table for comprehensive activity tracking
-- ===================================================================

BEGIN;

-- ============================================================
-- STEP 1: Expand user_roles ENUM to include 'super_admin'
-- ============================================================

DO $$
BEGIN
    -- Check if super_admin already exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumlabel = 'super_admin'
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'user_roles')
    ) THEN
        -- Add super_admin to the ENUM (before 'admin')
        ALTER TYPE user_roles ADD VALUE 'super_admin' BEFORE 'admin';
        RAISE NOTICE 'Added super_admin role to user_roles ENUM';
    ELSE
        RAISE NOTICE 'super_admin role already exists';
    END IF;
END $$;


-- ============================================================
-- STEP 2: Create user_activity_logs table
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_name = 'user_activity_logs'
    ) THEN
        -- Create user_activity_logs table
        CREATE TABLE user_activity_logs (
            id SERIAL PRIMARY KEY,

            -- User identification
            user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
            user_email VARCHAR(255),
            user_role VARCHAR(50),

            -- Activity details
            activity_type VARCHAR(100) NOT NULL,
            activity_category VARCHAR(50),
            description TEXT,

            -- Resource details
            resource_type VARCHAR(100),
            resource_id VARCHAR(255),
            resource_name TEXT,

            -- Request details
            http_method VARCHAR(10),
            endpoint VARCHAR(255),
            request_params JSONB,

            -- Response details
            status_code INTEGER,
            success BOOLEAN DEFAULT TRUE,
            error_message TEXT,

            -- Technical metadata
            ip_address VARCHAR(50),
            user_agent TEXT,
            session_id VARCHAR(100),
            request_duration_ms INTEGER,

            -- Changes tracking (for audit trail)
            changes_made JSONB,
            old_values JSONB,
            new_values JSONB,

            -- Timestamps
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

            -- Full text search
            search_vector TSVECTOR
        );

        -- Create indexes for performance
        CREATE INDEX idx_activity_user ON user_activity_logs(user_id);
        CREATE INDEX idx_activity_email ON user_activity_logs(user_email);
        CREATE INDEX idx_activity_type ON user_activity_logs(activity_type);
        CREATE INDEX idx_activity_category ON user_activity_logs(activity_category);
        CREATE INDEX idx_activity_resource ON user_activity_logs(resource_type, resource_id);
        CREATE INDEX idx_activity_timestamp ON user_activity_logs(created_at DESC);
        CREATE INDEX idx_activity_success ON user_activity_logs(success);
        CREATE INDEX idx_activity_search ON user_activity_logs USING GIN(search_vector);

        -- Create trigger function for full-text search
        CREATE OR REPLACE FUNCTION activity_search_vector_update() RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', COALESCE(NEW.activity_type, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(NEW.resource_name, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(NEW.user_email, '')), 'D');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        -- Create trigger for automatic search vector updates
        CREATE TRIGGER activity_search_vector_trigger
        BEFORE INSERT OR UPDATE OF activity_type, description, resource_name, user_email
        ON user_activity_logs
        FOR EACH ROW
        EXECUTE FUNCTION activity_search_vector_update();

        RAISE NOTICE 'Created user_activity_logs table with indexes and search trigger';
    ELSE
        RAISE NOTICE 'user_activity_logs table already exists';
    END IF;
END $$;

COMMIT;

-- ===================================================================
-- Migration Complete!
-- ===================================================================
-- Next steps:
--   1. Backend already has activity logging middleware
--   2. Backend already has admin routes for user management
--   3. Ready to create frontend UI for user management and activity logs
-- ===================================================================
