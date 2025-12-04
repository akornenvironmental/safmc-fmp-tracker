"""
Seed SSC members into production database
Run with: DATABASE_URL="postgresql://..." python3 seed_ssc_members_production.py
"""
import os
import sys
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Verify DATABASE_URL is set
if not os.getenv('DATABASE_URL'):
    print("❌ ERROR: DATABASE_URL environment variable must be set")
    print("Example:")
    print('export DATABASE_URL="postgresql://safmc_fmp_user:PASSWORD@dpg-d44eeo3uibrs73a2nkhg-a.oregon-postgres.render.com/safmc_fmp_tracker"')
    sys.exit(1)

from app import app, db
from src.models.ssc import SSCMember

# SSC Members from safmc.net
SSC_MEMBERS = [
    {
        "name": "Dr. Marcel Reichert",
        "state": "SC",
        "seat_type": "At-large",
        "is_chair": True,
        "expertise_area": "Fisheries Biology",
        "affiliation": "South Carolina Department of Natural Resources - Marine Resources Research Institute"
    },
    {
        "name": "Dr. Walter Bubley",
        "state": "SC",
        "seat_type": "State-designated",
        "is_vice_chair": True,
        "expertise_area": "Fisheries Science",
        "affiliation": "South Carolina Department of Natural Resources"
    },
    {
        "name": "Dr. Jennifer Potts",
        "state": "FL",
        "seat_type": "At-large",
        "expertise_area": "Stock Assessment",
        "affiliation": "NOAA Fisheries - Southeast Fisheries Science Center"
    },
    {
        "name": "Dr. Yan Li",
        "state": "NC",
        "seat_type": "At-large",
        "expertise_area": "Stock Assessment",
        "affiliation": "NOAA Fisheries - Southeast Fisheries Science Center"
    },
    {
        "name": "Dr. Erik Williams",
        "state": "FL",
        "seat_type": "At-large",
        "expertise_area": "Fisheries Biology",
        "affiliation": "NOAA Fisheries - Southeast Fisheries Science Center"
    },
    {
        "name": "Dr. Alexei Sharov",
        "state": "MD",
        "seat_type": "At-large",
        "expertise_area": "Stock Assessment",
        "affiliation": "Maryland Department of Natural Resources"
    },
    {
        "name": "Dr. Amy Schueller",
        "state": "NC",
        "seat_type": "At-large",
        "expertise_area": "Stock Assessment",
        "affiliation": "NOAA Fisheries - Southeast Fisheries Science Center"
    },
    {
        "name": "Dr. Genny Nesslage",
        "state": "MD",
        "seat_type": "At-large",
        "expertise_area": "Fisheries Science",
        "affiliation": "University of Maryland Center for Environmental Science"
    },
    {
        "name": "Dr. Jeff Buckel",
        "state": "NC",
        "seat_type": "At-large",
        "expertise_area": "Fisheries Ecology",
        "affiliation": "North Carolina State University"
    },
    {
        "name": "Dr. Joe Ballenger",
        "state": "SC",
        "seat_type": "State-designated",
        "expertise_area": "Fisheries Science",
        "affiliation": "South Carolina Department of Natural Resources"
    },
    {
        "name": "Dr. Chip Collier",
        "state": "FL",
        "seat_type": "State-designated",
        "expertise_area": "Fisheries Biology",
        "affiliation": "Florida Fish and Wildlife Conservation Commission"
    },
    {
        "name": "Dr. Mike Errigo",
        "state": "FL",
        "seat_type": "State-designated",
        "expertise_area": "Stock Assessment",
        "affiliation": "Florida Fish and Wildlife Conservation Commission"
    },
    {
        "name": "Dr. Jeff Buckel",
        "state": "NC",
        "seat_type": "State-designated",
        "expertise_area": "Fisheries Ecology",
        "affiliation": "North Carolina State University"
    },
    {
        "name": "Dr. Kyle Shertzer",
        "state": "NC",
        "seat_type": "At-large",
        "expertise_area": "Population Dynamics",
        "affiliation": "NOAA Fisheries - Southeast Fisheries Science Center"
    },
    {
        "name": "Dr. Skyler Sagarese",
        "state": "FL",
        "seat_type": "At-large",
        "expertise_area": "Ecosystem Modeling",
        "affiliation": "NOAA Fisheries - Southeast Fisheries Science Center"
    },
    {
        "name": "Dr. Fred Serchuk",
        "state": "MD",
        "seat_type": "At-large",
        "expertise_area": "Stock Assessment",
        "affiliation": "Retired - NOAA Fisheries"
    },
    {
        "name": "Dr. Viviane Zeidemann",
        "state": "FL",
        "seat_type": "At-large",
        "expertise_area": "Social Sciences",
        "affiliation": "NOAA Fisheries"
    },
    {
        "name": "Dr. Omid Karbassioon",
        "state": "FL",
        "seat_type": "Economist",
        "expertise_area": "Fisheries Economics",
        "affiliation": "ECS Federal in support of NOAA Fisheries"
    },
    {
        "name": "Dr. John Whitehead",
        "state": "NC",
        "seat_type": "Economist",
        "expertise_area": "Environmental Economics",
        "affiliation": "Appalachian State University"
    },
    {
        "name": "Dr. Chris Dumas",
        "state": "NC",
        "seat_type": "Economist",
        "expertise_area": "Environmental Economics",
        "affiliation": "University of North Carolina Wilmington"
    },
    {
        "name": "Dr. Tracey Yandle",
        "state": "FL",
        "seat_type": "Social Scientist",
        "expertise_area": "Fisheries Social Sciences",
        "affiliation": "Emory University"
    }
]

def seed_ssc_members():
    """Seed SSC members"""
    with app.app_context():
        try:
            print("Seeding SSC members...")

            # Check if members already exist
            existing_count = db.session.query(SSCMember).count()
            if existing_count > 0:
                print(f"⚠️  {existing_count} SSC members already exist. Skipping seed.")
                return

            # Add all members
            for member_data in SSC_MEMBERS:
                member = SSCMember(**member_data)
                db.session.add(member)

            db.session.commit()
            print(f"\n✅ Successfully seeded {len(SSC_MEMBERS)} SSC members!")

            # Verify
            total_count = db.session.query(SSCMember).count()
            chair_count = db.session.query(SSCMember).filter_by(is_chair=True).count()
            vice_chair_count = db.session.query(SSCMember).filter_by(is_vice_chair=True).count()

            print(f"\nSummary:")
            print(f"  Total members: {total_count}")
            print(f"  Chair: {chair_count}")
            print(f"  Vice-Chair: {vice_chair_count}")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    seed_ssc_members()
