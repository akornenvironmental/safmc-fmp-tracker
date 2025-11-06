"""
Create stock assessment tables for SAFMC FMP Tracker
Run this on Render to set up the database schema
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_tables():
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False

    try:
        conn = psycopg2.connect(database_url, sslmode='require')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("Creating stock_assessments table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_assessments (
                id SERIAL PRIMARY KEY,
                sedar_number VARCHAR(50),
                species VARCHAR(255) NOT NULL,
                scientific_name VARCHAR(255),
                stock_name VARCHAR(255),
                assessment_type VARCHAR(100),
                status VARCHAR(50),
                start_date DATE,
                completion_date DATE,
                stock_status VARCHAR(100),
                overfishing_occurring BOOLEAN DEFAULT FALSE,
                overfished BOOLEAN DEFAULT FALSE,
                biomass_current DECIMAL(15, 2),
                biomass_msy DECIMAL(15, 2),
                fishing_mortality_current DECIMAL(10, 4),
                fishing_mortality_msy DECIMAL(10, 4),
                overfishing_limit DECIMAL(15, 2),
                acceptable_biological_catch DECIMAL(15, 2),
                annual_catch_limit DECIMAL(15, 2),
                keywords TEXT[],
                fmps_affected TEXT[],
                source_url TEXT,
                document_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✓ stock_assessments table created")

        print("Creating assessment_comments table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessment_comments (
                id SERIAL PRIMARY KEY,
                assessment_id INTEGER REFERENCES stock_assessments(id) ON DELETE CASCADE,
                commenter_name VARCHAR(255),
                organization VARCHAR(255),
                comment_date DATE,
                comment_type VARCHAR(100),
                comment_text TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✓ assessment_comments table created")

        print("Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stock_assessments_species ON stock_assessments(species);
            CREATE INDEX IF NOT EXISTS idx_stock_assessments_sedar ON stock_assessments(sedar_number);
            CREATE INDEX IF NOT EXISTS idx_stock_assessments_status ON stock_assessments(status);
            CREATE INDEX IF NOT EXISTS idx_stock_assessments_updated ON stock_assessments(updated_at);
            CREATE INDEX IF NOT EXISTS idx_assessment_comments_assessment ON assessment_comments(assessment_id);
        """)
        print("✓ Indexes created")

        cursor.close()
        conn.close()

        print("\n✅ Stock assessment tables created successfully!")
        return True

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    create_tables()
