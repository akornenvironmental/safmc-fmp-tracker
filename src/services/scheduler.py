"""
Scheduler Service
Handles automated scraping and data updates
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import os

logger = logging.getLogger(__name__)

def init_scheduler(app):
    """Initialize the scheduler for automated tasks"""

    scheduler = BackgroundScheduler()

    # Only run scheduler if enabled
    if os.getenv('ENABLE_SCHEDULER', 'true').lower() == 'true':

        # Schedule weekly scraping at 2 AM on Sundays
        @scheduler.scheduled_job(CronTrigger(day_of_week='sun', hour=2, minute=0))
        def weekly_scrape():
            """Weekly scraping job for actions, amendments, and stock assessments"""
            with app.app_context():
                try:
                    logger.info("Starting weekly scrape job")

                    from src.scrapers.amendments_scraper import AmendmentsScraper
                    from src.scrapers.meetings_scraper import MeetingsScraper
                    from src.config.extensions import db
                    from src.models.action import Action
                    from src.models.meeting import Meeting
                    from src.models.scrape_log import ScrapeLog

                    start_time = datetime.utcnow()

                    # Scrape amendments
                    amendments_scraper = AmendmentsScraper()
                    amendments_results = amendments_scraper.scrape_all()

                    items_new = 0
                    items_updated = 0

                    for amendment_data in amendments_results['amendments']:
                        action = Action.query.filter_by(action_id=amendment_data['action_id']).first()

                        if action:
                            action.title = amendment_data['title']
                            action.type = amendment_data['type']
                            action.fmp = amendment_data['fmp']
                            action.progress_stage = amendment_data['progress_stage']
                            action.description = amendment_data['description']
                            action.lead_staff = amendment_data['lead_staff']
                            action.last_scraped = datetime.utcnow()
                            action.updated_at = datetime.utcnow()
                            items_updated += 1
                        else:
                            action = Action(
                                action_id=amendment_data['action_id'],
                                title=amendment_data['title'],
                                type=amendment_data['type'],
                                fmp=amendment_data['fmp'],
                                progress_stage=amendment_data['progress_stage'],
                                description=amendment_data['description'],
                                lead_staff=amendment_data['lead_staff'],
                                source_url=amendment_data['source_url'],
                                last_scraped=datetime.utcnow()
                            )
                            db.session.add(action)
                            items_new += 1

                    # Scrape meetings
                    meetings_scraper = MeetingsScraper()
                    meetings_results = meetings_scraper.scrape_meetings()

                    for meeting_data in meetings_results['meetings']:
                        meeting = Meeting.query.filter_by(meeting_id=meeting_data['meeting_id']).first()

                        if meeting:
                            meeting.title = meeting_data['title']
                            meeting.type = meeting_data['type']
                            meeting.start_date = meeting_data['start_date']
                            meeting.location = meeting_data['location']
                            meeting.description = meeting_data['description']
                            meeting.last_scraped = datetime.utcnow()
                            meeting.updated_at = datetime.utcnow()
                        else:
                            meeting = Meeting(
                                meeting_id=meeting_data['meeting_id'],
                                title=meeting_data['title'],
                                type=meeting_data['type'],
                                start_date=meeting_data['start_date'],
                                end_date=meeting_data['end_date'],
                                location=meeting_data['location'],
                                description=meeting_data['description'],
                                source_url=meeting_data['source_url'],
                                status=meeting_data['status'],
                                last_scraped=datetime.utcnow()
                            )
                            db.session.add(meeting)
                            items_new += 1

                    # Scrape stock assessments from SEDAR and StockSMART
                    try:
                        from src.scrapers.sedar_scraper import SEDARScraper
                        from src.scrapers.stocksmart_scraper import StockSMARTScraper

                        logger.info("Scraping SEDAR assessments...")
                        sedar_scraper = SEDARScraper()
                        sedar_results = sedar_scraper.scrape_assessments()

                        logger.info("Scraping StockSMART status...")
                        stocksmart_scraper = StockSMARTScraper()
                        stocksmart_results = stocksmart_scraper.get_stock_status()

                        logger.info(f"Stock assessments scraped: SEDAR={len(sedar_results.get('assessments', []))}, StockSMART={len(stocksmart_results.get('stocks', []))}")
                    except Exception as assess_error:
                        logger.error(f"Error scraping stock assessments: {assess_error}")

                    db.session.commit()

                    # Log the operation
                    duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                    log = ScrapeLog(
                        source='scheduled_weekly',
                        action_type='weekly_scrape',
                        status='success',
                        items_found=amendments_results['total_found'] + meetings_results['total_found'],
                        items_new=items_new,
                        items_updated=items_updated,
                        duration_ms=duration_ms,
                        completed_at=datetime.utcnow()
                    )
                    db.session.add(log)
                    db.session.commit()

                    logger.info(f"Weekly scrape completed: {items_new} new, {items_updated} updated")

                except Exception as e:
                    logger.error(f"Error in weekly scrape job: {e}")
                    db.session.rollback()

        scheduler.start()
        logger.info("Scheduler started successfully")

    else:
        logger.info("Scheduler disabled")

    return scheduler
