"""
Migration: Add is_under_development column to actions table
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
    """Add is_under_development column to actions table"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        try:
            # Check if is_under_development column already exists
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'actions' AND column_name = 'is_under_development'
            """))
            if result.fetchone():
                logger.info("is_under_development column already exists")
                return True

            # Add the is_under_development column
            logger.info("Adding is_under_development column to actions table...")
            db.session.execute(text("""
                ALTER TABLE actions
                ADD COLUMN IF NOT EXISTS is_under_development BOOLEAN NOT NULL DEFAULT FALSE
            """))
            db.session.commit()
            logger.info("Successfully added is_under_development column")

            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
