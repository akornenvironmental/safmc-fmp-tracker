"""
Initialize database and create tables
Run this before first use: python init_db.py
"""

from app import app
from src.config.extensions import db

with app.app_context():
    # Import all models to ensure they're registered
    from src.models.action import Action
    from src.models.meeting import Meeting
    from src.models.comment import Comment
    from src.models.milestone import Milestone
    from src.models.scrape_log import ScrapeLog

    # Create all tables
    db.create_all()

    print("Database tables created successfully!")
    print("\nCreated tables:")
    print("- actions")
    print("- meetings")
    print("- comments")
    print("- milestones")
    print("- scrape_logs")
