-- Add 'super_admin' to user_roles enum
-- Run this with: psql $DATABASE_URL -f migrations/add_super_admin_role.sql

BEGIN;

-- Add 'super_admin' value to the user_roles enum
ALTER TYPE user_roles ADD VALUE IF NOT EXISTS 'super_admin';

COMMIT;

-- Verify the change
SELECT unnest(enum_range(NULL::user_roles))::text AS role;
