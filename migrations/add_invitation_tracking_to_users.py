"""
Migration: Add invitation tracking fields to users table
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.config.extensions import db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Add invitation tracking fields to users table"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        try:
            # Check if invitation_status column already exists
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'invitation_status'
            """))
            if result.fetchone():
                logger.info("invitation_status column already exists")
                return True

            logger.info("Adding invitation tracking fields to users table...")

            # Create invitation_status enum type if it doesn't exist
            db.session.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE invitation_status AS ENUM ('pending', 'accepted');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))

            # Add invitation_status column
            db.session.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS invitation_status invitation_status DEFAULT 'pending'
            """))

            # Add invitation_accepted_at column
            db.session.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS invitation_accepted_at TIMESTAMP
            """))

            db.session.commit()
            logger.info("Successfully added invitation tracking fields")

            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
