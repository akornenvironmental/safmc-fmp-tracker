"""
Create SSC tables directly on production database
"""
import psycopg2

DATABASE_URL = "postgresql://safmc_user:SvMkI8VcP70Xjpm3YkfzAMNxURAhwZ0n@dpg-d3tpj9hbh1hs73alm8m0-a.oregon-postgres.render.com/safmc_interviews"

def create_ssc_tables():
    """Create SSC tables"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("Creating SSC tables...")

        # 1. SSC Members Table
        print("1. Creating ssc_members table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ssc_members (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                state VARCHAR(2),
                seat_type VARCHAR(100),
                expertise_area VARCHAR(255),
                affiliation VARCHAR(500),
                email VARCHAR(255),
                phone VARCHAR(50),
                is_chair BOOLEAN DEFAULT FALSE,
                is_vice_chair BOOLEAN DEFAULT FALSE,
                term_start DATE,
                term_end DATE,
                is_active BOOLEAN DEFAULT TRUE,
                bio TEXT,
                publications TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. SSC Meetings Table
        print("2. Creating ssc_meetings table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ssc_meetings (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR(500) NOT NULL,
                meeting_date_start TIMESTAMP NOT NULL,
                meeting_date_end TIMESTAMP,
                location VARCHAR(500),
                is_virtual BOOLEAN DEFAULT FALSE,
                meeting_type VARCHAR(100),
                status VARCHAR(50) DEFAULT 'scheduled',
                agenda_url TEXT,
                briefing_book_url TEXT,
                report_url TEXT,
                webinar_link TEXT,
                description TEXT,
                topics TEXT[],
                species_discussed TEXT[],
                attendance_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. SSC Meeting Attendees
        print("3. Creating ssc_meeting_attendees table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ssc_meeting_attendees (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                meeting_id UUID REFERENCES ssc_meetings(id) ON DELETE CASCADE,
                member_id UUID REFERENCES ssc_members(id) ON DELETE CASCADE,
                attended BOOLEAN DEFAULT TRUE,
                role VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(meeting_id, member_id)
            )
        """)

        # 4. SSC Recommendations Table
        print("4. Creating ssc_recommendations table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ssc_recommendations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                meeting_id UUID REFERENCES ssc_meetings(id) ON DELETE SET NULL,
                recommendation_number VARCHAR(50),
                title VARCHAR(500) NOT NULL,
                recommendation_text TEXT NOT NULL,
                recommendation_type VARCHAR(100),
                species TEXT[],
                fmp VARCHAR(255),
                topic VARCHAR(255),
                abc_value DECIMAL(15,2),
                abc_units VARCHAR(50),
                overfishing_limit DECIMAL(15,2),
                status VARCHAR(50) DEFAULT 'pending',
                council_response TEXT,
                council_action_taken VARCHAR(255),
                implementation_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 5. SSC-Council Connections
        print("5. Creating ssc_council_connections table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ssc_council_connections (
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

        # 6. SSC Documents Table
        print("6. Creating ssc_documents table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ssc_documents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                meeting_id UUID REFERENCES ssc_meetings(id) ON DELETE CASCADE,
                document_type VARCHAR(100) NOT NULL,
                title VARCHAR(500) NOT NULL,
                url TEXT NOT NULL,
                file_size VARCHAR(50),
                upload_date DATE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        print("7. Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ssc_meetings_date ON ssc_meetings(meeting_date_start DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ssc_recommendations_meeting ON ssc_recommendations(meeting_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ssc_recommendations_species ON ssc_recommendations USING GIN(species)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ssc_connections_recommendation ON ssc_council_connections(ssc_recommendation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ssc_connections_action ON ssc_council_connections(action_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ssc_members_active ON ssc_members(is_active)")

        conn.commit()
        print("\n✅ SSC tables created successfully!")

        # Verify tables were created
        print("\nVerifying tables...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name LIKE 'ssc_%'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        for table in tables:
            print(f"  ✓ {table[0]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_ssc_tables()
