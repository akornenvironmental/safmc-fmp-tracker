"""
Fix SSC Council Connections table - remove invalid foreign keys
"""
import psycopg2
import os

# Get DATABASE_URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://safmc_fmp_user:password@host/safmc_fmp_tracker')

def fix_ssc_foreign_keys():
    """Drop invalid foreign key constraints from ssc_council_connections"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("Fixing SSC council connections table...")

        # Drop the table if it exists and recreate without foreign keys to meetings/actions
        print("1. Dropping ssc_council_connections table...")
        cursor.execute("DROP TABLE IF EXISTS ssc_council_connections CASCADE")

        # Recreate table without foreign keys to meetings/actions
        print("2. Recreating ssc_council_connections table...")
        cursor.execute("""
            CREATE TABLE ssc_council_connections (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                ssc_recommendation_id UUID REFERENCES ssc_recommendations(id) ON DELETE CASCADE,
                council_meeting_id UUID,
                action_id UUID,
                connection_type VARCHAR(100),
                influence_level VARCHAR(50),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Recreate indexes
        print("3. Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ssc_connections_recommendation ON ssc_council_connections(ssc_recommendation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ssc_connections_council_meeting ON ssc_council_connections(council_meeting_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ssc_connections_action ON ssc_council_connections(action_id)")

        conn.commit()
        print("\n✅ SSC council connections table fixed successfully!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_ssc_foreign_keys()
