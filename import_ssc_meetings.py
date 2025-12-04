"""
Import SSC Meetings from safmc.net
Run this to populate the database with historical SSC meeting data
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Verify DATABASE_URL is set
if not os.getenv('DATABASE_URL'):
    print("❌ ERROR: DATABASE_URL environment variable must be set")
    print("Example:")
    print('export DATABASE_URL="postgresql://safmc_fmp_user:PASSWORD@dpg-d44eeo3uibrs73a2nkhg-a.oregon-postgres.render.com/safmc_fmp_tracker"')
    sys.exit(1)

from app import app
from src.services.ssc_import_service import SSCImportService

def main():
    """Import all SSC meetings"""
    with app.app_context():
        print("\n" + "="*60)
        print("SSC MEETING IMPORT")
        print("="*60)
        print("\nThis will:")
        print("  1. Scrape all SSC meetings from safmc.net")
        print("  2. Download meeting documents (agendas, briefing books, reports)")
        print("  3. Extract and store SSC recommendations")
        print("  4. Parse document content for analysis")
        print("\n⚠️  This may take several minutes...\n")

        try:
            service = SSCImportService()
            stats = service.import_all_meetings(download_documents=True)

            print("\n" + "="*60)
            print("IMPORT COMPLETE")
            print("="*60)
            print(f"\n✅ Meetings created:        {stats['meetings_created']}")
            print(f"✅ Meetings updated:        {stats['meetings_updated']}")
            print(f"✅ Documents created:       {stats['documents_created']}")
            print(f"✅ Recommendations created: {stats['recommendations_created']}")

            if stats['errors'] > 0:
                print(f"⚠️  Errors encountered:      {stats['errors']}")

            print("\nYou can now view SSC meetings at:")
            print("  https://safmc-fmp-tracker.onrender.com/ssc/meetings")
            print("  https://safmc-fmp-tracker.onrender.com/ssc/recommendations")
            print()

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
