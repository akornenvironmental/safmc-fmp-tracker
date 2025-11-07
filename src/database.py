"""
Database utility functions
"""

from src.config.extensions import db


def get_db_connection():
    """
    Get a raw database connection from SQLAlchemy engine
    This is for compatibility with legacy psycopg2-style code
    """
    return db.engine.raw_connection()
