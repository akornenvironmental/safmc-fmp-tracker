"""
Script to populate SSC meetings and recommendations from safmc.net
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
from sqlalchemy.dialects.postgresql import UUID, ARRAY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask app for database access"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/safmc_fmp_tracker')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def populate_ssc_meetings():
    """Scrape and populate SSC meetings"""
    app = create_app()

    with app.app_context():
        logger.info("Starting SSC data population...")

        # Initialize scraper
        scraper = SSCMeetingScraper()

        # Scrape meetings
        logger.info("Scraping SSC meetings...")
        meetings_data = scraper.scrape_all_meetings()

        if not meetings_data:
            logger.warning("No meetings found!")
            return

        logger.info(f"Found {len(meetings_data)} meetings")

        # Insert meetings into database
        meetings_added = 0
        recommendations_added = 0

        for meeting_data in meetings_data:
            try:
                from sqlalchemy import text

                # Check if meeting already exists (by title)
                result = db.session.execute(text("SELECT id FROM ssc_meetings WHERE title = :title"),
                                           {"title": meeting_data['title'][:500]})
                existing = result.first()

                if existing:
                    logger.info(f"Meeting already exists: {meeting_data['title'][:100]}")
                    continue

                # Parse dates
                meeting_date_start = None
                meeting_date_end = None

                if meeting_data.get('meeting_date_start'):
                    try:
                        meeting_date_start = datetime.fromisoformat(meeting_data['meeting_date_start'].replace('Z', '+00:00'))
                    except:
                        # Try parsing as date string
                        try:
                            meeting_date_start = datetime.strptime(meeting_data['meeting_date_start'], '%Y-%m-%d')
                        except:
                            logger.warning(f"Could not parse start date: {meeting_data['meeting_date_start']}")

                if meeting_data.get('meeting_date_end'):
                    try:
                        meeting_date_end = datetime.fromisoformat(meeting_data['meeting_date_end'].replace('Z', '+00:00'))
                    except:
                        try:
                            meeting_date_end = datetime.strptime(meeting_data['meeting_date_end'], '%Y-%m-%d')
                        except:
                            logger.warning(f"Could not parse end date: {meeting_data['meeting_date_end']}")

                # Create meeting using raw SQL
                meeting_id = str(uuid.uuid4())
                title = meeting_data['title'][:500] if meeting_data.get('title') else 'SSC Meeting'
                status = 'past' if meeting_date_start and meeting_date_start < datetime.utcnow() else 'scheduled'

                insert_sql = text("""
                    INSERT INTO ssc_meetings (
                        id, title, meeting_date_start, meeting_date_end, location, is_virtual,
                        meeting_type, status, agenda_url, briefing_book_url, report_url,
                        webinar_link, description, topics, species_discussed,
                        created_at, updated_at
                    ) VALUES (
                        :id, :title, :start_date, :end_date, :location, :is_virtual,
                        :meeting_type, :status, :agenda_url, :briefing_book_url, :report_url,
                        :webinar_link, :description, :topics, :species_discussed,
                        NOW(), NOW()
                    )
                """)

                db.session.execute(insert_sql, {
                    'id': meeting_id,
                    'title': title,
                    'start_date': meeting_date_start or datetime.utcnow(),
                    'end_date': meeting_date_end,
                    'location': meeting_data.get('location', '')[:500] if meeting_data.get('location') else None,
                    'is_virtual': meeting_data.get('is_virtual', False),
                    'meeting_type': (meeting_data.get('meeting_type', 'General Meeting') or 'General Meeting')[:100],
                    'status': status,
                    'agenda_url': meeting_data.get('agenda_url'),
                    'briefing_book_url': meeting_data.get('briefing_book_url'),
                    'report_url': meeting_data.get('report_url'),
                    'webinar_link': meeting_data.get('webinar_link'),
                    'description': meeting_data.get('description'),
                    'topics': meeting_data.get('topics', []),
                    'species_discussed': meeting_data.get('species_discussed', [])
                })

                meetings_added += 1
                logger.info(f"Added meeting: {title[:100]}")

                # Try to extract recommendations from report PDF if available
                if meeting_data.get('report_url'):
                    try:
                        logger.info(f"Downloading report from {meeting_data['report_url']}")
                        pdf_bytes = scraper.download_document(meeting_data['report_url'])

                        if pdf_bytes:
                            logger.info("Extracting text from PDF...")
                            report_text = scraper.extract_text_from_pdf(pdf_bytes)

                            if report_text:
                                logger.info("Parsing recommendations from report text...")
                                recommendations = scraper.parse_recommendations_from_report(report_text)

                                logger.info(f"Found {len(recommendations)} recommendations in report")

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
                    except Exception as pdf_error:
                        logger.warning(f"Could not extract recommendations from PDF: {pdf_error}")

                db.session.commit()

            except Exception as e:
                logger.error(f"Error adding meeting '{meeting_data.get('title', 'Unknown')[:100]}': {e}")
                db.session.rollback()
                continue

        logger.info(f"\n=== SSC Data Population Complete ===")
        logger.info(f"Meetings added: {meetings_added}")
        logger.info(f"Recommendations added: {recommendations_added}")

        # Show current counts using raw SQL
        result = db.session.execute(text("SELECT COUNT(*) FROM ssc_meetings"))
        total_meetings = result.scalar()
        result = db.session.execute(text("SELECT COUNT(*) FROM ssc_recommendations"))
        total_recommendations = result.scalar()
        logger.info(f"Total meetings in database: {total_meetings}")
        logger.info(f"Total recommendations in database: {total_recommendations}")

if __name__ == '__main__':
    populate_ssc_meetings()
