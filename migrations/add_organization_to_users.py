"""
Migration: Add organization column to users table
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
    """Add organization column to users table"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        try:
            # Check if organization column already exists
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'organization'
            """))
            if result.fetchone():
                logger.info("organization column already exists")
                return True

            # Add the organization column
            logger.info("Adding organization column to users table...")
            db.session.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS organization VARCHAR(255)
            """))
            db.session.commit()
            logger.info("Successfully added organization column")

            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
