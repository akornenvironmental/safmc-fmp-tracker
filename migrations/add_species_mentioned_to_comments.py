"""
Migration: Add species_mentioned column to comments table
Run this to add species detection capability to comments
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
    """Add species_mentioned column to comments table"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'comments' AND column_name = 'species_mentioned'
            """))
            if result.fetchone():
                logger.info("species_mentioned column already exists")
                return True

            # Add the column
            logger.info("Adding species_mentioned column to comments table...")
            db.session.execute(text("""
                ALTER TABLE comments
                ADD COLUMN IF NOT EXISTS species_mentioned TEXT
            """))
            db.session.commit()
            logger.info("Successfully added species_mentioned column")

            # Create index for faster searches
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_comments_species_mentioned
                ON comments (species_mentioned)
                WHERE species_mentioned IS NOT NULL
            """))
            db.session.commit()
            logger.info("Successfully created index on species_mentioned")

            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
