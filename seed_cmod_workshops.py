"""
Seed CMOD Workshop Data
Initial data for Council Member Ongoing Development workshops
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if not os.getenv('DATABASE_URL'):
    print("❌ ERROR: DATABASE_URL environment variable must be set")
    sys.exit(1)

from app import app, db
from src.models.cmod import CMODWorkshop, CMODSession, CMODDocument

# CMOD Workshop data
CMOD_WORKSHOPS = [
    {
        'year': 2022,
        'title': 'Council Member Ongoing Development Workshop 2022',
        'theme': 'New Approaches to Ecosystem-Based Fishery Management (EBFM) and Ecosystem Approaches to Fishery Management (EAFM)',
        'description': 'Inaugural CMOD workshop exploring ecosystem-based approaches to fishery management across all eight Regional Fishery Management Councils.',
        'start_date': date(2022, 11, 15),
        'end_date': date(2022, 11, 16),
        'location': 'Denver, Colorado',
        'host_council': 'New England Fishery Management Council',
        'focus_areas': ['EBFM', 'EAFM', 'Ecosystem Integration', 'Adaptive Management'],
        'skills_components': ['Crafting Effective Motions'],
        'status': 'completed',
        'materials_url': 'https://www.fisherycouncils.org/cmod-workshops/2022',
        'participating_councils': [
            'New England', 'Mid-Atlantic', 'South Atlantic', 'Gulf of Mexico',
            'Caribbean', 'Pacific', 'North Pacific', 'Western Pacific'
        ],
        'key_outcomes': {
            'day1': 'Regional ecosystem presentations and integration approaches',
            'day2': 'Climate disruptions and adaptive management strategies'
        },
        'recommendations': [
            'Incorporate ecosystem data into single-species management',
            'Develop larger implementation frameworks across councils',
            'Address climate change through scenario planning'
        ],
        'sessions': [
            {
                'title': 'Regional EBFM/EAFM Overviews',
                'description': 'Eight regional fishery councils presented ecosystem-based approaches',
                'session_type': 'Presentation',
                'session_date': date(2022, 11, 15),
                'session_order': 1,
                'topics': ['EBFM', 'EAFM', 'Regional Approaches'],
                'councils_presented': ['All Eight Councils']
            },
            {
                'title': 'Ecosystem Data Integration',
                'description': 'Incorporating ecosystem data into single-species management',
                'session_type': 'Presentation',
                'session_date': date(2022, 11, 15),
                'session_order': 2,
                'topics': ['Ecosystem Data', 'Single-Species Management'],
                'speakers': [
                    {'name': 'Sarah Gaichas', 'affiliation': 'NMFS Northeast', 'role': 'Scientist'}
                ]
            },
            {
                'title': 'Ecosystem Disruptions and Adaptive Management',
                'description': 'Red tide, whale entanglement, species distribution shifts',
                'session_type': 'Discussion',
                'session_date': date(2022, 11, 16),
                'session_order': 3,
                'topics': ['Climate Change', 'Ecosystem Disruption', 'Adaptive Management'],
                'speakers': [
                    {'name': 'Ebett Siddon', 'affiliation': 'NMFS Alaska', 'role': 'Scientist'},
                    {'name': 'Mandy Karnauskas', 'affiliation': 'NMFS Southeast', 'role': 'Scientist'}
                ]
            },
            {
                'title': 'Crafting Effective Motions',
                'description': 'Skills training on effective motion drafting',
                'session_type': 'Skills Training',
                'session_date': date(2022, 11, 16),
                'session_order': 4,
                'topics': ['Motion Crafting', 'Council Procedures']
            }
        ]
    },
    {
        'year': 2025,
        'title': 'Council Member Ongoing Development Workshop 2025',
        'theme': 'Understanding Climate-Related Vulnerabilities, Risks, and Uncertainties',
        'description': 'Second CMOD workshop focused on climate resilience, risk assessment, and adaptive capacity in fisheries management.',
        'start_date': date(2025, 4, 30),
        'end_date': date(2025, 5, 1),
        'location': 'Vancouver, Washington',
        'host_council': 'North Pacific Fishery Management Council',
        'focus_areas': ['Climate Change', 'Risk Assessment', 'Adaptive Management', 'Harvest Control Rules'],
        'skills_components': ['Risk Communication', 'Science Communication'],
        'status': 'completed',
        'materials_url': 'https://www.fisherycouncils.org/cmod-workshops/2025',
        'participating_councils': [
            'New England', 'Mid-Atlantic', 'South Atlantic', 'Gulf of Mexico',
            'Caribbean', 'Pacific', 'North Pacific', 'Western Pacific'
        ],
        'key_outcomes': {
            'climate_frameworks': 'Harvest control rules and climate resilience strategies',
            'case_studies': 'Snow crab, winter flounder, black sea bass dynamics',
            'adaptive_capacity': 'Governance challenges and flexibility approaches'
        },
        'recommendations': [
            'Develop climate-resilient harvest control rules',
            'Improve risk assessment frameworks',
            'Enhance adaptive management capacity',
            'Strengthen science communication on uncertainty'
        ],
        'sessions': [
            {
                'title': 'Climate Resilience and Harvest Control Rules',
                'description': 'Risk assessment approaches from multiple councils',
                'session_type': 'Presentation',
                'session_date': date(2025, 4, 30),
                'session_order': 1,
                'topics': ['Climate Resilience', 'Harvest Control Rules', 'Risk Assessment'],
                'councils_presented': ['North Pacific', 'Western Pacific', 'New England', 'Mid-Atlantic'],
                'speakers': [
                    {'name': 'Diana Stram', 'affiliation': 'NPFMC', 'role': 'Staff'},
                    {'name': 'Brandon Muffley', 'affiliation': 'MAFMC', 'role': 'Staff'}
                ]
            },
            {
                'title': 'Climate Change Case Studies',
                'description': 'Snow crab population changes, winter flounder, black sea bass',
                'session_type': 'Panel',
                'session_date': date(2025, 4, 30),
                'session_order': 2,
                'topics': ['Snow Crab', 'Winter Flounder', 'Black Sea Bass', 'Climate Impacts'],
                'key_takeaways': [
                    'Population dynamics shifting with climate',
                    'Need for flexible management approaches',
                    'Importance of monitoring and early detection'
                ]
            },
            {
                'title': 'Adaptive Management and Governance',
                'description': 'East Coast representation challenges and North Pacific flexibility',
                'session_type': 'Discussion',
                'session_date': date(2025, 5, 1),
                'session_order': 3,
                'topics': ['Adaptive Management', 'Governance', 'Flexibility'],
                'speakers': [
                    {'name': 'Dan Salerno', 'affiliation': 'NEFMC', 'role': 'Staff'}
                ]
            },
            {
                'title': 'Communicating Risk and Uncertainty',
                'description': 'COMPASS training on science communication',
                'session_type': 'Skills Training',
                'session_date': date(2025, 5, 1),
                'session_order': 4,
                'topics': ['Risk Communication', 'Science Communication', 'Uncertainty'],
                'speakers': [
                    {'name': 'Sarah Sunu', 'affiliation': 'COMPASS', 'role': 'Communications Expert'}
                ]
            }
        ]
    },
    {
        'year': 2026,
        'title': 'Council Member Ongoing Development Workshop 2026 (Proposed)',
        'theme': 'Improving US Seafood Competitiveness: Flexibility, Stability, and Adaptation',
        'description': 'Proposed CMOD workshop focusing on US seafood industry competitiveness, market stability, and adaptive capacity.',
        'start_date': date(2026, 10, 1),  # Placeholder date
        'end_date': date(2026, 10, 2),
        'location': 'TBD',
        'host_council': 'TBD',
        'focus_areas': ['Seafood Competitiveness', 'Market Stability', 'Flexibility', 'Adaptation'],
        'skills_components': ['TBD'],
        'status': 'scheduled',
        'materials_url': 'https://static1.squarespace.com/static/56c65ea3f2b77e3a78d3441e/t/68e94dd03c8c4f74d61b0acc/1760120275009/12.+CMOD+Update+-+CCC+Oct+2025.pdf',
        'participating_councils': [],
        'recommendations': []
    }
]


def seed_cmod_workshops():
    """Seed CMOD workshop data"""
    with app.app_context():
        try:
            print("\n" + "="*60)
            print("SEEDING CMOD WORKSHOPS")
            print("="*60)

            for workshop_data in CMOD_WORKSHOPS:
                print(f"\nProcessing: {workshop_data['title']}")

                # Check if workshop already exists
                existing = CMODWorkshop.query.filter_by(
                    year=workshop_data['year']
                ).first()

                if existing:
                    print(f"  ⚠️  {workshop_data['year']} workshop already exists, skipping...")
                    continue

                # Extract sessions data
                sessions_data = workshop_data.pop('sessions', [])

                # Create workshop
                workshop = CMODWorkshop(**workshop_data)
                db.session.add(workshop)
                db.session.flush()  # Get workshop ID

                print(f"  ✓ Created workshop: {workshop.title}")

                # Add sessions
                for session_data in sessions_data:
                    session = CMODSession(
                        workshop_id=workshop.id,
                        **session_data
                    )
                    db.session.add(session)
                    print(f"    ✓ Added session: {session.title}")

            db.session.commit()

            # Summary
            total = CMODWorkshop.query.count()
            print("\n" + "="*60)
            print(f"✅ CMOD SEEDING COMPLETE")
            print("="*60)
            print(f"Total workshops in database: {total}")
            print()

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    seed_cmod_workshops()
