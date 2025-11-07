"""
Create stock_assessments and assessment_comments tables
"""

import psycopg2
import os
from datetime import datetime

def run_migration():
    """Create stock assessments tables"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False

    # Fix Render's postgres:// URL to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        print("🔄 Creating stock_assessments table...")

        # Create stock_assessments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stock_assessments (
                id SERIAL PRIMARY KEY,
                sedar_number VARCHAR(50),
                species VARCHAR(200) NOT NULL,
                scientific_name VARCHAR(200),
                stock_name VARCHAR(300),
                assessment_type VARCHAR(100),
                status VARCHAR(100),
                start_date DATE,
                completion_date DATE,
                stock_status VARCHAR(100),
                overfishing_occurring BOOLEAN DEFAULT FALSE,
                overfished BOOLEAN DEFAULT FALSE,
                biomass_current NUMERIC(12, 3),
                biomass_msy NUMERIC(12, 3),
                fishing_mortality_current NUMERIC(12, 6),
                fishing_mortality_msy NUMERIC(12, 6),
                overfishing_limit NUMERIC(12, 3),
                acceptable_biological_catch NUMERIC(12, 3),
                annual_catch_limit NUMERIC(12, 3),
                keywords TEXT[],
                fmps_affected TEXT[],
                source_url TEXT,
                document_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_scraped TIMESTAMP
            );
        """)

        print("✅ stock_assessments table created")

        # Create assessment_comments table
        print("🔄 Creating assessment_comments table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS assessment_comments (
                id SERIAL PRIMARY KEY,
                assessment_id INTEGER REFERENCES stock_assessments(id) ON DELETE CASCADE,
                commenter_name VARCHAR(300),
                organization VARCHAR(300),
                comment_date DATE,
                comment_type VARCHAR(100),
                comment_text TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        print("✅ assessment_comments table created")

        # Create indices for better performance
        print("🔄 Creating indices...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_assessments_species ON stock_assessments(species);
            CREATE INDEX IF NOT EXISTS idx_assessments_status ON stock_assessments(status);
            CREATE INDEX IF NOT EXISTS idx_assessments_overfished ON stock_assessments(overfished);
            CREATE INDEX IF NOT EXISTS idx_assessments_overfishing ON stock_assessments(overfishing_occurring);
            CREATE INDEX IF NOT EXISTS idx_assessments_completion ON stock_assessments(completion_date);
            CREATE INDEX IF NOT EXISTS idx_assessment_comments_assessment_id ON assessment_comments(assessment_id);
        """)

        print("✅ Indices created")

        conn.commit()
        cur.close()
        conn.close()

        print("✅ Migration completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    run_migration()
