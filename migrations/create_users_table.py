"""Create users table migration

Run this with: python migrations/create_users_table.py
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from src.config.extensions import db

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/safmc_fmp_tracker')

def upgrade():
    """Create users table"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Create ENUM type for roles
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE user_roles AS ENUM ('admin', 'editor');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))

        # Create users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(255),
                role user_roles NOT NULL DEFAULT 'editor',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                last_login TIMESTAMP,
                login_token VARCHAR(255),
                token_expiry TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
        """))

        conn.commit()
        print("✓ Users table created successfully")

def downgrade():
    """Drop users table"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users;"))
        conn.execute(text("DROP TYPE IF EXISTS user_roles;"))
        conn.commit()
        print("✓ Users table dropped successfully")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--down', action='store_true', help='Run downgrade')
    args = parser.parse_args()

    if args.down:
        downgrade()
    else:
        upgrade()
