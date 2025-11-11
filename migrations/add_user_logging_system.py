"""
Add User Activity Logging and Super Admin Role

This migration adds:
1. user_activity_logs table for comprehensive activity tracking
2. Expands user_roles ENUM to include 'super_admin'

Run on Render via Shell or locally:
python migrations/add_user_logging_system.py
"""
import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime

# Get database URL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/safmc_fmp_tracker')

print("=" * 70)
print("SAFMC FMP Tracker - User Logging & Permissions Migration")
print("=" * 70)
print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
print(f"Timestamp: {datetime.utcnow().isoformat()}")
print()

engine = create_engine(DATABASE_URL)


def upgrade():
    """Apply the migration"""
    with engine.connect() as conn:
        # ============================================================
        # STEP 1: Expand user_roles ENUM to include 'super_admin'
        # ============================================================
        print("Step 1: Expanding user_roles ENUM to include 'super_admin'...")

        try:
            # Check if super_admin already exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_enum
                    WHERE enumlabel = 'super_admin'
                    AND enumtypid = (
                        SELECT oid FROM pg_type WHERE typname = 'user_roles'
                    )
                );
            """))
            exists = result.scalar()

            if not exists:
                # Add super_admin to the ENUM
                conn.execute(text("""
                    ALTER TYPE user_roles ADD VALUE 'super_admin' BEFORE 'admin';
                """))
                conn.commit()
                print("✓ Added 'super_admin' role to user_roles ENUM")
            else:
                print("• 'super_admin' role already exists")

        except Exception as e:
            print(f"⚠ Warning while updating ENUM: {e}")
            print("  Continuing with migration...")


        # ============================================================
        # STEP 2: Create user_activity_logs table
        # ============================================================
        print("\nStep 2: Creating user_activity_logs table...")

        # Check if table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'user_activity_logs'
            );
        """))
        table_exists = result.scalar()

        if not table_exists:
            # Create user_activity_logs table
            conn.execute(text("""
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
            """))

            # Create indexes for performance
            print("  Creating indexes...")
            conn.execute(text("""
                CREATE INDEX idx_activity_user ON user_activity_logs(user_id);
                CREATE INDEX idx_activity_email ON user_activity_logs(user_email);
                CREATE INDEX idx_activity_type ON user_activity_logs(activity_type);
                CREATE INDEX idx_activity_category ON user_activity_logs(activity_category);
                CREATE INDEX idx_activity_resource ON user_activity_logs(resource_type, resource_id);
                CREATE INDEX idx_activity_timestamp ON user_activity_logs(created_at DESC);
                CREATE INDEX idx_activity_success ON user_activity_logs(success);
                CREATE INDEX idx_activity_search ON user_activity_logs USING GIN(search_vector);
            """))

            # Create trigger for full-text search
            print("  Creating search trigger...")
            conn.execute(text("""
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

                CREATE TRIGGER activity_search_vector_trigger
                BEFORE INSERT OR UPDATE OF activity_type, description, resource_name, user_email
                ON user_activity_logs
                FOR EACH ROW
                EXECUTE FUNCTION activity_search_vector_update();
            """))

            conn.commit()
            print("✓ user_activity_logs table created successfully")
        else:
            print("• user_activity_logs table already exists")


        # ============================================================
        # STEP 3: Create activity types reference (optional helper)
        # ============================================================
        print("\nStep 3: Documenting standard activity types...")

        # This is just documentation - we'll use these activity types in the code
        standard_activities = {
            # Authentication & Authorization
            'user.login': 'User logged in',
            'user.logout': 'User logged out',
            'user.login_failed': 'Login attempt failed',
            'user.token_expired': 'User token expired',

            # User Management (super_admin only)
            'user.created': 'User account created',
            'user.updated': 'User account updated',
            'user.deleted': 'User account deleted',
            'user.role_changed': 'User role changed',
            'user.activated': 'User account activated',
            'user.deactivated': 'User account deactivated',

            # Actions
            'action.viewed': 'Viewed action details',
            'action.created': 'Created new action',
            'action.updated': 'Updated action',
            'action.deleted': 'Deleted action',
            'action.exported': 'Exported actions data',

            # Meetings
            'meeting.viewed': 'Viewed meeting details',
            'meeting.created': 'Created new meeting',
            'meeting.updated': 'Updated meeting',
            'meeting.deleted': 'Deleted meeting',
            'meeting.exported': 'Exported meetings data',

            # Comments
            'comment.viewed': 'Viewed comment details',
            'comment.created': 'Created new comment',
            'comment.updated': 'Updated comment',
            'comment.deleted': 'Deleted comment',
            'comment.exported': 'Exported comments data',

            # Stock Assessments
            'assessment.viewed': 'Viewed assessment details',
            'assessment.synced': 'Triggered assessment sync',
            'assessment.exported': 'Exported assessments data',

            # Data Operations
            'data.scraped': 'Triggered data scraping',
            'data.exported': 'Exported data',
            'data.imported': 'Imported data',
            'data.bulk_updated': 'Bulk updated data',

            # AI Operations
            'ai.query': 'Made AI query',
            'ai.query_failed': 'AI query failed',

            # Admin Operations
            'admin.settings_viewed': 'Viewed admin settings',
            'admin.settings_updated': 'Updated admin settings',
            'admin.logs_viewed': 'Viewed activity logs',
            'admin.logs_exported': 'Exported activity logs',
        }

        print(f"  Documented {len(standard_activities)} standard activity types")
        print("  (These will be used by the logging middleware)")


print("\n" + "=" * 70)
print("Migration complete!")
print()
print("Next steps:")
print("  1. Create permission middleware decorators")
print("  2. Create activity logging middleware")
print("  3. Add activity logging to API endpoints")
print("  4. Create user management API (super_admin only)")
print("  5. Create activity log viewing API")
print("=" * 70)


def downgrade():
    """Rollback the migration"""
    print("\nRolling back migration...")

    with engine.connect() as conn:
        # Drop user_activity_logs table
        print("Dropping user_activity_logs table...")
        conn.execute(text("DROP TABLE IF EXISTS user_activity_logs CASCADE;"))

        # Note: We cannot easily remove the ENUM value once added
        # This is a PostgreSQL limitation - ENUM values cannot be removed
        print("⚠ Note: 'super_admin' role will remain in user_roles ENUM")
        print("  (PostgreSQL does not support removing ENUM values)")

        conn.commit()
        print("✓ Rollback complete")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='User logging system migration')
    parser.add_argument('--downgrade', action='store_true', help='Rollback the migration')
    args = parser.parse_args()

    try:
        if args.downgrade:
            downgrade()
        else:
            upgrade()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
