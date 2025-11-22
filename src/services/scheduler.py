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

        # Schedule daily comment scraping at 6 AM EST (11 AM UTC)
        @scheduler.scheduled_job(CronTrigger(hour=11, minute=0))
        def daily_comments_scrape():
            """Daily scraping job for public comments from all SAFMC sources"""
            with app.app_context():
                try:
                    logger.info("Starting daily comments scrape job")

                    from src.scrapers.comments_scraper import CommentsScraper
                    from src.config.extensions import db
                    from src.models.comment import Comment
                    from src.models.scrape_log import ScrapeLog

                    start_time = datetime.utcnow()

                    # Scrape comments from all configured sources
                    comments_scraper = CommentsScraper()
                    results = comments_scraper.scrape_all_comments()

                    items_new = 0
                    items_updated = 0

                    for comment_data in results['comments']:
                        # Check if comment already exists
                        existing = Comment.query.filter_by(comment_id=comment_data['comment_id']).first()

                        if existing:
                            # Update existing comment
                            existing.comment_text = comment_data.get('comment_text')
                            existing.position = comment_data.get('position')
                            existing.key_topics = comment_data.get('key_topics')
                            existing.updated_at = datetime.utcnow()
                            items_updated += 1
                        else:
                            # Create new comment
                            comment = Comment(
                                comment_id=comment_data['comment_id'],
                                name=comment_data.get('name'),
                                organization=comment_data.get('organization'),
                                email=comment_data.get('email'),
                                city=comment_data.get('city'),
                                state=comment_data.get('state'),
                                contact_id=comment_data.get('contact_id'),
                                organization_id=comment_data.get('organization_id'),
                                action_id=comment_data.get('action_id'),
                                comment_date=datetime.strptime(comment_data['submit_date'], '%m/%d/%Y') if comment_data.get('submit_date') else None,
                                comment_type='Written',
                                commenter_type=comment_data.get('commenter_type'),
                                position=comment_data.get('position'),
                                key_topics=comment_data.get('key_topics'),
                                comment_text=comment_data.get('comment_text'),
                                amendment_phase=comment_data.get('amendment_phase'),
                                source='SAFMC Google Sheets',
                                source_url=comment_data.get('source_url'),
                                data_source=comment_data.get('data_source')
                            )
                            db.session.add(comment)
                            items_new += 1

                    db.session.commit()

                    # Log the operation
                    duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                    log = ScrapeLog(
                        source='scheduled_daily_comments',
                        action_type='daily_comments_scrape',
                        status='success',
                        items_found=results['total_found'],
                        items_new=items_new,
                        items_updated=items_updated,
                        duration_ms=duration_ms,
                        completed_at=datetime.utcnow()
                    )
                    db.session.add(log)
                    db.session.commit()

                    # Send email notifications for new comments
                    if items_new > 0:
                        try:
                            from src.services.notification_service import notify_admins_of_new_comments
                            # Get the new comments for notification
                            new_comment_data = [c.to_dict() for c in Comment.query.order_by(Comment.created_at.desc()).limit(items_new).all()]
                            notify_admins_of_new_comments(new_comment_data, db.session)
                        except Exception as notify_error:
                            logger.error(f"Error sending comment notifications: {notify_error}")

                    logger.info(f"Daily comments scrape completed: {items_new} new, {items_updated} updated from {len(results['by_source'])} sources")

                except Exception as e:
                    logger.error(f"Error in daily comments scrape job: {e}")
                    import traceback
                    traceback.print_exc()
                    db.session.rollback()

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
