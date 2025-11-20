#!/usr/bin/env python3
"""
Import Workplan - Complete workflow
1. Run migration to create tables
2. Import workplan Excel file
3. Verify data
"""

import os
import sys

# Set DATABASE_URL if not set (for local testing)
if not os.getenv('DATABASE_URL'):
    # You can set this to your production database URL
    print("DATABASE_URL not set. Using local database...")
    os.environ['DATABASE_URL'] = 'postgresql://user:password@localhost:5432/safmc_fmp_tracker'

from app import app, db
from src.models.workplan import WorkplanVersion, WorkplanItem, WorkplanMilestone
from src.services.workplan_service import WorkplanService
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Run the workplan migration SQL"""
    print("\n" + "="*80)
    print("STEP 1: Running Workplan Migration")
    print("="*80)

    migration_file = 'migrations/create_workplan_system.sql'

    try:
        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        with app.app_context():
            # Split by semicolon and execute
            statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

            for statement in statements:
                if statement.startswith('--') or statement.startswith('/*') or not statement:
                    continue

                try:
                    db.session.execute(text(statement))
                    db.session.commit()

                    # Print progress
                    if 'CREATE TABLE' in statement:
                        table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip()
                        if 'IF NOT EXISTS' in statement:
                            table_name = table_name.replace('IF NOT EXISTS', '').strip()
                        print(f"  ✓ Created/verified table: {table_name}")
                    elif 'INSERT INTO' in statement and 'ON CONFLICT' in statement:
                        print(f"  ✓ Inserted/updated reference data")

                except Exception as e:
                    if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                        print(f"  ℹ Already exists (skipping)")
                    else:
                        print(f"  ⚠ Warning: {e}")

        print("\n✅ Migration completed!")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def verify_tables():
    """Verify workplan tables exist"""
    print("\n" + "="*80)
    print("STEP 2: Verifying Tables")
    print("="*80)

    with app.app_context():
        result = db.session.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND (table_name LIKE 'workplan%' OR table_name = 'milestone_types')
            ORDER BY table_name
        """))

        tables = [row[0] for row in result]

        print(f"\nFound {len(tables)} workplan-related tables:")
        for table in tables:
            print(f"  ✓ {table}")

        expected = ['milestone_types', 'workplan_items', 'workplan_milestones',
                    'workplan_upload_log', 'workplan_versions']

        missing = set(expected) - set(tables)
        if missing:
            print(f"\n⚠ Missing tables: {missing}")
            return False

        print("\n✅ All tables verified!")
        return True


def import_workplan_file(file_path, version_name):
    """Import workplan Excel file"""
    print("\n" + "="*80)
    print("STEP 3: Importing Workplan File")
    print("="*80)

    print(f"\nFile: {file_path}")
    print(f"Version: {version_name}")

    if not os.path.exists(file_path):
        print(f"\n❌ File not found: {file_path}")
        return False

    with app.app_context():
        try:
            result = WorkplanService.import_workplan_file(
                file_path=file_path,
                version_name=version_name,
                upload_type='manual_upload',
                source_url='https://safmc.net/events/september-2025-council-meeting/'
            )

            if result['success']:
                print(f"\n✅ Import successful!")
                print(f"  Version ID: {result['version_id']}")
                print(f"  Items created: {result['items_created']}")
                print(f"  Milestones created: {result['milestones_created']}")
                return True
            else:
                print(f"\n❌ Import failed:")
                for error in result.get('errors', []):
                    print(f"  - {error}")
                return False

        except Exception as e:
            print(f"\n❌ Import error: {e}")
            import traceback
            traceback.print_exc()
            return False


def show_summary():
    """Show summary of imported data"""
    print("\n" + "="*80)
    print("STEP 4: Data Summary")
    print("="*80)

    with app.app_context():
        # Get current workplan
        current = WorkplanService.get_current_workplan()

        if not current['version']:
            print("\n⚠ No active workplan found")
            return

        version = current['version']
        items = current['items']

        print(f"\nActive Workplan: {version['versionName']}")
        print(f"Effective Date: {version['effectiveDate']}")
        print(f"Total Items: {len(items)}")

        # Group by status
        by_status = {}
        for item in items:
            status = item['status']
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(item)

        print("\nBreakdown by status:")
        for status in ['UNDERWAY', 'PLANNED', 'COMPLETED', 'DEFERRED']:
            if status in by_status:
                count = len(by_status[status])
                print(f"  {status}: {count} amendments")

        # Show sample items
        print("\nSample amendments (first 5 UNDERWAY):")
        underway = by_status.get('UNDERWAY', [])[:5]
        for item in underway:
            milestone_count = len(item.get('milestones', []))
            print(f"  • {item['amendmentId']}: {item['topic'][:60]}...")
            print(f"    Lead: {item['leadStaff']}, Milestones: {milestone_count}")

        # Check action linkage
        linked = sum(1 for item in items if item.get('actionId'))
        print(f"\nAction Linkage:")
        print(f"  Linked to existing actions: {linked}/{len(items)}")
        print(f"  New actions created: {len(items) - linked}")


def main():
    """Main workflow"""
    print("\n" + "="*80)
    print("SAFMC FMP TRACKER - WORKPLAN IMPORT")
    print("="*80)

    # Configuration
    WORKPLAN_FILE = '/Users/akorn/Desktop/fc2_a1_safmc_workplanq3_202509-xlsx.xlsx'
    VERSION_NAME = 'Q3 2025 - September 2025 Council Meeting'

    # Step 1: Run migration
    if not run_migration():
        print("\n❌ Migration failed. Aborting.")
        sys.exit(1)

    # Step 2: Verify tables
    if not verify_tables():
        print("\n❌ Table verification failed. Aborting.")
        sys.exit(1)

    # Step 3: Import workplan
    if not import_workplan_file(WORKPLAN_FILE, VERSION_NAME):
        print("\n❌ Import failed. Aborting.")
        sys.exit(1)

    # Step 4: Show summary
    show_summary()

    print("\n" + "="*80)
    print("✅ WORKPLAN IMPORT COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("  1. View workplan in database")
    print("  2. Create API endpoints")
    print("  3. Build frontend UI")
    print()


if __name__ == '__main__':
    main()
