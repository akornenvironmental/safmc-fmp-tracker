"""
API Routes for SAFMC FMP Tracker
Provides REST API endpoints for data access and management
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import logging

from src.config.extensions import db
from src.models.action import Action
from src.models.meeting import Meeting
from src.models.comment import Comment
from src.models.milestone import Milestone
from src.models.scrape_log import ScrapeLog
from src.scrapers.amendments_scraper import AmendmentsScraper
from src.scrapers.meetings_scraper import MeetingsScraper
from src.scrapers.comments_scraper import CommentsScraper
from src.services.ai_service import AIService

bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Initialize services
ai_service = AIService()

# ==================== DASHBOARD ENDPOINTS ====================

@bp.route('/dashboard/stats')
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
        return jsonify({'error': str(e)}), 500

@bp.route('/dashboard/recent-amendments')
def recent_amendments():
    """Get recent amendments"""
    try:
        limit = request.args.get('limit', 10, type=int)

        actions = Action.query.order_by(desc(Action.updated_at)).limit(limit).all()

        return jsonify({
            'success': True,
            'actions': [action.to_dict() for action in actions]
        })

    except Exception as e:
        logger.error(f"Error getting recent amendments: {e}")
        return jsonify({'error': str(e)}), 500

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
        return jsonify({'error': str(e)}), 500

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
        return jsonify({'error': str(e)}), 500

# ==================== MEETINGS ENDPOINTS ====================

@bp.route('/meetings')
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
        return jsonify({'error': str(e)}), 500

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
        return jsonify({'error': str(e)}), 500

# ==================== COMMENTS ENDPOINTS ====================

@bp.route('/comments')
def get_comments():
    """Get all comments"""
    try:
        action_id = request.args.get('action_id')

        query = Comment.query

        if action_id:
            query = query.filter(Comment.action_id == action_id)

        comments = query.order_by(desc(Comment.comment_date)).all()

        return jsonify({
            'success': True,
            'comments': [comment.to_dict() for comment in comments],
            'total': len(comments)
        })

    except Exception as e:
        logger.error(f"Error getting comments: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== SCRAPING ENDPOINTS ====================

@bp.route('/scrape/amendments', methods=['POST'])
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
                action.description = amendment_data['description']
                action.lead_staff = amendment_data['lead_staff']
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
                    description=amendment_data['description'],
                    lead_staff=amendment_data['lead_staff'],
                    source_url=amendment_data['source_url'],
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
        return jsonify({'error': str(e)}), 500

@bp.route('/scrape/meetings', methods=['POST'])
def scrape_meetings():
    """Manually trigger meetings scraping"""
    try:
        start_time = datetime.utcnow()

        scraper = MeetingsScraper()
        results = scraper.scrape_meetings()

        # Save or update meetings in database
        items_new = 0
        items_updated = 0

        for meeting_data in results['meetings']:
            meeting = Meeting.query.filter_by(meeting_id=meeting_data['meeting_id']).first()

            if meeting:
                # Update existing
                meeting.title = meeting_data['title']
                meeting.type = meeting_data['type']
                meeting.start_date = meeting_data['start_date']
                meeting.location = meeting_data['location']
                meeting.description = meeting_data['description']
                meeting.agenda_url = meeting_data.get('agenda_url')
                meeting.last_scraped = datetime.utcnow()
                meeting.updated_at = datetime.utcnow()
                items_updated += 1
            else:
                # Create new
                meeting = Meeting(
                    meeting_id=meeting_data['meeting_id'],
                    title=meeting_data['title'],
                    type=meeting_data['type'],
                    start_date=meeting_data['start_date'],
                    end_date=meeting_data['end_date'],
                    location=meeting_data['location'],
                    description=meeting_data['description'],
                    agenda_url=meeting_data.get('agenda_url'),
                    source_url=meeting_data['source_url'],
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
        return jsonify({'error': str(e)}), 500

@bp.route('/scrape/all', methods=['POST'])
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
        return jsonify({'error': str(e)}), 500

# ==================== AI QUERY ENDPOINTS ====================

@bp.route('/ai/query', methods=['POST'])
def ai_query():
    """Query the AI system"""
    try:
        data = request.get_json()
        question = data.get('question')

        if not question:
            return jsonify({'error': 'Question is required'}), 400

        # Get context from database
        actions = Action.query.order_by(desc(Action.updated_at)).limit(10).all()
        context = {
            'actions': [a.to_dict() for a in actions]
        }

        result = ai_service.query(question, context)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in AI query: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/ai/analyze', methods=['POST'])
def ai_analyze():
    """Analyze FMP patterns"""
    try:
        actions = Action.query.all()
        actions_data = [a.to_dict() for a in actions]

        result = ai_service.analyze_patterns(actions_data)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/ai/report', methods=['POST'])
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
        return jsonify({'error': str(e)}), 500

@bp.route('/ai/search', methods=['POST'])
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
        return jsonify({'error': str(e)}), 500

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
        return jsonify({'error': str(e)}), 500

@bp.route('/scrape/comments', methods=['POST'])
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
            comment = Comment.query.filter_by(comment_id=comment_data['comment_id']).first()

            if comment:
                # Update existing
                comment.name = comment_data.get('name')
                comment.organization = comment_data.get('organization')
                comment.city = comment_data.get('city')
                comment.state = comment_data.get('state')
                comment.email = comment_data.get('email')
                comment.comment_text = comment_data.get('comment_text')
                comment.commenter_type = comment_data.get('commenter_type')
                comment.position = comment_data.get('position')
                comment.key_topics = comment_data.get('key_topics')
                comment.updated_at = datetime.utcnow()
                items_updated += 1
            else:
                # Create new
                comment = Comment(
                    comment_id=comment_data['comment_id'],
                    action_id=comment_data.get('amendment_id'),
                    name=comment_data.get('name'),
                    organization=comment_data.get('organization'),
                    city=comment_data.get('city'),
                    state=comment_data.get('state'),
                    email=comment_data.get('email'),
                    commenter_type=comment_data.get('commenter_type'),
                    position=comment_data.get('position'),
                    key_topics=comment_data.get('key_topics'),
                    comment_text=comment_data.get('comment_text'),
                    amendment_phase=comment_data.get('amendment_phase'),
                    source_url=comment_data.get('source_url'),
                    data_source=comment_data.get('data_source'),
                    comment_date=datetime.utcnow()
                )
                db.session.add(comment)
                items_new += 1

        db.session.commit()

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
        return jsonify({'error': str(e)}), 500

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
        return jsonify({'error': str(e)}), 500
