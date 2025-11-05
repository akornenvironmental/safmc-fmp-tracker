#!/usr/bin/env python3
import os
import sys

# Check for DATABASE_URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL environment variable not set")
    print("Please run: export DATABASE_URL='your-database-url'")
    sys.exit(1)

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    print("=" * 60)
    print("SAFMC FMP Tracker - Comprehensive Enhancements Migration")
    print("=" * 60)
    print()
    print(f"Connecting to database...")
    
    conn = psycopg2.connect(database_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Read migration SQL
    with open('migrations/add_comprehensive_tracking_features.sql', 'r') as f:
        migration_sql = f.read()
    
    print("Running comprehensive migration...")
    print("-" * 60)
    
    cursor.execute(migration_sql)
    
    print("-" * 60)
    print("✅ Migration completed successfully!")
    
    # Verify
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN (
            'council_members', 'motions', 'votes',
            'white_papers', 'scoping_items',
            'executive_orders',
            'legislation', 'regulations',
            'stock_assessments', 'assessment_comments',
            'ap_reports', 'ssc_reports',
            'documents', 'action_documents', 'meeting_documents',
            'action_topics', 'meeting_topics', 'audit_log'
        )
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print(f"\n✅ Verified {len(tables)} new tables created:")
    for table in tables:
        print(f"  • {table[0]}")
    
    cursor.close()
    conn.close()
    
    print("\n🎉 All done! The FMP Tracker database is now ready for Phase 2.")
    
except ImportError:
    print("ERROR: psycopg2 not installed")
    print("Install with: pip3 install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERROR running migration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
