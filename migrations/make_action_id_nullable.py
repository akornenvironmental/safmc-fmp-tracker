"""Make action_id nullable in comments table

General public comments don't need to be linked to specific actions.

Run this with: python migrations/make_action_id_nullable.py
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
    """Make action_id nullable in comments table"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Make action_id nullable
        conn.execute(text("""
            ALTER TABLE comments
            ALTER COLUMN action_id DROP NOT NULL;
        """))

        conn.commit()
        print("✓ Made action_id nullable in comments table")

def downgrade():
    """Make action_id NOT NULL again (be careful - this will fail if NULL values exist)"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Make action_id NOT NULL again
        conn.execute(text("""
            ALTER TABLE comments
            ALTER COLUMN action_id SET NOT NULL;
        """))

        conn.commit()
        print("✓ Made action_id NOT NULL in comments table")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--down', action='store_true', help='Run downgrade')
    args = parser.parse_args()

    if args.down:
        downgrade()
    else:
        upgrade()
