"""
CMOD (Council Member Ongoing Development) Workshop Routes
API endpoints for CMOD workshops, sessions, documents, and topic tracking
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import func, desc, or_
from datetime import datetime
import logging

from src.config.extensions import db
from src.models.cmod import CMODWorkshop, CMODSession, CMODDocument, CMODTopicTracking
from src.middleware.auth_middleware import require_auth, require_admin, log_activity

logger = logging.getLogger(__name__)

bp = Blueprint('cmod', __name__, url_prefix='/api/cmod')


# ==================== CMOD WORKSHOPS ====================

@bp.route('/workshops', methods=['GET'])
@require_auth
def get_cmod_workshops():
    """Get all CMOD workshops with filtering"""
    try:
        # Get query parameters
        status = request.args.get('status', '').strip()
        year = request.args.get('year', type=int)
        host_council = request.args.get('host_council', '').strip()
        search = request.args.get('search', '').strip()

        # Build query
        query = CMODWorkshop.query

        if status:
            query = query.filter(CMODWorkshop.status == status)

        if year:
            query = query.filter(CMODWorkshop.year == year)

        if host_council:
            query = query.filter(CMODWorkshop.host_council.ilike(f'%{host_council}%'))

        if search:
            query = query.filter(
                or_(
                    CMODWorkshop.title.ilike(f'%{search}%'),
                    CMODWorkshop.theme.ilike(f'%{search}%'),
                    CMODWorkshop.description.ilike(f'%{search}%')
                )
            )

        # Order by year descending
        query = query.order_by(CMODWorkshop.year.desc())

        workshops = query.all()

        log_activity(
            activity_type='cmod.workshops_viewed',
            description='Viewed CMOD workshops',
            category='cmod'
        )

        return jsonify({
            'success': True,
            'workshops': [workshop.to_dict() for workshop in workshops],
            'count': len(workshops)
        })

    except Exception as e:
        logger.error(f"Error getting CMOD workshops: {e}")
        return jsonify({'error': 'Failed to get CMOD workshops'}), 500


@bp.route('/workshops/<workshop_id>', methods=['GET'])
@require_auth
def get_cmod_workshop(workshop_id):
    """Get single CMOD workshop with sessions"""
    try:
        workshop = CMODWorkshop.query.filter_by(id=workshop_id).first()

        if not workshop:
            return jsonify({'error': 'CMOD workshop not found'}), 404

        # Get sessions for this workshop
        sessions = CMODSession.query.filter_by(
            workshop_id=workshop_id
        ).order_by(CMODSession.session_order).all()

        # Get documents for this workshop
        documents = CMODDocument.query.filter_by(
            workshop_id=workshop_id
        ).all()

        log_activity(
            activity_type='cmod.workshop_viewed',
            description=f'Viewed CMOD workshop: {workshop.title}',
            category='cmod',
            resource_type='cmod_workshop',
            resource_id=workshop_id,
            resource_name=workshop.title
        )

        return jsonify({
            'success': True,
            'workshop': workshop.to_dict(),
            'sessions': [session.to_dict() for session in sessions],
            'documents': [doc.to_dict() for doc in documents]
        })

    except Exception as e:
        logger.error(f"Error getting CMOD workshop: {e}")
        return jsonify({'error': 'Failed to get CMOD workshop'}), 500


# ==================== CMOD SESSIONS ====================

@bp.route('/sessions', methods=['GET'])
@require_auth
def get_cmod_sessions():
    """Get CMOD sessions with filtering"""
    try:
        # Get query parameters
        workshop_id = request.args.get('workshop_id', '').strip()
        session_type = request.args.get('session_type', '').strip()
        topic = request.args.get('topic', '').strip()

        # Build query
        query = CMODSession.query

        if workshop_id:
            query = query.filter(CMODSession.workshop_id == workshop_id)

        if session_type:
            query = query.filter(CMODSession.session_type == session_type)

        if topic:
            query = query.filter(CMODSession.topics.contains([topic]))

        # Order by workshop and session order
        query = query.join(CMODWorkshop).order_by(
            CMODWorkshop.year.desc(),
            CMODSession.session_order
        )

        sessions = query.all()

        log_activity(
            activity_type='cmod.sessions_viewed',
            description='Viewed CMOD sessions',
            category='cmod'
        )

        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions],
            'count': len(sessions)
        })

    except Exception as e:
        logger.error(f"Error getting CMOD sessions: {e}")
        return jsonify({'error': 'Failed to get CMOD sessions'}), 500


# ==================== CMOD DOCUMENTS ====================

@bp.route('/documents', methods=['GET'])
@require_auth
def get_cmod_documents():
    """Get CMOD documents with filtering"""
    try:
        # Get query parameters
        workshop_id = request.args.get('workshop_id', '').strip()
        document_type = request.args.get('document_type', '').strip()
        council_source = request.args.get('council_source', '').strip()

        # Build query
        query = CMODDocument.query

        if workshop_id:
            query = query.filter(CMODDocument.workshop_id == workshop_id)

        if document_type:
            query = query.filter(CMODDocument.document_type == document_type)

        if council_source:
            query = query.filter(CMODDocument.council_source == council_source)

        # Order by created date descending
        query = query.order_by(CMODDocument.created_at.desc())

        documents = query.all()

        log_activity(
            activity_type='cmod.documents_viewed',
            description='Viewed CMOD documents',
            category='cmod'
        )

        return jsonify({
            'success': True,
            'documents': [doc.to_dict() for doc in documents],
            'count': len(documents)
        })

    except Exception as e:
        logger.error(f"Error getting CMOD documents: {e}")
        return jsonify({'error': 'Failed to get CMOD documents'}), 500


# ==================== CMOD TOPIC TRACKING ====================

@bp.route('/topics', methods=['GET'])
@require_auth
def get_cmod_topics():
    """Get CMOD topic tracking with filtering"""
    try:
        # Get query parameters
        workshop_id = request.args.get('workshop_id', '').strip()
        council_name = request.args.get('council_name', '').strip()
        implementation_status = request.args.get('implementation_status', '').strip()
        topic = request.args.get('topic', '').strip()

        # Build query
        query = CMODTopicTracking.query

        if workshop_id:
            query = query.filter(CMODTopicTracking.workshop_id == workshop_id)

        if council_name:
            query = query.filter(CMODTopicTracking.council_name == council_name)

        if implementation_status:
            query = query.filter(CMODTopicTracking.implementation_status == implementation_status)

        if topic:
            query = query.filter(CMODTopicTracking.topic.ilike(f'%{topic}%'))

        # Order by updated date descending
        query = query.order_by(CMODTopicTracking.updated_at.desc())

        topics = query.all()

        log_activity(
            activity_type='cmod.topics_viewed',
            description='Viewed CMOD topic tracking',
            category='cmod'
        )

        return jsonify({
            'success': True,
            'topics': [topic.to_dict() for topic in topics],
            'count': len(topics)
        })

    except Exception as e:
        logger.error(f"Error getting CMOD topics: {e}")
        return jsonify({'error': 'Failed to get CMOD topics'}), 500


@bp.route('/topics/<topic_id>', methods=['GET'])
@require_auth
def get_cmod_topic(topic_id):
    """Get single CMOD topic tracking record"""
    try:
        topic = CMODTopicTracking.query.filter_by(id=topic_id).first()

        if not topic:
            return jsonify({'error': 'CMOD topic not found'}), 404

        log_activity(
            activity_type='cmod.topic_viewed',
            description=f'Viewed CMOD topic: {topic.topic}',
            category='cmod',
            resource_type='cmod_topic',
            resource_id=topic_id,
            resource_name=topic.topic
        )

        return jsonify({
            'success': True,
            'topic': topic.to_dict()
        })

    except Exception as e:
        logger.error(f"Error getting CMOD topic: {e}")
        return jsonify({'error': 'Failed to get CMOD topic'}), 500


# ==================== CMOD ANALYTICS ====================

@bp.route('/analytics', methods=['GET'])
@require_auth
def get_cmod_analytics():
    """Get CMOD analytics and insights"""
    try:
        # Total workshops
        total_workshops = CMODWorkshop.query.count()
        completed_workshops = CMODWorkshop.query.filter_by(status='completed').count()
        scheduled_workshops = CMODWorkshop.query.filter_by(status='scheduled').count()

        # Workshops by year
        workshops_by_year = db.session.query(
            CMODWorkshop.year,
            func.count(CMODWorkshop.id).label('count')
        ).group_by(CMODWorkshop.year).order_by(CMODWorkshop.year.desc()).all()

        # Workshops by host council
        workshops_by_council = db.session.query(
            CMODWorkshop.host_council,
            func.count(CMODWorkshop.id).label('count')
        ).group_by(CMODWorkshop.host_council).order_by(desc('count')).all()

        # Top focus areas across all workshops
        from sqlalchemy import text
        focus_areas_query = text("""
            SELECT UNNEST(focus_areas) as focus_area, COUNT(*) as count
            FROM cmod_workshops
            WHERE focus_areas IS NOT NULL
            GROUP BY UNNEST(focus_areas)
            ORDER BY count DESC
            LIMIT 10
        """)
        focus_areas_result = db.session.execute(focus_areas_query)
        top_focus_areas = [{'focus_area': row[0], 'count': row[1]} for row in focus_areas_result]

        # Session types distribution
        sessions_by_type = db.session.query(
            CMODSession.session_type,
            func.count(CMODSession.id).label('count')
        ).group_by(CMODSession.session_type).order_by(desc('count')).all()

        # Topic implementation status
        topics_by_status = db.session.query(
            CMODTopicTracking.implementation_status,
            func.count(CMODTopicTracking.id).label('count')
        ).group_by(CMODTopicTracking.implementation_status).all()

        # Topics by council
        topics_by_council = db.session.query(
            CMODTopicTracking.council_name,
            func.count(CMODTopicTracking.id).label('count')
        ).filter(
            CMODTopicTracking.council_name.isnot(None)
        ).group_by(CMODTopicTracking.council_name).order_by(desc('count')).all()

        # Upcoming workshops
        upcoming_workshops = CMODWorkshop.query.filter(
            CMODWorkshop.start_date >= datetime.now(),
            CMODWorkshop.status == 'scheduled'
        ).order_by(CMODWorkshop.start_date).all()

        log_activity(
            activity_type='cmod.analytics_viewed',
            description='Viewed CMOD analytics',
            category='cmod'
        )

        return jsonify({
            'success': True,
            'analytics': {
                'total_workshops': total_workshops,
                'completed_workshops': completed_workshops,
                'scheduled_workshops': scheduled_workshops,
                'workshops_by_year': [{'year': y, 'count': c} for y, c in workshops_by_year],
                'workshops_by_council': [{'council': c, 'count': cnt} for c, cnt in workshops_by_council],
                'top_focus_areas': top_focus_areas,
                'sessions_by_type': [{'type': t, 'count': c} for t, c in sessions_by_type],
                'topics_by_status': [{'status': s, 'count': c} for s, c in topics_by_status],
                'topics_by_council': [{'council': c, 'count': cnt} for c, cnt in topics_by_council],
                'upcoming_workshops': [w.to_dict() for w in upcoming_workshops]
            }
        })

    except Exception as e:
        logger.error(f"Error getting CMOD analytics: {e}")
        return jsonify({'error': 'Failed to get CMOD analytics'}), 500


# ==================== ADMIN ENDPOINTS ====================

@bp.route('/topics', methods=['POST'])
@require_admin
def create_cmod_topic():
    """Create CMOD topic tracking record (admin only)"""
    try:
        data = request.get_json()

        topic = CMODTopicTracking(
            workshop_id=data.get('workshop_id'),
            topic=data['topic'],
            description=data.get('description'),
            council_name=data.get('council_name'),
            implementation_status=data.get('implementation_status', 'Not Started'),
            related_actions=data.get('related_actions', []),
            related_meetings=data.get('related_meetings', []),
            related_amendments=data.get('related_amendments', []),
            first_discussed=datetime.fromisoformat(data['first_discussed']) if data.get('first_discussed') else None,
            implementation_notes=data.get('implementation_notes'),
            outcomes_achieved=data.get('outcomes_achieved', []),
            challenges=data.get('challenges', [])
        )

        db.session.add(topic)
        db.session.commit()

        log_activity(
            activity_type='cmod.topic_created',
            description=f'Created CMOD topic tracking: {topic.topic}',
            category='cmod',
            resource_type='cmod_topic',
            resource_id=str(topic.id),
            resource_name=topic.topic
        )

        return jsonify({
            'success': True,
            'topic': topic.to_dict(),
            'message': 'CMOD topic tracking created successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error creating CMOD topic: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create CMOD topic tracking'}), 500


@bp.route('/topics/<topic_id>', methods=['PUT'])
@require_admin
def update_cmod_topic(topic_id):
    """Update CMOD topic tracking record (admin only)"""
    try:
        topic = CMODTopicTracking.query.filter_by(id=topic_id).first()

        if not topic:
            return jsonify({'error': 'CMOD topic not found'}), 404

        data = request.get_json()

        # Update fields
        if 'implementation_status' in data:
            topic.implementation_status = data['implementation_status']
        if 'related_actions' in data:
            topic.related_actions = data['related_actions']
        if 'related_meetings' in data:
            topic.related_meetings = data['related_meetings']
        if 'related_amendments' in data:
            topic.related_amendments = data['related_amendments']
        if 'last_updated_council' in data:
            topic.last_updated_council = datetime.fromisoformat(data['last_updated_council'])
        if 'implementation_notes' in data:
            topic.implementation_notes = data['implementation_notes']
        if 'outcomes_achieved' in data:
            topic.outcomes_achieved = data['outcomes_achieved']
        if 'challenges' in data:
            topic.challenges = data['challenges']

        db.session.commit()

        log_activity(
            activity_type='cmod.topic_updated',
            description=f'Updated CMOD topic tracking: {topic.topic}',
            category='cmod',
            resource_type='cmod_topic',
            resource_id=topic_id,
            resource_name=topic.topic
        )

        return jsonify({
            'success': True,
            'topic': topic.to_dict(),
            'message': 'CMOD topic tracking updated successfully'
        })

    except Exception as e:
        logger.error(f"Error updating CMOD topic: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update CMOD topic tracking'}), 500
