"""
Migration: Add refresh_token columns to users table
Run this to enable persistent sessions with refresh tokens
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
    """Add refresh_token and refresh_token_expiry columns to users table"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        try:
            # Check if refresh_token column already exists
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'refresh_token'
            """))
            if result.fetchone():
                logger.info("refresh_token column already exists")
            else:
                # Add the refresh_token column
                logger.info("Adding refresh_token column to users table...")
                db.session.execute(text("""
                    ALTER TABLE users
                    ADD COLUMN IF NOT EXISTS refresh_token VARCHAR(255)
                """))
                db.session.commit()
                logger.info("Successfully added refresh_token column")

                # Create index for faster lookups
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_refresh_token
                    ON users (refresh_token)
                    WHERE refresh_token IS NOT NULL
                """))
                db.session.commit()
                logger.info("Successfully created index on refresh_token")

            # Check if refresh_token_expiry column already exists
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'refresh_token_expiry'
            """))
            if result.fetchone():
                logger.info("refresh_token_expiry column already exists")
            else:
                # Add the refresh_token_expiry column
                logger.info("Adding refresh_token_expiry column to users table...")
                db.session.execute(text("""
                    ALTER TABLE users
                    ADD COLUMN IF NOT EXISTS refresh_token_expiry TIMESTAMP
                """))
                db.session.commit()
                logger.info("Successfully added refresh_token_expiry column")

            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
