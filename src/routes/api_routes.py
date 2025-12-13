"""
API Routes for SAFMC FMP Tracker
Provides REST API endpoints for data access and management
"""

from flask import Blueprint, jsonify, request, session, current_app
from sqlalchemy import func, desc, text
from sqlalchemy.exc import OperationalError, DBAPIError
from datetime import datetime, timedelta
import logging
import time
import json
import threading
from functools import wraps

from src.config.extensions import db
from src.models.action import Action
from src.models.meeting import Meeting
from src.models.comment import Comment
from src.models.contact import Contact
from src.models.organization import Organization
from src.models.milestone import Milestone
from src.models.scrape_log import ScrapeLog
from src.models.workplan import WorkplanVersion, WorkplanItem, WorkplanMilestone, WorkplanUploadLog
from src.scrapers.amendments_scraper import AmendmentsScraper
from src.scrapers.amendments_scraper_enhanced import EnhancedAmendmentsScraper
from src.scrapers.meetings_scraper import MeetingsScraper
from src.scrapers.multi_council_scraper import MultiCouncilScraper
from src.scrapers.comments_scraper import CommentsScraper
from src.scrapers.briefing_books_scraper import BriefingBooksScraper
from src.services.ai_service import AIService
from src.middleware.auth_middleware import require_auth, require_admin
from src.middleware.auth import require_role
from src.utils.security import validate_pagination_params, validate_string_length, safe_error_response

bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Initialize services
ai_service = AIService()

