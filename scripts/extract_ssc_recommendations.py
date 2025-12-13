"""
Script to extract SSC recommendations from existing meeting reports
Reads existing SSC meetings from database and extracts recommendations from their PDF reports
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.config.extensions import db
from src.scrapers.ssc_meeting_scraper import SSCMeetingScraper
from datetime import datetime
from flask import Flask
import logging
import uuid
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask app for database access"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/safmc_fmp_tracker')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def extract_recommendations_from_meetings():
    """Extract recommendations from existing SSC meeting reports"""
    app = create_app()

    with app.app_context():
        logger.info("Starting SSC recommendations extraction...")

        # Initialize scraper
        scraper = SSCMeetingScraper()

        # Get all SSC meetings with report URLs
        result = db.session.execute(text("""
            SELECT id, title, report_url
            FROM ssc_meetings
            WHERE report_url IS NOT NULL
            ORDER BY meeting_date_start DESC
        """))

        meetings = result.fetchall()
        logger.info(f"Found {len(meetings)} SSC meetings with report URLs")

        if not meetings:
            logger.warning("No meetings with report URLs found!")
            return

        recommendations_added = 0
        meetings_processed = 0

        for meeting in meetings:
            meeting_id = meeting[0]
            meeting_title = meeting[1]
            report_url = meeting[2]

            try:
                logger.info(f"\n--- Processing: {meeting_title[:100]} ---")
                logger.info(f"Report URL: {report_url}")

                # Check if we already have recommendations for this meeting
                check_result = db.session.execute(
                    text("SELECT COUNT(*) FROM ssc_recommendations WHERE meeting_id = :meeting_id"),
                    {"meeting_id": meeting_id}
                )
                existing_count = check_result.scalar()

                if existing_count > 0:
                    logger.info(f"Already has {existing_count} recommendations - skipping")
                    continue

                # Download the PDF report
                logger.info("Downloading PDF report...")
                pdf_bytes = scraper.download_document(report_url)

                if not pdf_bytes:
                    logger.warning("Could not download PDF")
                    continue

                # Extract text from PDF
                logger.info("Extracting text from PDF...")
                report_text = scraper.extract_text_from_pdf(pdf_bytes)

                if not report_text:
                    logger.warning("Could not extract text from PDF")
                    continue

                logger.info(f"Extracted {len(report_text)} characters of text")

                # Parse recommendations
                logger.info("Parsing recommendations...")
                recommendations = scraper.parse_recommendations_from_report(report_text)

                logger.info(f"Found {len(recommendations)} recommendations")

                # Insert recommendations into database
                for rec_data in recommendations:
                    rec_insert_sql = text("""
                        INSERT INTO ssc_recommendations (
                            id, meeting_id, recommendation_number, title, recommendation_text,
                            recommendation_type, species, abc_value, abc_units, status,
                            created_at, updated_at
                        ) VALUES (
                            :id, :meeting_id, :rec_number, :title, :rec_text,
                            :rec_type, :species, :abc_value, :abc_units, :status,
                            NOW(), NOW()
                        )
                    """)

                    db.session.execute(rec_insert_sql, {
                        'id': str(uuid.uuid4()),
                        'meeting_id': meeting_id,
                        'rec_number': rec_data.get('recommendation_number'),
                        'title': (rec_data.get('title', 'SSC Recommendation') or 'SSC Recommendation')[:500],
                        'rec_text': rec_data.get('recommendation_text', ''),
                        'rec_type': (rec_data.get('recommendation_type', 'General Recommendation') or 'General Recommendation')[:100],
                        'species': rec_data.get('species', []),
                        'abc_value': rec_data.get('abc_value'),
                        'abc_units': rec_data.get('abc_units'),
                        'status': rec_data.get('status', 'pending')
                    })
                    recommendations_added += 1
                    logger.info(f"  - Added: {rec_data.get('title', 'SSC Recommendation')[:80]}")

                db.session.commit()
                meetings_processed += 1
                logger.info(f"Successfully processed meeting with {len(recommendations)} recommendations")

            except Exception as e:
                logger.error(f"Error processing meeting '{meeting_title[:100]}': {e}")
                db.session.rollback()
                continue

        logger.info(f"\n=== SSC Recommendations Extraction Complete ===")
        logger.info(f"Meetings processed: {meetings_processed}")
        logger.info(f"Recommendations added: {recommendations_added}")

        # Show final counts
        result = db.session.execute(text("SELECT COUNT(*) FROM ssc_meetings"))
        total_meetings = result.scalar()
        result = db.session.execute(text("SELECT COUNT(*) FROM ssc_recommendations"))
        total_recommendations = result.scalar()
        logger.info(f"Total meetings in database: {total_meetings}")
        logger.info(f"Total recommendations in database: {total_recommendations}")

if __name__ == '__main__':
    extract_recommendations_from_meetings()
