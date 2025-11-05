#!/usr/bin/env python3
"""
Run comprehensive tracking features migration
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_migration():
    """Run the comprehensive migration SQL"""

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
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'add_comprehensive_tracking_features.sql')

        if not os.path.exists(migration_file):
            print(f"ERROR: Migration file not found: {migration_file}")
            sys.exit(1)

        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        print("Running comprehensive tracking features migration...")
        print("This will create 18 new tables for roll call voting, white papers,")
        print("executive orders, legislation, stock assessments, AP/SSC reports, and documents.")
        print("-" * 60)

        # Execute the entire migration as one transaction
        cursor.execute(migration_sql)

        print("-" * 60)
        print("Migration completed successfully!")

        # Verify tables were created
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN (
                'council_members', 'motions', 'votes',
                'white_papers', 'scoping_items',
                'executive_orders',
                'legislation', 'regulations',
                'stock_assessments', 'assessment_comments',
                'ap_reports', 'ssc_reports',
                'documents', 'action_documents', 'meeting_documents',
                'action_topics', 'meeting_topics',
                'audit_log'
            )
            ORDER BY table_name
        """)

        tables = cursor.fetchall()
        print(f"\n✅ Created {len(tables)} new tables:")
        for table in tables:
            print(f"  • {table[0]}")

        cursor.close()
        conn.close()

        print("\n✅ Migration complete! Comprehensive tracking features database is ready.")

    except Exception as e:
        print(f"\n❌ ERROR running migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_migration()
