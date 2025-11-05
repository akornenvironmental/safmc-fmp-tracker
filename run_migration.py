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

        # Remove comment lines and split by semicolons
        lines = [line for line in migration_sql.split('\n') if line.strip() and not line.strip().startswith('--')]
        sql_without_comments = '\n'.join(lines)
        statements = [s.strip() for s in sql_without_comments.split(';') if s.strip()]

        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"{i}. Executing: {statement[:80]}...")
                try:
                    cursor.execute(statement)
                    print("   ✓ Success")
                except Exception as e:
                    print(f"   ✗ Error: {e}")
                    raise

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
