"""
Seed SSC members data into production database
"""
import psycopg2
from datetime import date

DATABASE_URL = "postgresql://safmc_user:SvMkI8VcP70Xjpm3YkfzAMNxURAhwZ0n@dpg-d3tpj9hbh1hs73alm8m0-a.oregon-postgres.render.com/safmc_interviews"

# SSC Members from safmc.net
SSC_MEMBERS = [
    {
        "name": "Dr. Marcel Reichert",
        "state": "SC",
        "seat_type": "At-large",
        "is_chair": True,
        "is_vice_chair": False,
        "expertise_area": "Marine Biology, Stock Assessment",
        "is_active": True
    },
    {
        "name": "Dr. Walter Bubley",
        "state": "SC",
        "seat_type": "State-designated",
        "is_chair": False,
        "is_vice_chair": True,
        "expertise_area": "Fisheries Science",
        "is_active": True
    },
    {
        "name": "Dr. Jeff Buckel",
        "state": "NC",
        "seat_type": "At-large",
        "expertise_area": "Fish Ecology",
        "is_chair": False,
        "is_vice_chair": False,
        "is_active": True
    },
    {
        "name": "Dr. Jie Cao",
        "state": "NC",
        "seat_type": "At-large",
        "expertise_area": "Statistics, Population Dynamics",
        "is_active": True
    },
    {
        "name": "Dr. Luiz Barbieri",
        "state": "FL",
        "seat_type": "State-designated",
        "expertise_area": "Fish Population Dynamics",
        "is_active": True
    },
    {
        "name": "Dr. Chris Dumas",
        "state": "NC",
        "seat_type": "Economist",
        "expertise_area": "Fisheries Economics",
        "is_active": True
    },
    {
        "name": "Dr. Jared Flowers",
        "state": "GA",
        "seat_type": "State-designated",
        "expertise_area": "Fisheries Management",
        "is_active": True
    },
    {
        "name": "Dr. James Gartland",
        "state": "VA",
        "seat_type": "At-large",
        "expertise_area": "Stock Assessment",
        "is_active": True
    },
    {
        "name": "Dr. Kai Lorenzen",
        "state": "FL",
        "seat_type": "At-large",
        "expertise_area": "Fisheries Science, Population Dynamics",
        "is_active": True
    },
    {
        "name": "Anne Markwith",
        "state": "NC",
        "seat_type": "State-designated",
        "expertise_area": "Fisheries Management",
        "is_active": True
    },
    {
        "name": "Dr. Genevieve Nesslage",
        "state": "MD",
        "seat_type": "At-large",
        "expertise_area": "Quantitative Fisheries Science",
        "is_active": True
    },
    {
        "name": "Christina Package-Ward",
        "state": "FL",
        "seat_type": "At-large",
        "expertise_area": "Fisheries Management",
        "is_active": True
    },
    {
        "name": "Dr. Kelsey Roberts",
        "state": "MA",
        "seat_type": "At-large",
        "expertise_area": "Fisheries Science",
        "is_active": True
    },
    {
        "name": "Dr. Fred Scharf",
        "state": "NC",
        "seat_type": "At-large",
        "expertise_area": "Fish Ecology, Stock Assessment",
        "is_active": True
    },
    {
        "name": "Dr. Catherine \"CJ\" Schlick",
        "state": "SC",
        "seat_type": "At-large",
        "expertise_area": "Fisheries Biology",
        "is_active": True
    },
    {
        "name": "Dr. Amy Schueller",
        "state": "NC",
        "seat_type": "At-large",
        "expertise_area": "Stock Assessment Modeling",
        "is_active": True
    },
    {
        "name": "Dr. Fred Serchuk",
        "state": "FL",
        "seat_type": "At-large",
        "expertise_area": "Stock Assessment, Fisheries Science",
        "is_active": True
    },
    {
        "name": "Dr. Alexei Sharov",
        "state": "MD",
        "seat_type": "At-large",
        "expertise_area": "Population Dynamics, Stock Assessment",
        "is_active": True
    },
    {
        "name": "Dr. Steve Turner",
        "state": "FL",
        "seat_type": "At-large",
        "expertise_area": "Marine Biology",
        "is_active": True
    },
    {
        "name": "Dr. Jennifer Sweeney-Tookes",
        "state": "GA",
        "seat_type": "Social Scientist",
        "expertise_area": "Social Sciences, Human Dimensions",
        "is_active": True
    },
    {
        "name": "Jason Walsh",
        "state": "NC",
        "seat_type": "Economist",
        "expertise_area": "Fisheries Economics",
        "is_active": True
    }
]

def seed_members():
    """Seed SSC members"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check if members already exist
        cursor.execute("SELECT COUNT(*) FROM ssc_members")
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"⚠️  {count} SSC members already exist. Skipping seed.")
            cursor.close()
            conn.close()
            return

        print("Seeding SSC members...")
        for i, member in enumerate(SSC_MEMBERS, 1):
            # Ensure all members have required fields
            if 'is_chair' not in member:
                member['is_chair'] = False
            if 'is_vice_chair' not in member:
                member['is_vice_chair'] = False

            cursor.execute("""
                INSERT INTO ssc_members (
                    name, state, seat_type, expertise_area,
                    is_chair, is_vice_chair, is_active
                ) VALUES (
                    %(name)s, %(state)s, %(seat_type)s, %(expertise_area)s,
                    %(is_chair)s, %(is_vice_chair)s, %(is_active)s
                )
            """, member)
            print(f"  {i}. {member['name']} ({member['seat_type']})")

        conn.commit()
        print(f"\n✅ Successfully seeded {len(SSC_MEMBERS)} SSC members!")

        # Display seeded members
        print("\n" + "="*60)
        print("SSC MEMBERS:")
        print("="*60)
        cursor.execute("""
            SELECT name, state, seat_type, expertise_area, is_chair, is_vice_chair
            FROM ssc_members
            ORDER BY is_chair DESC, is_vice_chair DESC, name
        """)
        members = cursor.fetchall()
        for member in members:
            name, state, seat_type, expertise, is_chair, is_vice_chair = member
            role = ""
            if is_chair:
                role = " 👑 CHAIR"
            elif is_vice_chair:
                role = " 🎖️  VICE-CHAIR"
            print(f"{name} ({state}){role}")
            print(f"  {seat_type} | {expertise}")
            print()

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    seed_members()
