"""
SSC (Scientific and Statistical Committee) Routes
API endpoints for SSC members, meetings, recommendations, and analytics
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import text, func, desc, and_, or_
from datetime import datetime, timedelta
import logging

from src.config.extensions import db
from src.models.ssc import SSCMember, SSCMeeting, SSCRecommendation, SSCCouncilConnection, SSCDocument
from src.middleware.auth_middleware import require_auth, require_admin, log_activity

logger = logging.getLogger(__name__)

bp = Blueprint('ssc', __name__, url_prefix='/api/ssc')


# ==================== SSC MEMBERS ====================

@bp.route('/members', methods=['GET'])
@require_auth
def get_ssc_members():
    """Get all SSC members with filtering"""
    try:
        # Get query parameters
        state = request.args.get('state', '').strip()
        seat_type = request.args.get('seat_type', '').strip()
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        search = request.args.get('search', '').strip()

        # Build query
        query = SSCMember.query

        if active_only:
            query = query.filter(SSCMember.is_active == True)

        if state:
            query = query.filter(SSCMember.state == state)

        if seat_type:
            query = query.filter(SSCMember.seat_type == seat_type)

        if search:
            query = query.filter(
                or_(
                    SSCMember.name.ilike(f'%{search}%'),
                    SSCMember.expertise_area.ilike(f'%{search}%'),
                    SSCMember.affiliation.ilike(f'%{search}%')
                )
            )

        # Order by chair, vice-chair, then name
        query = query.order_by(
            SSCMember.is_chair.desc(),
            SSCMember.is_vice_chair.desc(),
            SSCMember.name
        )

        members = query.all()

        # Log activity
        log_activity(
            activity_type='ssc.members_viewed',
            description='Viewed SSC members',
            category='ssc'
        )

        return jsonify({
            'success': True,
            'members': [member.to_dict() for member in members],
            'count': len(members)
        })

    except Exception as e:
        logger.error(f"Error getting SSC members: {e}")
        return jsonify({'error': 'Failed to get SSC members'}), 500


@bp.route('/members/<member_id>', methods=['GET'])
@require_auth
def get_ssc_member(member_id):
    """Get single SSC member details"""
    try:
        member = SSCMember.query.filter_by(id=member_id).first()

        if not member:
            return jsonify({'error': 'SSC member not found'}), 404

        log_activity(
            activity_type='ssc.member_viewed',
            description=f'Viewed SSC member: {member.name}',
            category='ssc',
            resource_type='ssc_member',
            resource_id=member_id,
            resource_name=member.name
        )

        return jsonify({
            'success': True,
            'member': member.to_dict()
        })

    except Exception as e:
        logger.error(f"Error getting SSC member: {e}")
        return jsonify({'error': 'Failed to get SSC member'}), 500


# ==================== SSC MEETINGS ====================

@bp.route('/meetings', methods=['GET'])
@require_auth
def get_ssc_meetings():
    """Get SSC meetings with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', '').strip()
        upcoming = request.args.get('upcoming', '').lower() == 'true'
        year = request.args.get('year', type=int)

        # Build query
        query = SSCMeeting.query

        if status:
            query = query.filter(SSCMeeting.status == status)

        if upcoming:
            query = query.filter(SSCMeeting.meeting_date_start >= datetime.now())

        if year:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31, 23, 59, 59)
            query = query.filter(
                SSCMeeting.meeting_date_start >= start_date,
                SSCMeeting.meeting_date_start <= end_date
            )

        # Order by date descending (most recent first)
        query = query.order_by(SSCMeeting.meeting_date_start.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        log_activity(
            activity_type='ssc.meetings_viewed',
            description=f'Viewed SSC meetings (page {page})',
            category='ssc'
        )

        return jsonify({
            'success': True,
            'meetings': [meeting.to_dict() for meeting in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })

    except Exception as e:
        logger.error(f"Error getting SSC meetings: {e}")
        return jsonify({'error': 'Failed to get SSC meetings'}), 500


@bp.route('/meetings/<meeting_id>', methods=['GET'])
@require_auth
def get_ssc_meeting(meeting_id):
    """Get single SSC meeting with recommendations"""
    try:
        meeting = SSCMeeting.query.filter_by(id=meeting_id).first()

        if not meeting:
            return jsonify({'error': 'SSC meeting not found'}), 404

        log_activity(
            activity_type='ssc.meeting_viewed',
            description=f'Viewed SSC meeting: {meeting.title}',
            category='ssc',
            resource_type='ssc_meeting',
            resource_id=meeting_id,
            resource_name=meeting.title
        )

        return jsonify({
            'success': True,
            'meeting': meeting.to_dict(include_recommendations=True)
        })

    except Exception as e:
        logger.error(f"Error getting SSC meeting: {e}")
        return jsonify({'error': 'Failed to get SSC meeting'}), 500


# ==================== SSC RECOMMENDATIONS ====================

@bp.route('/recommendations', methods=['GET'])
@require_auth
def get_ssc_recommendations():
    """Get SSC recommendations with filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', '').strip()
        species = request.args.get('species', '').strip()
        fmp = request.args.get('fmp', '').strip()
        recommendation_type = request.args.get('type', '').strip()
        search = request.args.get('search', '').strip()

        # Build query
        query = SSCRecommendation.query

        if status:
            query = query.filter(SSCRecommendation.status == status)

        if species:
            query = query.filter(SSCRecommendation.species.contains([species]))

        if fmp:
            query = query.filter(SSCRecommendation.fmp.ilike(f'%{fmp}%'))

        if recommendation_type:
            query = query.filter(SSCRecommendation.recommendation_type == recommendation_type)

        if search:
            query = query.filter(
                or_(
                    SSCRecommendation.title.ilike(f'%{search}%'),
                    SSCRecommendation.recommendation_text.ilike(f'%{search}%')
                )
            )

        # Order by created date descending
        query = query.order_by(SSCRecommendation.created_at.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        log_activity(
            activity_type='ssc.recommendations_viewed',
            description=f'Viewed SSC recommendations (page {page})',
            category='ssc'
        )

        return jsonify({
            'success': True,
            'recommendations': [rec.to_dict() for rec in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })

    except Exception as e:
        logger.error(f"Error getting SSC recommendations: {e}")
        return jsonify({'error': 'Failed to get SSC recommendations'}), 500


@bp.route('/recommendations/<recommendation_id>', methods=['GET'])
@require_auth
def get_ssc_recommendation(recommendation_id):
    """Get single SSC recommendation with Council connections"""
    try:
        recommendation = SSCRecommendation.query.filter_by(id=recommendation_id).first()

        if not recommendation:
            return jsonify({'error': 'SSC recommendation not found'}), 404

        log_activity(
            activity_type='ssc.recommendation_viewed',
            description=f'Viewed SSC recommendation: {recommendation.title}',
            category='ssc',
            resource_type='ssc_recommendation',
            resource_id=recommendation_id,
            resource_name=recommendation.title
        )

        return jsonify({
            'success': True,
            'recommendation': recommendation.to_dict(include_connections=True)
        })

    except Exception as e:
        logger.error(f"Error getting SSC recommendation: {e}")
        return jsonify({'error': 'Failed to get SSC recommendation'}), 500


# ==================== SSC ANALYTICS ====================

@bp.route('/analytics', methods=['GET'])
@require_auth
def get_ssc_analytics():
    """Get SSC analytics and insights"""
    try:
        # Time range
        days = request.args.get('days', 365, type=int)
        start_date = datetime.now() - timedelta(days=days)

        # Total members
        total_members = SSCMember.query.filter_by(is_active=True).count()

        # Members by seat type
        members_by_seat = db.session.query(
            SSCMember.seat_type,
            func.count(SSCMember.id).label('count')
        ).filter(SSCMember.is_active == True).group_by(SSCMember.seat_type).all()

        # Members by state
        members_by_state = db.session.query(
            SSCMember.state,
            func.count(SSCMember.id).label('count')
        ).filter(SSCMember.is_active == True).group_by(SSCMember.state).order_by(desc('count')).all()

        # Upcoming meetings
        upcoming_meetings = SSCMeeting.query.filter(
            SSCMeeting.meeting_date_start >= datetime.now()
        ).order_by(SSCMeeting.meeting_date_start).limit(5).all()

        # Recent meetings
        recent_meetings = SSCMeeting.query.filter(
            SSCMeeting.meeting_date_start < datetime.now(),
            SSCMeeting.meeting_date_start >= start_date
        ).order_by(SSCMeeting.meeting_date_start.desc()).limit(10).all()

        # Recommendations by status
        recs_by_status = db.session.query(
            SSCRecommendation.status,
            func.count(SSCRecommendation.id).label('count')
        ).group_by(SSCRecommendation.status).all()

        # Recommendations by type
        recs_by_type = db.session.query(
            SSCRecommendation.recommendation_type,
            func.count(SSCRecommendation.id).label('count')
        ).group_by(SSCRecommendation.recommendation_type).order_by(desc('count')).limit(10).all()

        # Top species discussed
        top_species_query = text("""
            SELECT UNNEST(species) as species, COUNT(*) as count
            FROM ssc_recommendations
            WHERE species IS NOT NULL
            GROUP BY UNNEST(species)
            ORDER BY count DESC
            LIMIT 10
        """)
        top_species_result = db.session.execute(top_species_query)
        top_species = [{'species': row[0], 'count': row[1]} for row in top_species_result]

        log_activity(
            activity_type='ssc.analytics_viewed',
            description='Viewed SSC analytics',
            category='ssc'
        )

        return jsonify({
            'success': True,
            'analytics': {
                'total_members': total_members,
                'members_by_seat_type': [{'seat_type': s, 'count': c} for s, c in members_by_seat],
                'members_by_state': [{'state': s, 'count': c} for s, c in members_by_state],
                'upcoming_meetings': [m.to_dict() for m in upcoming_meetings],
                'recent_meetings': [m.to_dict() for m in recent_meetings],
                'recommendations_by_status': [{'status': s, 'count': c} for s, c in recs_by_status],
                'recommendations_by_type': [{'type': t, 'count': c} for t, c in recs_by_type],
                'top_species': top_species
            }
        })

    except Exception as e:
        logger.error(f"Error getting SSC analytics: {e}")
        return jsonify({'error': 'Failed to get SSC analytics'}), 500


# ==================== ADMIN ENDPOINTS ====================

@bp.route('/meetings', methods=['POST'])
@require_admin
def create_ssc_meeting():
    """Create new SSC meeting (admin only)"""
    try:
        data = request.get_json()

        meeting = SSCMeeting(
            title=data['title'],
            meeting_date_start=datetime.fromisoformat(data['meeting_date_start']),
            meeting_date_end=datetime.fromisoformat(data['meeting_date_end']) if data.get('meeting_date_end') else None,
            location=data.get('location'),
            is_virtual=data.get('is_virtual', False),
            meeting_type=data.get('meeting_type'),
            status=data.get('status', 'scheduled'),
            agenda_url=data.get('agenda_url'),
            briefing_book_url=data.get('briefing_book_url'),
            report_url=data.get('report_url'),
            webinar_link=data.get('webinar_link'),
            description=data.get('description'),
            topics=data.get('topics', []),
            species_discussed=data.get('species_discussed', [])
        )

        db.session.add(meeting)
        db.session.commit()

        log_activity(
            activity_type='ssc.meeting_created',
            description=f'Created SSC meeting: {meeting.title}',
            category='ssc',
            resource_type='ssc_meeting',
            resource_id=str(meeting.id),
            resource_name=meeting.title
        )

        return jsonify({
            'success': True,
            'meeting': meeting.to_dict(),
            'message': 'SSC meeting created successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error creating SSC meeting: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create SSC meeting'}), 500


@bp.route('/recommendations', methods=['POST'])
@require_admin
def create_ssc_recommendation():
    """Create new SSC recommendation (admin only)"""
    try:
        data = request.get_json()

        recommendation = SSCRecommendation(
            meeting_id=data.get('meeting_id'),
            recommendation_number=data.get('recommendation_number'),
            title=data['title'],
            recommendation_text=data['recommendation_text'],
            recommendation_type=data.get('recommendation_type'),
            species=data.get('species', []),
            fmp=data.get('fmp'),
            topic=data.get('topic'),
            abc_value=data.get('abc_value'),
            abc_units=data.get('abc_units'),
            overfishing_limit=data.get('overfishing_limit'),
            status=data.get('status', 'pending'),
            notes=data.get('notes')
        )

        db.session.add(recommendation)
        db.session.commit()

        log_activity(
            activity_type='ssc.recommendation_created',
            description=f'Created SSC recommendation: {recommendation.title}',
            category='ssc',
            resource_type='ssc_recommendation',
            resource_id=str(recommendation.id),
            resource_name=recommendation.title
        )

        return jsonify({
            'success': True,
            'recommendation': recommendation.to_dict(),
            'message': 'SSC recommendation created successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error creating SSC recommendation: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create SSC recommendation'}), 500
