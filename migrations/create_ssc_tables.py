"""
Create SSC (Scientific and Statistical Committee) tables

Tables:
1. ssc_members - SSC member directory
2. ssc_meetings - SSC meeting schedule and details
3. ssc_recommendations - SSC recommendations to the Council
4. ssc_council_connections - Links SSC recommendations to Council actions
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app import app, db

def run_migration():
    """Create SSC tables"""

    # 1. SSC Members Table
    db.session.execute(text("""
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
    """))

    # 2. SSC Meetings Table
    db.session.execute(text("""
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
    """))

    # 3. SSC Meeting Attendees (many-to-many)
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS ssc_meeting_attendees (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            meeting_id UUID REFERENCES ssc_meetings(id) ON DELETE CASCADE,
            member_id UUID REFERENCES ssc_members(id) ON DELETE CASCADE,
            attended BOOLEAN DEFAULT TRUE,
            role VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(meeting_id, member_id)
        )
    """))

    # 4. SSC Recommendations Table
    db.session.execute(text("""
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
    """))

    # 5. SSC-Council Connections (links SSC recommendations to Council actions)
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS ssc_council_connections (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ssc_recommendation_id UUID REFERENCES ssc_recommendations(id) ON DELETE CASCADE,
            council_meeting_id UUID REFERENCES meetings(id) ON DELETE SET NULL,
            action_id UUID REFERENCES actions(id) ON DELETE SET NULL,
            connection_type VARCHAR(100),
            influence_level VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ssc_recommendation_id, council_meeting_id)
        )
    """))

    # 6. SSC Documents Table (agendas, reports, presentations)
    db.session.execute(text("""
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
    """))

    # Create indexes for performance
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_ssc_meetings_date ON ssc_meetings(meeting_date_start DESC)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_ssc_recommendations_meeting ON ssc_recommendations(meeting_id)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_ssc_recommendations_species ON ssc_recommendations USING GIN(species)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_ssc_connections_recommendation ON ssc_council_connections(ssc_recommendation_id)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_ssc_connections_action ON ssc_council_connections(action_id)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_ssc_members_active ON ssc_members(is_active)"))

    db.session.commit()
    print("✅ SSC tables created successfully")

if __name__ == '__main__':
    with app.app_context():
        run_migration()
