"""Create contacts and organizations tables

Run this with: python migrations/create_contacts_and_orgs.py
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/safmc_fmp_tracker')

def upgrade():
    """Create contacts and organizations tables"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Create organizations table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS organizations (
                id SERIAL PRIMARY KEY,
                org_id VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(500) NOT NULL,
                name_normalized VARCHAR(500),
                acronym VARCHAR(50),
                org_type VARCHAR(100),
                email VARCHAR(200),
                phone VARCHAR(50),
                website VARCHAR(500),
                city VARCHAR(200),
                state VARCHAR(50),
                zip_code VARCHAR(20),
                address TEXT,
                description TEXT,
                sectors JSONB,
                total_comments INTEGER DEFAULT 0,
                total_members_active INTEGER DEFAULT 0,
                first_engagement_date TIMESTAMP,
                last_engagement_date TIMESTAMP,
                data_source VARCHAR(300),
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # Create indexes for organizations
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_organizations_org_id ON organizations(org_id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_organizations_name ON organizations(name);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_organizations_name_normalized ON organizations(name_normalized);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_organizations_state ON organizations(state);
        """))

        # Create contacts table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS contacts (
                id SERIAL PRIMARY KEY,
                contact_id VARCHAR(100) UNIQUE NOT NULL,
                first_name VARCHAR(200),
                last_name VARCHAR(200),
                full_name VARCHAR(400),
                email VARCHAR(200),
                phone VARCHAR(50),
                city VARCHAR(200),
                state VARCHAR(50),
                zip_code VARCHAR(20),
                address TEXT,
                organization_id INTEGER REFERENCES organizations(id),
                title VARCHAR(200),
                sector VARCHAR(100),
                total_comments INTEGER DEFAULT 0,
                total_meetings_attended INTEGER DEFAULT 0,
                first_engagement_date TIMESTAMP,
                last_engagement_date TIMESTAMP,
                data_source VARCHAR(300),
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # Create indexes for contacts
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_contacts_contact_id ON contacts(contact_id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_contacts_full_name ON contacts(full_name);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_contacts_state ON contacts(state);
        """))

        conn.commit()
        print("✓ Organizations and contacts tables created successfully")

        # Add foreign keys to comments table
        # Check if columns exist first
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'comments'
            AND column_name IN ('contact_id', 'organization_id');
        """))
        existing_cols = [row[0] for row in result.fetchall()]

        if 'contact_id' not in existing_cols:
            conn.execute(text("""
                ALTER TABLE comments
                ADD COLUMN contact_id INTEGER REFERENCES contacts(id);
            """))
            print("✓ Added contact_id column to comments")

        if 'organization_id' not in existing_cols:
            conn.execute(text("""
                ALTER TABLE comments
                ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
            """))
            print("✓ Added organization_id column to comments")

        conn.commit()
        print("✓ All migrations completed successfully")

def downgrade():
    """Drop contacts and organizations tables"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Drop foreign key columns from comments first
        conn.execute(text("""
            ALTER TABLE comments
            DROP COLUMN IF EXISTS contact_id,
            DROP COLUMN IF EXISTS organization_id;
        """))

        # Drop tables
        conn.execute(text("DROP TABLE IF EXISTS contacts CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS organizations CASCADE;"))
        conn.commit()
        print("✓ Contacts and organizations tables dropped successfully")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--down', action='store_true', help='Run downgrade')
    args = parser.parse_args()

    if args.down:
        downgrade()
    else:
        upgrade()
