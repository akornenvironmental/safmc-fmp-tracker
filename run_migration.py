#!/usr/bin/env python3
"""
Run SAFE/SEDAR integration system migration
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_migration():
    """Run the SAFE/SEDAR migration SQL"""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Set with: export DATABASE_URL='postgresql://...'")
        sys.exit(1)

    print(f"🚀 Running SAFE/SEDAR migration...")
    print(f"Database: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")

    try:
        # Connect to database with SSL
        conn = psycopg2.connect(database_url, sslmode='require')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("✅ Connected to database")

        # Read migration SQL
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'create_safe_sedar_system.sql')

        if not os.path.exists(migration_file):
            print(f"ERROR: Migration file not found: {migration_file}")
            sys.exit(1)

        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        print(f"📄 Read {len(migration_sql)} characters from migration file")
        print("\nThis will create:")
        print("  • 7 new tables (SAFE reports, SEDAR assessments, stock data, links)")
        print("  • 4 SQL views (stock status, ACL compliance, assessment links)")
        print("  • Enhanced existing tables with assessment references")
        print("-" * 60)

        # Execute the entire migration
        print("🔨 Executing migration SQL...")
        cursor.execute(migration_sql)

        print("-" * 60)
        print("✅ Migration executed successfully!")

        # Verify tables were created
        print("\n🔍 Verifying tables...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN (
                'safe_reports',
                'safe_report_stocks',
                'safe_report_sections',
                'sedar_assessments',
                'assessment_action_links',
                'safe_sedar_scrape_log',
                'stock_status_definitions'
            )
            ORDER BY table_name
        """)

        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} SAFE/SEDAR tables:")
        for table in tables:
            print(f"   - {table[0]}")

        # Verify views were created
        print("\n🔍 Verifying views...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            AND (table_name LIKE 'v_%stock%' OR table_name LIKE 'v_%sedar%' OR table_name LIKE 'v_%acl%')
            ORDER BY table_name
        """)

        views = cursor.fetchall()
        print(f"✅ Found {len(views)} views:")
        for view in views:
            print(f"   - {view[0]}")

        cursor.close()
        conn.close()

        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("  1. Trigger SEDAR import: POST /api/sedar/scrape")
        print("  2. Trigger SAFE import: POST /api/safe-reports/scrape")
        print("  3. Verify data: GET /api/sedar/stats and GET /api/safe-reports/stats")

    except Exception as e:
        print(f"\n❌ ERROR running migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_migration()
