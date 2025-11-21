"""
SEDAR Assessments API Routes
"""

import logging
from flask import Blueprint, jsonify, request
from sqlalchemy import or_, desc

from src.config.extensions import db
from src.models.safe_sedar import SEDARAssessment, AssessmentActionLink, SAFESEDARScrapeLog

logger = logging.getLogger(__name__)

bp = Blueprint('sedar', __name__, url_prefix='/api/sedar')


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
def get_sedar_assessments():
    """
    Get all SEDAR assessments with optional filters

    Query params:
    - status: Filter by assessment_status
    - species: Filter by species name (partial match)
    - council: Filter by council
    - fmp: Filter by FMP
    - year: Filter by completion year
    - search: Search across species, title, SEDAR number
    - limit: Max results (default 100)
    - offset: Pagination offset (default 0)
    """
    try:
        # Build query
        query = SEDARAssessment.query

        # Filters
        status = request.args.get('status')
        if status:
            query = query.filter(SEDARAssessment.assessment_status == status)

        species = request.args.get('species')
        if species:
            query = query.filter(SEDARAssessment.species_name.ilike(f'%{species}%'))

        council = request.args.get('council')
        if council:
            query = query.filter(SEDARAssessment.council == council)

        fmp = request.args.get('fmp')
        if fmp:
            query = query.filter(SEDARAssessment.fmp == fmp)

        year = request.args.get('year')
        if year:
            query = query.filter(db.extract('year', SEDARAssessment.completion_date) == int(year))

        search = request.args.get('search')
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                or_(
                    SEDARAssessment.sedar_number.ilike(search_term),
                    SEDARAssessment.species_name.ilike(search_term),
                    SEDARAssessment.full_title.ilike(search_term)
                )
            )

        # Pagination
        limit = min(int(request.args.get('limit', 100)), 500)
        offset = int(request.args.get('offset', 0))

        # Order by completion date desc, then SEDAR number desc
        query = query.order_by(
            desc(SEDARAssessment.completion_date),
            desc(SEDARAssessment.sedar_number)
        )

        # Get total count
        total = query.count()

        # Get page of results
        assessments = query.limit(limit).offset(offset).all()

        return jsonify({
            'success': True,
            'assessments': [a.to_dict() for a in assessments],
            'total': total,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"Error getting SEDAR assessments: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<sedar_number>', methods=['GET'])
def get_sedar_assessment(sedar_number):
    """Get specific SEDAR assessment by number"""
    try:
        # Normalize SEDAR number format
        if not sedar_number.upper().startswith('SEDAR'):
            sedar_number = f"SEDAR {sedar_number}"

        assessment = SEDARAssessment.query.filter_by(sedar_number=sedar_number).first()

        if not assessment:
            return jsonify({'success': False, 'error': 'Assessment not found'}), 404

        return jsonify({
            'success': True,
            'assessment': assessment.to_dict()
        })

    except Exception as e:
        logger.error(f"Error getting SEDAR assessment {sedar_number}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<sedar_number>/actions', methods=['GET'])
def get_sedar_linked_actions(sedar_number):
    """Get actions linked to a specific SEDAR assessment"""
    try:
        # Normalize SEDAR number
        if not sedar_number.upper().startswith('SEDAR'):
            sedar_number = f"SEDAR {sedar_number}"

        assessment = SEDARAssessment.query.filter_by(sedar_number=sedar_number).first()

        if not assessment:
            return jsonify({'success': False, 'error': 'Assessment not found'}), 404

        # Get linked actions
        links = AssessmentActionLink.query.filter_by(sedar_assessment_id=assessment.id).all()

        # Get action details
        from src.models.action import Action
        action_ids = [link.action_id for link in links]
        actions = Action.query.filter(Action.action_id.in_(action_ids)).all()

        # Combine link metadata with action data
        linked_actions = []
        for link in links:
            action = next((a for a in actions if a.action_id == link.action_id), None)
            if action:
                linked_actions.append({
                    'link': link.to_dict(),
                    'action': {
                        'action_id': action.action_id,
                        'title': action.title,
                        'fmp': action.fmp,
                        'status': action.status,
                        'phase': action.phase
                    }
                })

        return jsonify({
            'success': True,
            'sedarNumber': sedar_number,
            'linkedActions': linked_actions,
            'count': len(linked_actions)
        })

    except Exception as e:
        logger.error(f"Error getting linked actions for {sedar_number}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/species/<species_name>', methods=['GET'])
def get_species_assessments(species_name):
    """Get all SEDAR assessments for a specific species"""
    try:
        assessments = SEDARAssessment.query.filter(
            SEDARAssessment.species_name.ilike(f'%{species_name}%')
        ).order_by(desc(SEDARAssessment.completion_date)).all()

        return jsonify({
            'success': True,
            'species': species_name,
            'assessments': [a.to_dict() for a in assessments],
            'count': len(assessments)
        })

    except Exception as e:
        logger.error(f"Error getting assessments for species {species_name}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/councils', methods=['GET'])
def get_councils():
    """Get list of councils with assessment counts"""
    try:
        from sqlalchemy import func

        results = db.session.query(
            SEDARAssessment.council,
            func.count(SEDARAssessment.id).label('count')
        ).group_by(SEDARAssessment.council).all()

        councils = [
            {'council': council, 'count': count}
            for council, count in results
            if council  # Exclude None
        ]

        return jsonify({
            'success': True,
            'councils': councils
        })

    except Exception as e:
        logger.error(f"Error getting councils: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
def get_sedar_stats():
    """Get summary statistics for SEDAR assessments"""
    try:
        from sqlalchemy import func

        # Total assessments
        total = SEDARAssessment.query.count()

        # By status
        status_counts = db.session.query(
            SEDARAssessment.assessment_status,
            func.count(SEDARAssessment.id).label('count')
        ).group_by(SEDARAssessment.assessment_status).all()

        # By council
        council_counts = db.session.query(
            SEDARAssessment.council,
            func.count(SEDARAssessment.id).label('count')
        ).group_by(SEDARAssessment.council).all()

        # Recent assessments (completed in last 3 years)
        from datetime import datetime, timedelta
        three_years_ago = datetime.now().date() - timedelta(days=3*365)
        recent_count = SEDARAssessment.query.filter(
            SEDARAssessment.completion_date >= three_years_ago
        ).count()

        # Overfished/overfishing counts
        overfished_count = SEDARAssessment.query.filter(
            SEDARAssessment.stock_status == 'Overfished'
        ).count()

        overfishing_count = SEDARAssessment.query.filter(
            SEDARAssessment.overfishing_status.ilike('%occurring%')
        ).count()

        # Rebuilding required
        rebuilding_count = SEDARAssessment.query.filter(
            SEDARAssessment.rebuilding_required == True
        ).count()

        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'byStatus': {status: count for status, count in status_counts},
                'byCouncil': {council: count for council, count in council_counts if council},
                'recentAssessments': recent_count,
                'overfished': overfished_count,
                'overfishing': overfishing_count,
                'rebuildingRequired': rebuilding_count
            }
        })

    except Exception as e:
        logger.error(f"Error getting SEDAR stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/scrape', methods=['POST'])
def trigger_sedar_scrape():
    """
    Trigger SEDAR assessments scraping

    Body params:
    - safmc_only: Boolean (default False)
    - run_linking: Boolean - whether to run automatic linking after scrape (default True)
    """
    try:
        data = request.get_json() or {}

        safmc_only = data.get('safmc_only', False)
        run_linking = data.get('run_linking', True)

        logger.info(f"Starting SEDAR scrape (SAFMC only: {safmc_only})...")

        # Lazy import to avoid loading heavy dependencies at module level
        from src.services.sedar_import_service import SEDARImportService

        # Run import
        service = SEDARImportService()
        result = service.import_all_assessments(safmc_only=safmc_only)

        # Run automatic linking if requested
        if result.get('success') and run_linking:
            logger.info("Running automatic assessment-to-action linking...")
            linking_result = service.link_assessments_to_actions()
            result['linking'] = linking_result

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error triggering SEDAR scrape: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/link-to-action', methods=['POST'])
def link_sedar_to_action():
    """
    Manually link SEDAR assessment to an action

    Body params:
    - sedar_number: SEDAR number
    - action_id: Action ID
    - link_type: Type of link (default: 'basis_for_action')
    - notes: Optional notes
    - specific_recommendation: Optional specific recommendation text
    """
    try:
        data = request.get_json()

        sedar_number = data.get('sedar_number')
        action_id = data.get('action_id')
        link_type = data.get('link_type', 'basis_for_action')
        notes = data.get('notes')
        specific_recommendation = data.get('specific_recommendation')

        if not sedar_number or not action_id:
            return jsonify({
                'success': False,
                'error': 'sedar_number and action_id required'
            }), 400

        # Normalize SEDAR number
        if not sedar_number.upper().startswith('SEDAR'):
            sedar_number = f"SEDAR {sedar_number}"

        # Get assessment
        assessment = SEDARAssessment.query.filter_by(sedar_number=sedar_number).first()
        if not assessment:
            return jsonify({
                'success': False,
                'error': 'Assessment not found'
            }), 404

        # Check if link already exists
        existing = AssessmentActionLink.query.filter_by(
            sedar_assessment_id=assessment.id,
            action_id=action_id,
            link_type=link_type
        ).first()

        if existing:
            return jsonify({
                'success': False,
                'error': 'Link already exists'
            }), 409

        # Create link
        link = AssessmentActionLink(
            sedar_assessment_id=assessment.id,
            action_id=action_id,
            link_type=link_type,
            confidence='high',  # Manual links are high confidence
            notes=notes,
            specific_recommendation=specific_recommendation,
            created_by='manual',
            verified=True  # Manual links are pre-verified
        )

        db.session.add(link)
        db.session.commit()

        return jsonify({
            'success': True,
            'link': link.to_dict()
        })

    except Exception as e:
        logger.error(f"Error linking SEDAR to action: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/scrape-logs', methods=['GET'])
def get_scrape_logs():
    """Get SEDAR scraping history"""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)

        logs = SAFESEDARScrapeLog.query.filter(
            SAFESEDARScrapeLog.scrape_type == 'sedar_assessments'
        ).order_by(desc(SAFESEDARScrapeLog.started_at)).limit(limit).all()

        return jsonify({
            'success': True,
            'logs': [log.to_dict() for log in logs]
        })

    except Exception as e:
        logger.error(f"Error getting scrape logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/verify-link/<int:link_id>', methods=['POST'])
def verify_assessment_link(link_id):
    """Mark an automatically-created link as verified"""
    try:
        link = AssessmentActionLink.query.get(link_id)

        if not link:
            return jsonify({'success': False, 'error': 'Link not found'}), 404

        link.verified = True
        db.session.commit()

        return jsonify({
            'success': True,
            'link': link.to_dict()
        })

    except Exception as e:
        logger.error(f"Error verifying link: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/unverified-links', methods=['GET'])
def get_unverified_links():
    """Get list of automatically-created links that need manual verification"""
    try:
        links = AssessmentActionLink.query.filter_by(verified=False).all()

        # Get assessment and action details
        enriched_links = []
        for link in links:
            assessment = SEDARAssessment.query.get(link.sedar_assessment_id)

            from src.models.action import Action
            action = Action.query.filter_by(action_id=link.action_id).first()

            if assessment and action:
                enriched_links.append({
                    'link': link.to_dict(),
                    'assessment': {
                        'sedar_number': assessment.sedar_number,
                        'species_name': assessment.species_name,
                        'full_title': assessment.full_title
                    },
                    'action': {
                        'action_id': action.action_id,
                        'title': action.title,
                        'fmp': action.fmp
                    }
                })

        return jsonify({
            'success': True,
            'unverifiedLinks': enriched_links,
            'count': len(enriched_links)
        })

    except Exception as e:
        logger.error(f"Error getting unverified links: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