# Database retry decorator
def retry_on_db_error(max_retries=3, delay=0.5):
    """Decorator to retry database operations on connection errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DBAPIError) as e:
                    last_exception = e
                    logger.warning(f"Database error on attempt {attempt + 1}/{max_retries}: {e}")

                    # Remove stale session
                    db.session.remove()

                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
                        raise last_exception
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ==================== DASHBOARD ENDPOINTS ====================

@bp.route('/dashboard/stats')
@retry_on_db_error(max_retries=3, delay=0.5)
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Count actions
        total_actions = Action.query.count()
        active_actions = Action.query.filter(
            Action.progress_stage.notin_(['Implemented', 'Complete'])
        ).count()
        pending_review = Action.query.filter(
            Action.progress_stage.in_(['Public Hearing', 'Final Approval', 'Secretarial Review'])
        ).count()

        # Count meetings
        total_meetings = Meeting.query.count()
        upcoming_meetings = Meeting.query.filter(
            Meeting.start_date > datetime.utcnow()
        ).count()

        # Count comments
        total_comments = Comment.query.count()
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_comments = Comment.query.filter(
            Comment.comment_date > thirty_days_ago
        ).count()

        return jsonify({
            'totalActions': total_actions,
            'activeActions': active_actions,
            'pendingReview': pending_review,
            'totalMeetings': total_meetings,
            'upcomingMeetings': upcoming_meetings,
            'totalComments': total_comments,
            'recentComments': recent_comments
        })

    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/dashboard/recent-amendments')
def recent_amendments():
    """Get recent amendments"""
    try:
        limit = request.args.get('limit', 10, type=int)
        # Validate limit bounds (1-100)
        limit = max(1, min(limit or 10, 100))

        actions = Action.query.order_by(desc(Action.updated_at)).limit(limit).all()

        return jsonify({
            'success': True,
            'actions': [action.to_dict() for action in actions]
        })

    except Exception as e:
        logger.error(f"Error getting recent amendments: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

# ==================== ACTIONS ENDPOINTS ====================

@bp.route('/actions')
def get_actions():
    """Get all actions with optional filtering"""
    try:
        # Get query parameters
        fmp = request.args.get('fmp')
        status = request.args.get('status')
        progress_stage = request.args.get('progress_stage')
        action_type = request.args.get('type')

        # Build query
        query = Action.query

        if fmp:
            query = query.filter(Action.fmp == fmp)
        if status:
            query = query.filter(Action.status == status)
        if progress_stage:
            query = query.filter(Action.progress_stage == progress_stage)
        if action_type:
            query = query.filter(Action.type == action_type)

        actions = query.order_by(desc(Action.updated_at)).all()

        return jsonify({
            'success': True,
            'actions': [action.to_dict() for action in actions],
            'total': len(actions)
        })

    except Exception as e:
        logger.error(f"Error getting actions: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/actions/<action_id>')
def get_action(action_id):
    """Get a specific action by ID"""
    try:
        action = Action.query.filter_by(action_id=action_id).first()

        if not action:
            return jsonify({'error': 'Action not found'}), 404

        # Get related data
        milestones = [m.to_dict() for m in action.milestones.all()]
        comments = [c.to_dict() for c in action.comments.all()]

        return jsonify({
            'action': action.to_dict(),
            'milestones': milestones,
            'comments': comments
        })

    except Exception as e:
        logger.error(f"Error getting action {action_id}: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

# ==================== MEETINGS ENDPOINTS ====================

@bp.route('/meetings')
@retry_on_db_error(max_retries=3, delay=0.5)
def get_meetings():
    """Get all meetings"""
    try:
        # Get query parameters
        upcoming_only = request.args.get('upcoming', 'false').lower() == 'true'
        meeting_type = request.args.get('type')

        # Build query
        query = Meeting.query

        if upcoming_only:
            query = query.filter(Meeting.start_date > datetime.utcnow())

        if meeting_type:
            query = query.filter(Meeting.type == meeting_type)

        meetings = query.order_by(Meeting.start_date).all()

        return jsonify({
            'success': True,
            'meetings': [meeting.to_dict() for meeting in meetings],
            'total': len(meetings)
        })

    except Exception as e:
        logger.error(f"Error getting meetings: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/meetings/<meeting_id>')
def get_meeting(meeting_id):
    """Get a specific meeting by ID"""
    try:
        meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()

        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404

        return jsonify(meeting.to_dict())

    except Exception as e:
        logger.error(f"Error getting meeting {meeting_id}: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

# ==================== COMMENTS ENDPOINTS ====================

@bp.route('/comments')
def get_comments():
    """Get all comments with action details"""
    try:
        action_id = request.args.get('action_id')

        # Join comments with actions to get action title and FMP
        query = db.session.query(Comment, Action).outerjoin(
            Action, Comment.action_id == Action.action_id
        )

        if action_id:
            query = query.filter(Comment.action_id == action_id)

        results = query.order_by(desc(Comment.comment_date)).all()

        # Build response with action details
        comments_data = []
        for comment, action in results:
            comment_dict = comment.to_dict()
            # Add action details
            comment_dict['actionTitle'] = action.title if action else None
            comment_dict['actionFmp'] = action.fmp if action else None
            comments_data.append(comment_dict)

        return jsonify({
            'success': True,
            'comments': comments_data,
            'total': len(comments_data)
        })

    except Exception as e:
        logger.error(f"Error getting comments: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/comments/detect-species', methods=['POST'])
@require_admin
def detect_species_in_comments():
    """Detect and tag species mentioned in comment text"""
    try:
        from src.services.species_service import SpeciesService
        species_service = SpeciesService()

        # Get comments without species_mentioned populated
        comments = Comment.query.filter(
            (Comment.species_mentioned == None) | (Comment.species_mentioned == '')
        ).filter(
            Comment.comment_text != None,
            Comment.comment_text != ''
        ).all()

        if not comments:
            return jsonify({
                'success': True,
                'message': 'No comments need species detection',
                'processed': 0
            })

        updated_count = 0
        species_counts = {}

        for comment in comments:
            if comment.comment_text:
                # Use the species service to extract species from text
                detected = species_service.extract_species_from_text(comment.comment_text)
                if detected:
                    comment.species_mentioned = ','.join(sorted(detected))
                    updated_count += 1
                    # Track counts
                    for species in detected:
                        species_counts[species] = species_counts.get(species, 0) + 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Detected species in {updated_count} comments',
            'processed': updated_count,
            'totalComments': len(comments),
            'speciesCounts': species_counts
        })

    except Exception as e:
        logger.error(f"Error detecting species in comments: {e}")
        db.session.rollback()
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/comments/species-stats', methods=['GET'])
def get_comment_species_stats():
    """Get statistics on species mentioned in comments"""
    try:
        # Get all comments with species_mentioned
        comments = Comment.query.filter(
            Comment.species_mentioned != None,
            Comment.species_mentioned != ''
        ).all()

        species_counts = {}
        comments_by_species = {}

        for comment in comments:
            if comment.species_mentioned:
                species_list = comment.species_mentioned.split(',')
                for species in species_list:
                    species = species.strip()
                    if species:
                        species_counts[species] = species_counts.get(species, 0) + 1
                        if species not in comments_by_species:
                            comments_by_species[species] = []
                        comments_by_species[species].append({
                            'id': comment.comment_id,
                            'name': comment.name,
                            'position': comment.position,
                            'date': comment.comment_date.isoformat() if comment.comment_date else None
                        })

        # Sort by count descending
        sorted_species = sorted(species_counts.items(), key=lambda x: x[1], reverse=True)

        return jsonify({
            'success': True,
            'totalCommentsWithSpecies': len(comments),
            'speciesCounts': dict(sorted_species),
            'topSpecies': [{'name': s, 'count': c} for s, c in sorted_species[:10]],
            'commentsBySpecies': comments_by_species
        })

    except Exception as e:
        logger.error(f"Error getting species stats: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/contacts')
def get_contacts():
    """Get all contacts"""
    try:
        # Optional filters
        state = request.args.get('state')
        sector = request.args.get('sector')
        organization_id = request.args.get('organization_id')

        query = Contact.query

        if state:
            query = query.filter(Contact.state == state)
        if sector:
            query = query.filter(Contact.sector == sector)
        if organization_id:
            query = query.filter(Contact.organization_id == organization_id)

        contacts = query.order_by(desc(Contact.last_engagement_date)).all()

        return jsonify({
            'success': True,
            'contacts': [contact.to_dict() for contact in contacts],
            'total': len(contacts)
        })

    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/organizations')
def get_organizations():
    """Get all organizations"""
    try:
        # Optional filters
        state = request.args.get('state')
        org_type = request.args.get('org_type')

        query = Organization.query

        if state:
            query = query.filter(Organization.state == state)
        if org_type:
            query = query.filter(Organization.org_type == org_type)

        organizations = query.order_by(desc(Organization.total_comments)).all()

        return jsonify({
            'success': True,
            'organizations': [org.to_dict() for org in organizations],
            'total': len(organizations)
        })

    except Exception as e:
        logger.error(f"Error getting organizations: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

# ==================== SCRAPING ENDPOINTS ====================

@bp.route('/scrape/amendments', methods=['POST'])
@require_admin
def scrape_amendments():
    """Manually trigger amendments scraping"""
    try:
        start_time = datetime.utcnow()

        scraper = AmendmentsScraper()
        results = scraper.scrape_all()

        # Save or update actions in database
        items_new = 0
        items_updated = 0

        for amendment_data in results['amendments']:
            action = Action.query.filter_by(action_id=amendment_data['action_id']).first()

            if action:
                # Update existing
                action.title = amendment_data['title']
                action.type = amendment_data['type']
                action.fmp = amendment_data['fmp']
                action.progress_stage = amendment_data['progress_stage']
                action.progress_percentage = amendment_data.get('progress_percentage', 0)
                action.phase = amendment_data.get('phase', '')
                action.description = amendment_data['description']
                action.lead_staff = amendment_data['lead_staff']
                action.source_url = amendment_data.get('source_url', action.source_url)
                action.status = amendment_data.get('status')
                action.start_date = amendment_data.get('start_date')
                action.completion_date = amendment_data.get('completion_date')
                action.last_scraped = datetime.utcnow()
                action.updated_at = datetime.utcnow()
                items_updated += 1
            else:
                # Create new
                action = Action(
                    action_id=amendment_data['action_id'],
                    title=amendment_data['title'],
                    type=amendment_data['type'],
                    fmp=amendment_data['fmp'],
                    progress_stage=amendment_data['progress_stage'],
                    progress_percentage=amendment_data.get('progress_percentage', 0),
                    phase=amendment_data.get('phase', ''),
                    description=amendment_data['description'],
                    lead_staff=amendment_data['lead_staff'],
                    source_url=amendment_data['source_url'],
                    status=amendment_data.get('status'),
                    start_date=amendment_data.get('start_date'),
                    completion_date=amendment_data.get('completion_date'),
                    last_scraped=datetime.utcnow()
                )
                db.session.add(action)
                items_new += 1

        db.session.commit()

        # Log the scrape
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        log = ScrapeLog(
            source='amendments',
            action_type='scrape_amendments',
            status='success' if not results['errors'] else 'partial',
            items_found=results['total_found'],
            items_new=items_new,
            items_updated=items_updated,
            error_message='; '.join(results['errors']) if results['errors'] else None,
            duration_ms=duration_ms,
            completed_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'success': True,
            'itemsFound': results['total_found'],
            'itemsNew': items_new,
            'itemsUpdated': items_updated,
            'duration': duration_ms,
            'errors': results['errors']
        })

    except Exception as e:
        logger.error(f"Error in scrape_amendments: {e}")
        db.session.rollback()
        return safe_error_response(e)[0], safe_error_response(e)[1]


def _run_comprehensive_scrape_background():
    """
    Background function for comprehensive amendment scraping.
    Runs in a separate thread with its own Flask app context.
    """
    with current_app.app_context():
        try:
            start_time = datetime.utcnow()
            logger.info("Background comprehensive amendment scrape started...")

            scraper = EnhancedAmendmentsScraper(rate_limit=1.5)
            results = scraper.scrape_all_comprehensive()

            # Save or update actions in database
            items_new = 0
            items_updated = 0
            milestones_created = 0
            documents_queued = 0

            for amendment_data in results['amendments']:
                action = Action.query.filter_by(action_id=amendment_data['action_id']).first()

                if action:
                    # Update existing action
                    action.title = amendment_data['title']
                    action.type = amendment_data['type']
                    action.fmp = amendment_data['fmp']
                    action.progress_stage = amendment_data['progress_stage']
                    action.progress_percentage = amendment_data.get('progress_percentage', 0)
                    action.phase = amendment_data.get('phase', '')
                    action.description = amendment_data['description']
                    action.lead_staff = amendment_data['lead_staff']
                    action.source_url = amendment_data.get('source_url', action.source_url)
                    action.status = amendment_data.get('status')
                    action.start_date = amendment_data.get('start_date')
                    action.completion_date = amendment_data.get('completion_date')

                    # Enhanced fields
                    if amendment_data.get('detail_url'):
                        action.source_url = amendment_data['detail_url']
                    if amendment_data.get('detailed_description'):
                        action.description = amendment_data['detailed_description']
                    if amendment_data.get('federal_register'):
                        if not action.notes:
                            action.notes = ''
                        action.notes += f"\nFederal Register: {amendment_data['federal_register']}"

                    action.last_scraped = datetime.utcnow()
                    action.updated_at = datetime.utcnow()
                    items_updated += 1
                else:
                    # Create new action
                    action = Action(
                        action_id=amendment_data['action_id'],
                        title=amendment_data['title'],
                        type=amendment_data['type'],
                        fmp=amendment_data['fmp'],
                        progress_stage=amendment_data['progress_stage'],
                        progress_percentage=amendment_data.get('progress_percentage', 0),
                        phase=amendment_data.get('phase', ''),
                        description=amendment_data.get('detailed_description') or amendment_data['description'],
                        lead_staff=amendment_data['lead_staff'],
                        source_url=amendment_data.get('detail_url') or amendment_data.get('source_url'),
                        status=amendment_data.get('status'),
                        start_date=amendment_data.get('start_date'),
                        completion_date=amendment_data.get('completion_date'),
                        last_scraped=datetime.utcnow()
                    )

                    if amendment_data.get('federal_register'):
                        action.notes = f"Federal Register: {amendment_data['federal_register']}"

                    db.session.add(action)
                    items_new += 1

            db.session.commit()

            # Create milestones from timeline data
            for milestone_data in results['milestones']:
                if milestone_data.get('action_id'):
                    action = Action.query.filter_by(action_id=milestone_data['action_id']).first()
                    if action:
                        milestone = Milestone(
                            action_id=action.action_id,
                            description=milestone_data.get('description', ''),
                            target_date=milestone_data.get('parsed_date'),
                            milestone_type='timeline'
                        )
                        db.session.add(milestone)
                        milestones_created += 1

            # Queue documents for processing
            for doc_data in results['documents']:
                documents_queued += 1

            db.session.commit()

            # Log the comprehensive scrape
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            log = ScrapeLog(
                source='amendments_comprehensive',
                action_type='scrape_amendments_comprehensive',
                status='success' if not results['errors'] else 'partial',
                items_found=results['total_found'],
                items_new=items_new,
                items_updated=items_updated,
                error_message='; '.join(results['errors'][:5]) if results['errors'] else None,
                duration_ms=duration_ms,
                completed_at=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()

            logger.info(f"Background comprehensive scrape complete: {items_new} new, {items_updated} updated, {milestones_created} milestones")

        except Exception as e:
            logger.error(f"Error in background comprehensive scrape: {e}")
            import traceback
            traceback.print_exc()
            try:
                db.session.rollback()
                # Log the failure
                log = ScrapeLog(
                    source='amendments_comprehensive',
                    action_type='scrape_amendments_comprehensive',
                    status='error',
                    items_found=0,
                    items_new=0,
                    items_updated=0,
                    error_message=str(e)[:500],
                    completed_at=datetime.utcnow()
                )
                db.session.add(log)
                db.session.commit()
            except:
                pass


@bp.route('/scrape/amendments/comprehensive', methods=['POST'])
@require_admin
def scrape_amendments_comprehensive():
    """
    Comprehensive historical amendment scraping (2018-present) - Background Job

    This endpoint starts the scraper in a background thread and returns immediately.
    The scraper runs for 10-15 minutes without timing out.

    Check progress at: /api/logs/scrape?source=amendments_comprehensive&limit=1
    """
    try:
        # Start background thread
        thread = threading.Thread(target=_run_comprehensive_scrape_background, daemon=True)
        thread.start()

        logger.info("Comprehensive scrape started in background thread")

        return jsonify({
            'success': True,
            'message': 'Comprehensive amendment scrape started in background',
            'duration_estimate': '10-15 minutes',
            'check_status': '/api/logs/scrape?source=amendments_comprehensive&limit=1',
            'instructions': 'Check the logs endpoint periodically to monitor progress. The scrape will find ~215 historical amendments.'
        })

    except Exception as e:
        logger.error(f"Error starting comprehensive scrape: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/scrape/meetings', methods=['POST'])
@require_admin
def scrape_meetings():
    """Manually trigger meetings scraping from all councils"""
    try:
        start_time = datetime.utcnow()

        # Use multi-council scraper for comprehensive calendar integration
        multi_scraper = MultiCouncilScraper()
        results = multi_scraper.scrape_all_councils()

        # Save or update meetings in database
        items_new = 0
        items_updated = 0

        for meeting_data in results['meetings']:
            meeting = Meeting.query.filter_by(meeting_id=meeting_data['meeting_id']).first()

            if meeting:
                # Update existing
                meeting.title = meeting_data['title']
                meeting.type = meeting_data['type']
                meeting.council = meeting_data.get('council')
                meeting.organization_type = meeting_data.get('organization_type')
                meeting.start_date = meeting_data['start_date']
                meeting.end_date = meeting_data['end_date']
                meeting.location = meeting_data['location']
                meeting.description = meeting_data['description']
                meeting.agenda_url = meeting_data.get('agenda_url')
                meeting.source_url = meeting_data['source_url']
                meeting.rss_feed_url = meeting_data.get('rss_feed_url')
                meeting.status = meeting_data['status']
                meeting.last_scraped = datetime.utcnow()
                meeting.updated_at = datetime.utcnow()
                items_updated += 1
            else:
                # Create new
                meeting = Meeting(
                    meeting_id=meeting_data['meeting_id'],
                    title=meeting_data['title'],
                    type=meeting_data['type'],
                    council=meeting_data.get('council'),
                    organization_type=meeting_data.get('organization_type'),
                    start_date=meeting_data['start_date'],
                    end_date=meeting_data['end_date'],
                    location=meeting_data['location'],
                    description=meeting_data['description'],
                    agenda_url=meeting_data.get('agenda_url'),
                    source_url=meeting_data['source_url'],
                    rss_feed_url=meeting_data.get('rss_feed_url'),
                    status=meeting_data['status'],
                    last_scraped=datetime.utcnow()
                )
                db.session.add(meeting)
                items_new += 1

        db.session.commit()

        # Log the scrape
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        log = ScrapeLog(
            source='meetings',
            action_type='scrape_meetings',
            status='success' if not results['errors'] else 'partial',
            items_found=results['total_found'],
            items_new=items_new,
            items_updated=items_updated,
            error_message='; '.join(results['errors']) if results['errors'] else None,
            duration_ms=duration_ms,
            completed_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'success': True,
            'itemsFound': results['total_found'],
            'itemsNew': items_new,
            'itemsUpdated': items_updated,
            'duration': duration_ms,
            'errors': results['errors']
        })

    except Exception as e:
        logger.error(f"Error in scrape_meetings: {e}")
        db.session.rollback()
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/scrape/fisherypulse', methods=['POST'])
@require_admin
def scrape_fisherypulse():
    """Trigger comprehensive FisheryPulse meeting scraping from Federal Register, NOAA, and all councils"""
    try:
        start_time = datetime.utcnow()

        # Import FisheryPulse scraper
        from src.scrapers.fisherypulse_scraper import FisheryPulseScraper

        scraper = FisheryPulseScraper()
        meetings = scraper.scrape_all()

        # Save meetings to database (pass db object)
        saved_count = scraper.save_to_database(meetings, db)

        # Log the scrape
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        log = ScrapeLog(
            source='fisherypulse',
            action_type='scrape_fisherypulse',
            status='success',
            items_found=len(meetings),
            items_new=saved_count,
            items_updated=0,
            duration_ms=duration_ms,
            completed_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'success': True,
            'itemsFound': len(meetings),
            'itemsNew': saved_count,
            'duration': duration_ms,
            'message': f'Synced {saved_count} new meetings from Federal Register, NOAA, and regional councils'
        })

    except Exception as e:
        logger.error(f"Error in scrape_fisherypulse: {e}")
        import traceback
        logger.error(traceback.format_exc())
        db.session.rollback()
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/scrape/all', methods=['POST'])
@require_admin
def scrape_all():
    """Trigger scraping of all data"""
    try:
        # Scrape amendments
        amendments_response = scrape_amendments()
        amendments_data = amendments_response.get_json() if hasattr(amendments_response, 'get_json') else {}

        # Scrape meetings
        meetings_response = scrape_meetings()
        meetings_data = meetings_response.get_json() if hasattr(meetings_response, 'get_json') else {}

        return jsonify({
            'success': True,
            'amendments': amendments_data,
            'meetings': meetings_data
        })

    except Exception as e:
        logger.error(f"Error in scrape_all: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

# ==================== AI QUERY ENDPOINTS ====================

@bp.route('/ai/query', methods=['POST'])
@require_auth
def ai_query():
    """Query the AI system"""
    start_time = time.time()
    query_log_id = None

    try:
        data = request.get_json()
        question = data.get('question')

        if not question:
            return jsonify({'error': 'Question is required'}), 400

        # Extract user information
        user_id = session.get('user_id')
        user_email = session.get('user_email')
        user_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        session_id = session.get('session_id')

        # Get context from database
        actions = Action.query.order_by(desc(Action.updated_at)).limit(10).all()
        context = {
            'actions': [a.to_dict() for a in actions]
        }

        # Calculate context size
        context_str = json.dumps(context)
        context_size = len(context_str)

        # Query AI service
        result = ai_service.query(question, context)

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Extract response info
        response_text = result.get('answer', '')
        success = not result.get('error')
        error_msg = result.get('error') if not success else None

        # Log query to database
        try:
            db.session.execute(text("""
                INSERT INTO ai_query_log (
                    user_id, user_email, user_ip,
                    question, response,
                    context_size_chars,
                    response_time_ms,
                    success, error_message,
                    user_agent, session_id
                ) VALUES (
                    :user_id, :user_email, :user_ip,
                    :question, :response,
                    :context_size,
                    :response_time,
                    :success, :error,
                    :user_agent, :session_id
                )
            """), {
                'user_id': user_id,
                'user_email': user_email,
                'user_ip': user_ip,
                'question': question,
                'response': response_text,
                'context_size': context_size,
                'response_time': response_time_ms,
                'success': success,
                'error': error_msg,
                'user_agent': user_agent,
                'session_id': session_id
            })
            db.session.commit()
        except Exception as log_error:
            logger.error(f"Failed to log AI query: {log_error}")
            db.session.rollback()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in AI query: {e}")

        # Log failed query
        try:
            response_time_ms = int((time.time() - start_time) * 1000)
            db.session.execute(text("""
                INSERT INTO ai_query_log (
                    user_id, user_email, user_ip,
                    question, response,
                    response_time_ms,
                    success, error_message,
                    user_agent, session_id
                ) VALUES (
                    :user_id, :user_email, :user_ip,
                    :question, :response,
                    :response_time,
                    :success, :error,
                    :user_agent, :session_id
                )
            """), {
                'user_id': session.get('user_id'),
                'user_email': session.get('user_email'),
                'user_ip': request.remote_addr,
                'question': data.get('question', '') if 'data' in locals() else '',
                'response': None,
                'response_time': response_time_ms,
                'success': False,
                'error': str(e),
                'user_agent': request.headers.get('User-Agent', ''),
                'session_id': session.get('session_id')
            })
            db.session.commit()
        except Exception as log_error:
            logger.error(f"Failed to log failed AI query: {log_error}")
            db.session.rollback()

        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/ai/analyze', methods=['POST'])
@require_auth
def ai_analyze():
    """Analyze FMP patterns"""
    try:
        actions = Action.query.all()
        actions_data = [a.to_dict() for a in actions]

        result = ai_service.analyze_patterns(actions_data)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/ai/report', methods=['POST'])
@require_auth
def ai_report():
    """Generate status report"""
    try:
        actions = Action.query.order_by(desc(Action.updated_at)).limit(15).all()
        meetings = Meeting.query.filter(
            Meeting.start_date > datetime.utcnow()
        ).order_by(Meeting.start_date).limit(10).all()

        actions_data = [a.to_dict() for a in actions]
        meetings_data = [m.to_dict() for m in meetings]

        result = ai_service.generate_status_report(actions_data, meetings_data)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/ai/search', methods=['POST'])
@require_auth
def ai_search():
    """Search FMP content"""
    try:
        data = request.get_json()
        search_terms = data.get('search_terms')

        if not search_terms:
            return jsonify({'error': 'Search terms are required'}), 400

        actions = Action.query.all()
        actions_data = [a.to_dict() for a in actions]

        result = ai_service.search_content(search_terms, actions_data)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in AI search: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/ai/analyze-comments', methods=['POST'])
@require_auth
def ai_analyze_comments():
    """Analyze public comments using AI to identify themes, sentiment, and concerns"""
    try:
        data = request.get_json() or {}

        # Get filter parameters
        fmp = data.get('fmp')
        position = data.get('position')
        state = data.get('state')
        commenter_type = data.get('commenterType')

        # Build query with filters
        query = Comment.query

        if fmp:
            # Need to join with Action to filter by FMP
            query = query.join(Action, Comment.action_id == Action.action_id).filter(Action.fmp.ilike(f'%{fmp}%'))

        if position:
            query = query.filter(Comment.position == position)

        if state:
            query = query.filter(Comment.state == state)

        if commenter_type:
            query = query.filter(Comment.commenter_type == commenter_type)

        # Get comments (limit to prevent overwhelming the AI)
        comments = query.order_by(desc(Comment.comment_date)).limit(200).all()

        if not comments:
            return jsonify({
                'success': False,
                'error': 'No comments found matching the specified filters'
            }), 404

        # Convert to dict format
        comments_data = []
        for c in comments:
            comment_dict = c.to_dict()
            # Add action info if available
            if c.action_id:
                action = Action.query.filter_by(action_id=c.action_id).first()
                if action:
                    comment_dict['actionFmp'] = action.fmp
                    comment_dict['actionTitle'] = action.title
            comments_data.append(comment_dict)

        # Filter params for AI context
        filter_params = {
            'fmp': fmp,
            'position': position,
            'state': state,
            'commenterType': commenter_type
        }

        # Run AI analysis
        result = ai_service.analyze_comments(comments_data, filter_params)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in AI comment analysis: {e}")
        import traceback
        traceback.print_exc()
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/ai/summarize-comments', methods=['POST'])
@require_auth
def ai_summarize_comments():
    """Generate summaries of comments grouped by a specified field"""
    try:
        data = request.get_json() or {}
        group_by = data.get('groupBy', 'fmp')

        # Validate group_by parameter
        valid_groups = ['fmp', 'position', 'state', 'commenterType']
        if group_by not in valid_groups:
            return jsonify({
                'error': f'Invalid groupBy parameter. Must be one of: {", ".join(valid_groups)}'
            }), 400

        # Get all comments with action info
        comments = Comment.query.order_by(desc(Comment.comment_date)).limit(500).all()

        if not comments:
            return jsonify({
                'success': False,
                'error': 'No comments found in database'
            }), 404

        # Convert to dict format with action info
        comments_data = []
        for c in comments:
            comment_dict = c.to_dict()
            if c.action_id:
                action = Action.query.filter_by(action_id=c.action_id).first()
                if action:
                    comment_dict['actionFmp'] = action.fmp
                    comment_dict['actionTitle'] = action.title
            comments_data.append(comment_dict)

        # Run AI summarization
        result = ai_service.summarize_comment_group(comments_data, group_by)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in AI comment summarization: {e}")
        import traceback
        traceback.print_exc()
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/ai/query-logs', methods=['GET'])
@require_admin
def get_ai_query_logs():
    """Get AI query logs for admin review and troubleshooting"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        success_only = request.args.get('success', None)
        search = request.args.get('search', '')

        # Build query
        query = """
            SELECT
                id, user_id, user_email, user_ip,
                question, response,
                context_size_chars, response_time_ms,
                success, error_message,
                created_at
            FROM ai_query_log
            WHERE 1=1
        """
        params = {}

        # Filter by success status
        if success_only is not None:
            query += " AND success = :success"
            params['success'] = success_only == 'true'

        # Search in questions and responses
        if search:
            query += " AND (question ILIKE :search OR response ILIKE :search)"
            params['search'] = f'%{search}%'

        # Order and pagination
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params['limit'] = min(limit, 1000)  # Cap at 1000
        params['offset'] = offset

        result = db.session.execute(text(query), params)

        logs = []
        for row in result:
            logs.append({
                'id': row[0],
                'user_id': row[1],
                'user_email': row[2],
                'user_ip': row[3],
                'question': row[4],
                'response': row[5],
                'context_size_chars': row[6],
                'response_time_ms': row[7],
                'success': row[8],
                'error_message': row[9],
                'created_at': row[10].isoformat() if row[10] else None
            })

        # Get total count
        count_query = "SELECT COUNT(*) FROM ai_query_log WHERE 1=1"
        count_params = {}
        if success_only is not None:
            count_query += " AND success = :success"
            count_params['success'] = success_only == 'true'
        if search:
            count_query += " AND (question ILIKE :search OR response ILIKE :search)"
            count_params['search'] = f'%{search}%'

        total = db.session.execute(text(count_query), count_params).scalar()

        return jsonify({
            'success': True,
            'logs': logs,
            'total': total,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"Error fetching AI query logs: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/ai/query-stats', methods=['GET'])
@require_admin
def get_ai_query_stats():
    """Get AI query statistics for admin dashboard"""
    try:
        # Total queries
        total = db.session.execute(text("SELECT COUNT(*) FROM ai_query_log")).scalar()

        # Success/failure counts
        success_count = db.session.execute(text(
            "SELECT COUNT(*) FROM ai_query_log WHERE success = true"
        )).scalar()

        failure_count = db.session.execute(text(
            "SELECT COUNT(*) FROM ai_query_log WHERE success = false"
        )).scalar()

        # Average response time
        avg_response_time = db.session.execute(text(
            "SELECT AVG(response_time_ms) FROM ai_query_log WHERE success = true"
        )).scalar()

        # Recent queries (last 24 hours)
        recent_count = db.session.execute(text("""
            SELECT COUNT(*) FROM ai_query_log
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """)).scalar()

        # Top users
        top_users = db.session.execute(text("""
            SELECT user_email, COUNT(*) as query_count
            FROM ai_query_log
            WHERE user_email IS NOT NULL
            GROUP BY user_email
            ORDER BY query_count DESC
            LIMIT 10
        """)).fetchall()

        return jsonify({
            'success': True,
            'stats': {
                'total_queries': total or 0,
                'successful_queries': success_count or 0,
                'failed_queries': failure_count or 0,
                'success_rate': round((success_count / total * 100) if total > 0 else 0, 2),
                'avg_response_time_ms': round(avg_response_time, 2) if avg_response_time else 0,
                'queries_24h': recent_count or 0,
                'top_users': [{'email': row[0], 'count': row[1]} for row in top_users]
            }
        })

    except Exception as e:
        logger.error(f"Error fetching AI query stats: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

# ==================== ENHANCED COMMENTS ENDPOINTS ====================

@bp.route('/comments/analytics')
def get_comments_analytics():
    """Get comment analytics"""
    try:
        action_id = request.args.get('action_id')

        query = Comment.query
        if action_id:
            query = query.filter(Comment.action_id == action_id)

        comments = query.all()

        # Calculate analytics
        analytics = {
            'total': len(comments),
            'by_phase': {},
            'by_position': {},
            'by_type': {},
            'by_state': {},
            'top_topics': {}
        }

        for comment in comments:
            # By phase
            if comment.amendment_phase:
                analytics['by_phase'][comment.amendment_phase] = \
                    analytics['by_phase'].get(comment.amendment_phase, 0) + 1

            # By position
            if comment.position:
                analytics['by_position'][comment.position] = \
                    analytics['by_position'].get(comment.position, 0) + 1

            # By type
            if comment.commenter_type:
                analytics['by_type'][comment.commenter_type] = \
                    analytics['by_type'].get(comment.commenter_type, 0) + 1

            # By state
            if comment.state:
                analytics['by_state'][comment.state] = \
                    analytics['by_state'].get(comment.state, 0) + 1

            # Topics
            if comment.key_topics:
                for topic in comment.key_topics.split(','):
                    topic = topic.strip()
                    if topic:
                        analytics['top_topics'][topic] = \
                            analytics['top_topics'].get(topic, 0) + 1

        return jsonify(analytics)

    except Exception as e:
        logger.error(f"Error getting comment analytics: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/scrape/comments', methods=['POST'])
@require_admin
def scrape_comments():
    """Manually trigger comments scraping"""
    try:
        start_time = datetime.utcnow()

        scraper = CommentsScraper()
        results = scraper.scrape_all_comments()

        # Save or update comments in database
        items_new = 0
        items_updated = 0

        for comment_data in results['comments']:
            # DEBUG: Log incoming comment data
            logger.info(f"[ENDPOINT DEBUG] Received comment_data for {comment_data['comment_id']}")
            logger.info(f"[ENDPOINT DEBUG] action_id in comment_data: '{comment_data.get('action_id')}'")
            logger.info(f"[ENDPOINT DEBUG] contact_id: {comment_data.get('contact_id')}, org_id: {comment_data.get('organization_id')}")

            comment = Comment.query.filter_by(comment_id=comment_data['comment_id']).first()

            if comment:
                # Update existing
                logger.info(f"[ENDPOINT DEBUG] Updating existing comment {comment.comment_id}")
                comment.name = comment_data.get('name')
                comment.organization = comment_data.get('organization')
                comment.city = comment_data.get('city')
                comment.state = comment_data.get('state')
                email = comment_data.get('email')
                comment.email = email.lower().strip() if email else None
                comment.comment_text = comment_data.get('comment_text')
                comment.commenter_type = comment_data.get('commenter_type')
                comment.position = comment_data.get('position')
                comment.key_topics = comment_data.get('key_topics')
                comment.contact_id = comment_data.get('contact_id')
                comment.organization_id = comment_data.get('organization_id')
                comment.action_id = comment_data.get('action_id')
                logger.info(f"[ENDPOINT DEBUG] Set comment.action_id to: '{comment.action_id}'")
                comment.updated_at = datetime.utcnow()
                items_updated += 1
            else:
                # Create new
                action_id_value = comment_data.get('action_id')
                logger.info(f"[ENDPOINT DEBUG] Creating new comment {comment_data['comment_id']}")
                logger.info(f"[ENDPOINT DEBUG] action_id value to be saved: '{action_id_value}'")

                email = comment_data.get('email')
                comment = Comment(
                    comment_id=comment_data['comment_id'],
                    action_id=action_id_value,
                    contact_id=comment_data.get('contact_id'),
                    organization_id=comment_data.get('organization_id'),
                    name=comment_data.get('name'),
                    organization=comment_data.get('organization'),
                    city=comment_data.get('city'),
                    state=comment_data.get('state'),
                    email=email.lower().strip() if email else None,
                    commenter_type=comment_data.get('commenter_type'),
                    position=comment_data.get('position'),
                    key_topics=comment_data.get('key_topics'),
                    comment_text=comment_data.get('comment_text'),
                    amendment_phase=comment_data.get('amendment_phase'),
                    source_url=comment_data.get('source_url'),
                    data_source=comment_data.get('data_source'),
                    comment_date=datetime.utcnow()
                )
                logger.info(f"[ENDPOINT DEBUG] Created Comment object with action_id: '{comment.action_id}'")
                db.session.add(comment)
                items_new += 1

        logger.info(f"[ENDPOINT DEBUG] About to commit {items_new} new + {items_updated} updated comments to database")
        db.session.commit()
        logger.info("[ENDPOINT DEBUG] Database commit successful")

        # DEBUG: Verify what's in the database after commit
        logger.info("[ENDPOINT DEBUG] Verifying database state after commit...")
        sample_comments = Comment.query.limit(5).all()
        for c in sample_comments:
            logger.info(f"[ENDPOINT DEBUG] DB verification - comment_id: {c.comment_id}, action_id: '{c.action_id}', contact_id: {c.contact_id}")

        # Count how many have action_id populated
        total_comments = Comment.query.count()
        comments_with_action = Comment.query.filter(Comment.action_id != None).count()
        logger.info(f"[ENDPOINT DEBUG] Total comments: {total_comments}, with action_id: {comments_with_action}")

        # Log the scrape
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        log = ScrapeLog(
            source='comments',
            action_type='scrape_comments',
            status='success' if not results['errors'] else 'partial',
            items_found=results['total_found'],
            items_new=items_new,
            items_updated=items_updated,
            error_message='; '.join([e['error'] for e in results['errors']]) if results['errors'] else None,
            duration_ms=duration_ms,
            completed_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'success': True,
            'itemsFound': results['total_found'],
            'itemsNew': items_new,
            'itemsUpdated': items_updated,
            'bySource': results['by_source'],
            'duration': duration_ms,
            'errors': results['errors']
        })

    except Exception as e:
        logger.error(f"Error in scrape_comments: {e}")
        db.session.rollback()
        return safe_error_response(e)[0], safe_error_response(e)[1]

# ==================== LOGS ENDPOINTS ====================

@bp.route('/logs/scrape')
def get_scrape_logs():
    """Get scrape logs"""
    try:
        limit = request.args.get('limit', 50, type=int)

        logs = ScrapeLog.query.order_by(desc(ScrapeLog.started_at)).limit(limit).all()

        return jsonify({
            'logs': [log.to_dict() for log in logs]
        })

    except Exception as e:
        logger.error(f"Error getting scrape logs: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

# ==================== DOCUMENT ENDPOINTS ====================

@bp.route('/documents')
def get_documents():
    """Search and browse FMP documents"""
    try:
        # Get query parameters
        search_query = request.args.get('q', '')
        document_type = request.args.get('type')
        fmp = request.args.get('fmp')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Build query
        query = """
            SELECT id, document_id, title, document_type, fmp,
                   amendment_number, document_date, publication_date,
                   status, source_url, download_url, summary,
                   keywords, species, topics, page_count, created_at
            FROM fmp_documents
            WHERE 1=1
        """
        params = {}

        # Add search filter
        if search_query:
            query += " AND search_vector @@ plainto_tsquery('english', :search_query)"
            params['search_query'] = search_query

        # Add type filter
        if document_type:
            query += " AND document_type = :document_type"
            params['document_type'] = document_type

        # Add FMP filter
        if fmp:
            query += " AND fmp = :fmp"
            params['fmp'] = fmp

        # Add ordering and pagination
        query += " ORDER BY document_date DESC NULLS LAST, created_at DESC"
        query += " LIMIT :limit OFFSET :offset"
        params['limit'] = limit
        params['offset'] = offset

        result = db.session.execute(text(query), params)
        documents = []

        for row in result:
            documents.append({
                'id': row[0],
                'document_id': row[1],
                'title': row[2],
                'document_type': row[3],
                'fmp': row[4],
                'amendment_number': row[5],
                'document_date': row[6].isoformat() if row[6] else None,
                'publication_date': row[7].isoformat() if row[7] else None,
                'status': row[8],
                'source_url': row[9],
                'download_url': row[10],
                'summary': row[11],
                'keywords': row[12],
                'species': row[13],
                'topics': row[14],
                'page_count': row[15],
                'created_at': row[16].isoformat() if row[16] else None
            })

        # Get total count
        count_query = "SELECT COUNT(*) FROM fmp_documents WHERE 1=1"
        count_params = {}
        if search_query:
            count_query += " AND search_vector @@ plainto_tsquery('english', :search_query)"
            count_params['search_query'] = search_query
        if document_type:
            count_query += " AND document_type = :document_type"
            count_params['document_type'] = document_type
        if fmp:
            count_query += " AND fmp = :fmp"
            count_params['fmp'] = fmp

        count_result = db.session.execute(text(count_query), count_params)
        total = count_result.scalar()

        return jsonify({
            'documents': documents,
            'total': total,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/documents/<document_id>')
def get_document(document_id):
    """Get single document with full details"""
    try:
        query = """
            SELECT id, document_id, title, document_type, fmp,
                   amendment_number, document_date, publication_date, effective_date,
                   status, source_url, download_url, description, summary,
                   keywords, species, topics, file_size_bytes, page_count,
                   processed, indexed, metadata, created_at, updated_at
            FROM fmp_documents
            WHERE document_id = :document_id
        """

        result = db.session.execute(text(query), {'document_id': document_id})
        row = result.fetchone()

        if not row:
            return jsonify({'error': 'Document not found'}), 404

        document = {
            'id': row[0],
            'document_id': row[1],
            'title': row[2],
            'document_type': row[3],
            'fmp': row[4],
            'amendment_number': row[5],
            'document_date': row[6].isoformat() if row[6] else None,
            'publication_date': row[7].isoformat() if row[7] else None,
            'effective_date': row[8].isoformat() if row[8] else None,
            'status': row[9],
            'source_url': row[10],
            'download_url': row[11],
            'description': row[12],
            'summary': row[13],
            'keywords': row[14],
            'species': row[15],
            'topics': row[16],
            'file_size_bytes': row[17],
            'page_count': row[18],
            'processed': row[19],
            'indexed': row[20],
            'metadata': row[21],
            'created_at': row[22].isoformat() if row[22] else None,
            'updated_at': row[23].isoformat() if row[23] else None
        }

        # Get document chunks for this document
        chunks_query = """
            SELECT chunk_index, chunk_text, chunk_type, section_title, page_number
            FROM document_chunks
            WHERE document_id = :document_id
            ORDER BY chunk_index
        """
        chunks_result = db.session.execute(text(chunks_query), {'document_id': document_id})

        document['chunks'] = []
        for chunk_row in chunks_result:
            document['chunks'].append({
                'chunk_index': chunk_row[0],
                'chunk_text': chunk_row[1],
                'chunk_type': chunk_row[2],
                'section_title': chunk_row[3],
                'page_number': chunk_row[4]
            })

        return jsonify(document)

    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/documents/stats')
def get_document_stats():
    """Get document statistics"""
    try:
        stats_query = """
            SELECT
                COUNT(*) as total_documents,
                COUNT(DISTINCT fmp) as total_fmps,
                COUNT(DISTINCT document_type) as total_types,
                SUM(CASE WHEN processed = true THEN 1 ELSE 0 END) as processed_count,
                SUM(CASE WHEN indexed = true THEN 1 ELSE 0 END) as indexed_count,
                SUM(page_count) as total_pages,
                SUM(file_size_bytes) as total_bytes
            FROM fmp_documents
        """

        result = db.session.execute(text(stats_query))
        row = result.fetchone()

        # Get documents by type
        type_query = """
            SELECT document_type, COUNT(*) as count
            FROM fmp_documents
            WHERE document_type IS NOT NULL
            GROUP BY document_type
            ORDER BY count DESC
        """
        type_result = db.session.execute(text(type_query))
        by_type = {row[0]: row[1] for row in type_result}

        # Get documents by FMP
        fmp_query = """
            SELECT fmp, COUNT(*) as count
            FROM fmp_documents
            WHERE fmp IS NOT NULL
            GROUP BY fmp
            ORDER BY count DESC
        """
        fmp_result = db.session.execute(text(fmp_query))
        by_fmp = {row[0]: row[1] for row in fmp_result}

        return jsonify({
            'total_documents': row[0],
            'total_fmps': row[1],
            'total_types': row[2],
            'processed_count': row[3],
            'indexed_count': row[4],
            'total_pages': row[5],
            'total_bytes': row[6],
            'by_type': by_type,
            'by_fmp': by_fmp
        })

    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/scrape/documents/briefing-books', methods=['POST'])
@require_admin
def scrape_briefing_books():
    """Manually trigger briefing books scraping"""
    try:
        start_time = datetime.utcnow()

        # Get optional parameters
        data = request.get_json() or {}
        limit = data.get('limit', 10)  # Default to first 10 briefing books

        scraper = BriefingBooksScraper()
        results = scraper.scrape_briefing_books(limit=limit)

        # Log the scrape
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        log = ScrapeLog(
            source='fmp_documents',
            action_type='scrape_briefing_books',
            status='success' if results.get('documents_queued', 0) > 0 else 'warning',
            items_found=results.get('documents_queued', 0),
            items_new=results.get('documents_queued', 0),
            items_updated=0,
            error_message=results.get('errors') if results.get('errors') else None,
            duration_ms=duration_ms,
            completed_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'success': True,
            'booksFound': results.get('books_found', 0),
            'documentsQueued': results.get('documents_queued', 0),
            'duration': duration_ms,
            'errors': results.get('errors', [])
        })

    except Exception as e:
        logger.error(f"Error in scrape_briefing_books: {e}")
        db.session.rollback()
        return safe_error_response(e)[0], safe_error_response(e)[1]

@bp.route('/scrape/queue/status')
def get_scrape_queue_status():
    """Get status of document scrape queue"""
    try:
        status_query = """
            SELECT
                status,
                COUNT(*) as count,
                SUM(CASE WHEN status = 'failed' THEN attempts ELSE 0 END) as total_attempts
            FROM document_scrape_queue
            GROUP BY status
        """

        result = db.session.execute(text(status_query))
        status_counts = {}
        for row in result:
            status_counts[row[0]] = {
                'count': row[1],
                'total_attempts': row[2]
            }

        # Get recent queue items
        recent_query = """
            SELECT url, document_type, fmp, status, attempts, priority, created_at, updated_at
            FROM document_scrape_queue
            ORDER BY updated_at DESC
            LIMIT 20
        """
        recent_result = db.session.execute(text(recent_query))

        recent_items = []
        for row in recent_result:
            recent_items.append({
                'url': row[0],
                'document_type': row[1],
                'fmp': row[2],
                'status': row[3],
                'attempts': row[4],
                'priority': row[5],
                'created_at': row[6].isoformat() if row[6] else None,
                'updated_at': row[7].isoformat() if row[7] else None
            })

        return jsonify({
            'status_counts': status_counts,
            'recent_items': recent_items
        })

    except Exception as e:
        logger.error(f"Error getting scrape queue status: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/comments/fix-links', methods=['POST'])
def fix_comment_links():
    """
    Fix comment-action links by re-matching comments to actions.
    Also sets FMP on actions that are missing it.
    """
    try:
        fixed_count = 0
        fmp_updated = 0

        # First, fix the Coral 11 / Shrimp 12 action to have proper FMP
        coral_shrimp_action = Action.query.filter(
            Action.action_id == 'coral-11-shrimp-12'
        ).first()

        if coral_shrimp_action and not coral_shrimp_action.fmp:
            coral_shrimp_action.fmp = 'Coral, Shrimp'
            fmp_updated += 1
            logger.info(f"Set FMP for coral-11-shrimp-12 to 'Coral, Shrimp'")

        # Get all comments that have 'general-comment' as action_id
        general_comments = Comment.query.filter(
            Comment.action_id == 'general-comment'
        ).all()

        logger.info(f"Found {len(general_comments)} comments with 'general-comment' action_id")

        # Try to match each comment to a proper action based on data source
        # Comments from the Coral/Shrimp sheet should link to coral-11-shrimp-12
        for comment in general_comments:
            if comment.data_source and 'Comprehensive' in (comment.data_source or ''):
                # This is from the main comprehensive sheet
                if coral_shrimp_action:
                    comment.action_id = coral_shrimp_action.action_id
                    fixed_count += 1
            elif comment.data_source and ('Additional 1' in comment.data_source or 'Additional 2' in comment.data_source):
                # These sheets also have Coral/Shrimp comments based on the URL
                if coral_shrimp_action:
                    comment.action_id = coral_shrimp_action.action_id
                    fixed_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Fixed {fixed_count} comment links, updated FMP on {fmp_updated} actions',
            'fixed_count': fixed_count,
            'fmp_updated': fmp_updated
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error fixing comment links: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


# ==================== FEEDBACK ENDPOINT ====================

@bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback - stores in database and logs for review (anonymous allowed)"""
    try:
        data = request.get_json()

        if not data or not data.get('feedback'):
            return jsonify({'success': False, 'error': 'Feedback is required'}), 400

        feedback_text = data.get('feedback', '').strip()
        component = data.get('component', 'General')
        url = data.get('url', '')
        user_email = data.get('userEmail', session.get('email', 'anonymous'))
        user_name = data.get('userName', session.get('name', 'Anonymous'))

        # Validate feedback length
        if len(feedback_text) > 5000:
            return jsonify({'success': False, 'error': 'Feedback too long (max 5000 characters)'}), 400

        # Store feedback in database
        result = db.session.execute(text("""
            INSERT INTO user_feedback (user_email, user_name, component, url, feedback, created_at)
            VALUES (:email, :name, :component, :url, :feedback, :created_at)
            RETURNING id
        """), {
            'email': user_email,
            'name': user_name,
            'component': component,
            'url': url,
            'feedback': feedback_text,
            'created_at': datetime.utcnow()
        })

        feedback_id = result.fetchone()[0]
        db.session.commit()

        logger.info(f"Feedback received from {user_email}: {feedback_text[:100]}...")

        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback_id
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error submitting feedback: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/feedback/all', methods=['GET'])
@require_role('admin', 'super_admin')
def get_all_feedback():
    """Get all feedback submissions - admin only"""
    try:

        # Get query parameters
        status_filter = request.args.get('status', 'all')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Build query
        query = """
            SELECT id, user_email, user_name, component, url, feedback,
                   status, admin_notes, created_at, reviewed_at, reviewed_by
            FROM user_feedback
        """

        params = {}
        if status_filter != 'all':
            query += " WHERE status = :status"
            params['status'] = status_filter

        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params['limit'] = limit
        params['offset'] = offset

        result = db.session.execute(text(query), params)
        feedback_items = []

        for row in result:
            feedback_items.append({
                'id': row[0],
                'user_email': row[1],
                'user_name': row[2],
                'component': row[3],
                'url': row[4],
                'feedback': row[5],
                'status': row[6],
                'admin_notes': row[7],
                'created_at': row[8].isoformat() if row[8] else None,
                'reviewed_at': row[9].isoformat() if row[9] else None,
                'reviewed_by': row[10]
            })

        # Get total count
        count_query = "SELECT COUNT(*) FROM user_feedback"
        if status_filter != 'all':
            count_query += " WHERE status = :status"
        count_result = db.session.execute(text(count_query), {'status': status_filter} if status_filter != 'all' else {})
        total_count = count_result.scalar()

        return jsonify({
            'success': True,
            'feedback': feedback_items,
            'total': total_count,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"Error fetching feedback: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/feedback/<int:feedback_id>', methods=['PATCH'])
@require_role('admin', 'super_admin')
def update_feedback_status(feedback_id):
    """Update feedback status and add admin notes - admin only"""
    try:

        data = request.get_json()
        new_status = data.get('status')
        admin_notes = data.get('admin_notes')

        if not new_status:
            return jsonify({'error': 'Status is required'}), 400

        # Valid statuses
        valid_statuses = ['new', 'in_review', 'resolved', 'archived']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400

        # Update feedback
        update_query = """
            UPDATE user_feedback
            SET status = :status,
                admin_notes = :admin_notes,
                reviewed_at = :reviewed_at,
                reviewed_by = :reviewed_by
            WHERE id = :id
            RETURNING id, status
        """

        result = db.session.execute(text(update_query), {
            'status': new_status,
            'admin_notes': admin_notes,
            'reviewed_at': datetime.utcnow(),
            'reviewed_by': session.get('email'),
            'id': feedback_id
        })

        updated = result.fetchone()
        if not updated:
            return jsonify({'error': 'Feedback not found'}), 404

        db.session.commit()

        logger.info(f"Feedback {feedback_id} updated to {new_status} by {session.get('email')}")

        return jsonify({
            'success': True,
            'message': 'Feedback updated successfully',
            'feedback_id': updated[0],
            'status': updated[1]
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating feedback: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/feedback/<int:feedback_id>', methods=['DELETE'])
@require_role('admin', 'super_admin')
def delete_feedback(feedback_id):
    """Delete feedback - admin only"""
    try:
        # Delete feedback
        delete_query = """
            DELETE FROM user_feedback
            WHERE id = :id
            RETURNING id
        """

        result = db.session.execute(text(delete_query), {'id': feedback_id})
        deleted = result.fetchone()

        if not deleted:
            return jsonify({'error': 'Feedback not found'}), 404

        db.session.commit()

        logger.info(f"Feedback {feedback_id} deleted by {session.get('email')}")

        return jsonify({
            'success': True,
            'message': 'Feedback deleted successfully',
            'feedback_id': deleted[0]
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting feedback: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/feedback/stats', methods=['GET'])
@require_role('admin', 'super_admin')
def get_feedback_stats():
    """Get feedback statistics - admin only"""
    try:

        # Get status counts
        status_query = """
            SELECT status, COUNT(*) as count
            FROM user_feedback
            GROUP BY status
        """
        status_result = db.session.execute(text(status_query))
        status_counts = {row[0]: row[1] for row in status_result}

        # Get component counts
        component_query = """
            SELECT component, COUNT(*) as count
            FROM user_feedback
            GROUP BY component
            ORDER BY count DESC
            LIMIT 10
        """
        component_result = db.session.execute(text(component_query))
        component_counts = {row[0]: row[1] for row in component_result}

        # Get recent feedback count (last 7 days)
        recent_query = """
            SELECT COUNT(*) FROM user_feedback
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """
        recent_result = db.session.execute(text(recent_query))
        recent_count = recent_result.scalar()

        # Get total count
        total_query = "SELECT COUNT(*) FROM user_feedback"
        total_result = db.session.execute(text(total_query))
        total_count = total_result.scalar()

        return jsonify({
            'success': True,
            'stats': {
                'total': total_count,
                'recent': recent_count,
                'by_status': status_counts,
                'by_component': component_counts
            }
        })

    except Exception as e:
        logger.error(f"Error fetching feedback stats: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]

# ==================== WORKPLAN ENDPOINTS ====================

@bp.route('/workplan/upload', methods=['POST'])
@require_auth
def upload_workplan():
    """
    Upload and parse workplan Excel file
    Creates a new workplan version with items and milestones
    """
    try:
        import os
        import tempfile
        from werkzeug.utils import secure_filename
        from src.utils.workplan_parser import parse_workplan_file
        from src.models.workplan import WorkplanVersion, WorkplanItem, WorkplanMilestone, WorkplanUploadLog

        start_time = time.time()

        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Get metadata from form
        version_name = request.form.get('version_name')
        quarter = request.form.get('quarter')
        fiscal_year = request.form.get('fiscal_year', type=int)

        if not version_name:
            return jsonify({'success': False, 'error': 'Version name required'}), 400

        # Check if version name already exists
        existing = WorkplanVersion.query.filter_by(version_name=version_name).first()
        if existing:
            return jsonify({'success': False, 'error': f'Version "{version_name}" already exists'}), 400

        # Save file temporarily
        filename = secure_filename(file.filename)
        file_size = 0

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            file.save(tmp_file.name)
            tmp_file.seek(0, os.SEEK_END)
            file_size = tmp_file.tell()
            temp_path = tmp_file.name

        try:
            # Parse the Excel file
            logger.info(f"Parsing workplan file: {filename}")
            parsed_data = parse_workplan_file(temp_path)

            # Create workplan version
            version = WorkplanVersion(
                version_name=version_name,
                source_file_name=filename,
                upload_type='manual_upload',
                uploaded_by_user_id=session.get('user_id'),
                quarter=quarter,
                fiscal_year=fiscal_year,
                created_at=datetime.utcnow(),
                is_active=True
            )
            db.session.add(version)
            db.session.flush()  # Get version.id

            items_created = 0
            milestones_created = 0

            # Create workplan items and milestones
            for item_data in parsed_data.get('items', []):
                # Map parser fields to model fields
                workplan_item = WorkplanItem(
                    workplan_version_id=version.id,
                    amendment_id=item_data.get('amendment_number', ''),
                    topic=item_data.get('amendment_name', ''),
                    status=item_data.get('category', 'other').upper(),
                    lead_staff=item_data.get('safmc_lead'),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(workplan_item)
                db.session.flush()  # Get workplan_item.id
                items_created += 1

                # Create milestones for this item
                for milestone_data in item_data.get('milestones', []):
                    milestone = WorkplanMilestone(
                        workplan_item_id=workplan_item.id,
                        milestone_type=milestone_data.get('status_code', ''),
                        scheduled_date=datetime.fromisoformat(milestone_data['quarter_date']) if milestone_data.get('quarter_date') else None,
                        scheduled_meeting=milestone_data.get('quarter', ''),
                        is_completed=milestone_data.get('is_complete', False),
                        notes=milestone_data.get('status_description'),
                        created_at=datetime.utcnow()
                    )
                    db.session.add(milestone)
                    milestones_created += 1

            # Create upload log
            duration_ms = int((time.time() - start_time) * 1000)
            upload_log = WorkplanUploadLog(
                workplan_version_id=version.id,
                upload_type='manual_upload',
                file_name=filename,
                file_size_bytes=file_size,
                uploaded_by_user_id=session.get('user_id'),
                status='success',
                items_found=len(parsed_data.get('items', [])),
                items_created=items_created,
                items_updated=0,
                milestones_created=milestones_created,
                processing_duration_ms=duration_ms,
                created_at=datetime.utcnow()
            )
            db.session.add(upload_log)

            # Commit all changes
            db.session.commit()

            logger.info(f"Successfully imported workplan: {version_name} ({items_created} items, {milestones_created} milestones)")

            return jsonify({
                'success': True,
                'version': version.to_dict(),
                'stats': {
                    'itemsCreated': items_created,
                    'milestonesCreated': milestones_created,
                    'processingTimeMs': duration_ms
                }
            })

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error uploading workplan: {e}")

        # Log failed upload
        try:
            failed_log = WorkplanUploadLog(
                upload_type='manual_upload',
                file_name=filename if 'filename' in locals() else 'unknown',
                uploaded_by_user_id=session.get('user_id'),
                status='failed',
                error_message=str(e),
                created_at=datetime.utcnow()
            )
            db.session.add(failed_log)
            db.session.commit()
        except:
            pass

        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/workplan/versions')
def get_workplan_versions():
    """Get all workplan versions"""
    try:
        versions = WorkplanVersion.query.order_by(desc(WorkplanVersion.created_at)).all()

        return jsonify({
            'success': True,
            'versions': [v.to_dict() for v in versions]
        })

    except Exception as e:
        logger.error(f"Error fetching workplan versions: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/workplan/versions/<int:version_id>')
def get_workplan_version(version_id):
    """Get specific workplan version with all items and milestones"""
    try:
        from src.models.workplan import WorkplanVersion, WorkplanItem

        version = WorkplanVersion.query.get(version_id)
        if not version:
            return jsonify({'success': False, 'error': 'Version not found'}), 404

        # Get all items with milestones
        items = WorkplanItem.query.filter_by(workplan_version_id=version_id).all()

        return jsonify({
            'success': True,
            'version': version.to_dict(),
            'items': [item.to_dict(include_milestones=True) for item in items]
        })

    except Exception as e:
        logger.error(f"Error fetching workplan version: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/workplan/items')
def get_workplan_items():
    """Get workplan items with optional filtering"""
    try:
        from src.models.workplan import WorkplanItem, WorkplanVersion

        # Get query parameters
        version_id = request.args.get('version_id', type=int)
        status = request.args.get('status')

        # Build query
        query = WorkplanItem.query

        # Join with version to get active items
        query = query.join(WorkplanVersion)

        if version_id:
            query = query.filter(WorkplanItem.workplan_version_id == version_id)
        else:
            # Default to active version
            query = query.filter(WorkplanVersion.is_active == True)

        if status:
            query = query.filter(WorkplanItem.status == status.upper())

        items = query.all()

        return jsonify({
            'success': True,
            'items': [item.to_dict(include_milestones=True) for item in items]
        })

    except Exception as e:
        logger.error(f"Error fetching workplan items: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/workplan/items/<int:item_id>')
def get_workplan_item(item_id):
    """Get specific workplan item with details"""
    try:
        from src.models.workplan import WorkplanItem

        item = WorkplanItem.query.get(item_id)
        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404

        return jsonify({
            'success': True,
            'item': item.to_dict(include_milestones=True)
        })

    except Exception as e:
        logger.error(f"Error fetching workplan item: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/workplan/upload-history')
def get_workplan_upload_history():
    """Get upload history logs"""
    try:
        from src.models.workplan import WorkplanUploadLog

        limit = request.args.get('limit', 50, type=int)
        limit = max(1, min(limit, 200))

        logs = WorkplanUploadLog.query.order_by(desc(WorkplanUploadLog.created_at)).limit(limit).all()

        return jsonify({
            'success': True,
            'uploads': [log.to_dict() for log in logs]
        })

    except Exception as e:
        logger.error(f"Error fetching upload history: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]


@bp.route('/workplan/milestone-types')
def get_milestone_types():
    """Get all milestone type codes and descriptions"""
    try:
        from src.models.workplan import MilestoneType

        types = MilestoneType.query.order_by(MilestoneType.typical_order).all()

        return jsonify({
            'success': True,
            'milestoneTypes': [t.to_dict() for t in types]
        })

    except Exception as e:
        logger.error(f"Error fetching milestone types: {e}")
        return safe_error_response(e)[0], safe_error_response(e)[1]
