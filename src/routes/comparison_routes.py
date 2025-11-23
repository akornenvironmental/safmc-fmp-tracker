"""
Amendment Comparison API Routes
"""

import logging
from flask import Blueprint, jsonify, request
from src.services.comparison_service import ComparisonService
from src.utils.security import safe_error_response

logger = logging.getLogger(__name__)

bp = Blueprint('comparison', __name__, url_prefix='/api/compare')


@bp.route('', methods=['POST'])
@bp.route('/', methods=['POST'])
def compare_actions():
    """
    Compare multiple actions side-by-side

    Body params:
    - action_ids: List of action IDs to compare (2-5 actions)
    """
    try:
        data = request.get_json()
        action_ids = data.get('action_ids', [])

        if len(action_ids) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 action IDs required'
            }), 400

        if len(action_ids) > 5:
            return jsonify({
                'success': False,
                'error': 'Maximum 5 actions can be compared at once'
            }), 400

        result = ComparisonService.compare_actions(action_ids)

        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 404

        return jsonify({
            'success': True,
            'comparison': result
        })

    except Exception as e:
        logger.error(f"Error comparing actions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/similar/<action_id>', methods=['GET'])
def find_similar(action_id):
    """
    Find actions similar to a given action

    Query params:
    - limit: Max results (default 10)
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 50)

        similar = ComparisonService.find_similar_actions(action_id, limit)

        return jsonify({
            'success': True,
            'sourceActionId': action_id,
            'similar': similar,
            'count': len(similar)
        })

    except Exception as e:
        logger.error(f"Error finding similar actions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/fmp-history/<fmp>', methods=['GET'])
def get_fmp_history(fmp):
    """
    Get complete amendment history for an FMP
    """
    try:
        # URL decode FMP name
        fmp = fmp.replace('-', ' ').title()

        history = ComparisonService.get_fmp_amendment_history(fmp)

        return jsonify({
            'success': True,
            'history': history
        })

    except Exception as e:
        logger.error(f"Error getting FMP history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/species-history/<species_name>', methods=['GET'])
def get_species_history(species_name):
    """
    Get regulatory history for a species
    """
    try:
        # URL decode species name
        species_name = species_name.replace('-', ' ').title()

        history = ComparisonService.get_species_regulation_history(species_name)

        return jsonify({
            'success': True,
            'history': history
        })

    except Exception as e:
        logger.error(f"Error getting species history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/versions', methods=['GET'])
def get_action_versions():
    """
    Find all versions of a similar action

    Query params:
    - title: Base title to search for (e.g., "Snapper Grouper Amendment")
    """
    try:
        base_title = request.args.get('title', '')

        if not base_title:
            return jsonify({
                'success': False,
                'error': 'title parameter required'
            }), 400

        versions = ComparisonService.get_action_versions(base_title)

        return jsonify({
            'success': True,
            'baseTitle': base_title,
            'versions': versions,
            'count': len(versions)
        })

    except Exception as e:
        logger.error(f"Error getting action versions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
