"""
Create SSC tables using Flask app context and SQLAlchemy
"""
import os
import sys

# Set up path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from src.models.ssc import SSCMember, SSCMeeting, SSCRecommendation, SSCCouncilConnection, SSCDocument

def create_ssc_tables():
    """Create SSC tables using SQLAlchemy"""
    try:
        with app.app_context():
            print("Creating SSC tables...")

            # Create tables
            print("1. Creating tables...")
            db.create_all()

            print("\n✅ SSC tables created successfully!")

            # Verify tables were created
            print("\nVerifying tables...")
            result = db.session.execute(db.text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name LIKE 'ssc_%'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            for table in tables:
                print(f"  ✓ {table[0]}")

            # Count members
            member_count = db.session.query(SSCMember).count()
            print(f"\nSSC Members count: {member_count}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_ssc_tables()
