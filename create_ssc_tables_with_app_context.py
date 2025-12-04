"""
Create SSC tables using Flask app context (manual db.create_all())
Run this locally with DATABASE_URL set to production database
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set DATABASE_URL before importing app
if not os.getenv('DATABASE_URL'):
    print("❌ ERROR: DATABASE_URL environment variable must be set")
    print("Example:")
    print('export DATABASE_URL="postgresql://safmc_fmp_user:PASSWORD@dpg-d44eeo3uibrs73a2nkhg-a.oregon-postgres.render.com/safmc_fmp_tracker"')
    sys.exit(1)

from app import app, db
from sqlalchemy import text

def create_ssc_tables():
    """Create all tables including SSC tables"""
    with app.app_context():
        try:
            print("Creating database tables...")

            # Create all tables (this will only create missing tables)
            db.create_all()

            print("✅ Tables created successfully!")

            # Verify SSC tables exist
            print("\nVerifying SSC tables...")
            result = db.session.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name LIKE 'ssc_%'
                ORDER BY table_name
            """))

            tables = result.fetchall()
            if tables:
                for table in tables:
                    print(f"  ✓ {table[0]}")
            else:
                print("  ⚠️  No SSC tables found")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    create_ssc_tables()
