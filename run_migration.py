#!/usr/bin/env python3
"""
Run database migration to add meeting council fields
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_migration():
    """Run the migration SQL"""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    print(f"Connecting to database...")

    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Read migration SQL
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'add_meeting_council_fields.sql')
        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        print("Running migration...")
        print("-" * 60)

        # Split by semicolons and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]

        for statement in statements:
            if statement:
                print(f"Executing: {statement[:100]}...")
                cursor.execute(statement)
                print("  ✓ Success")

        print("-" * 60)
        print("Migration completed successfully!")

        # Verify columns were added
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'meetings'
            AND column_name IN ('council', 'organization_type', 'rss_feed_url')
            ORDER BY column_name
        """)

        columns = cursor.fetchall()
        print("\nVerification - New columns:")
        for col_name, col_type in columns:
            print(f"  • {col_name}: {col_type}")

        cursor.close()
        conn.close()

        print("\n✅ Migration complete! The meetings table now has council tracking fields.")

    except Exception as e:
        print(f"\n❌ ERROR running migration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_migration()
