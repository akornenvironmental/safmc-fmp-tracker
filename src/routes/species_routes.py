"""
Species API Routes
Provides endpoints for species profiles and data
"""

import logging
from flask import Blueprint, jsonify, request
from src.services.species_service import SpeciesService

logger = logging.getLogger(__name__)

bp = Blueprint('species', __name__, url_prefix='/api/species')


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
def get_species_list():
    """
    Get list of all species with basic stats

    Query params:
    - search: Filter species by name (optional)
    - limit: Limit number of results (optional)
    """
    try:
        search = request.args.get('search', '').strip()
        limit = request.args.get('limit', type=int)

        if search:
            species_list = SpeciesService.search_species(search)
        else:
            species_list = SpeciesService.get_all_species()

        # Apply limit if specified
        if limit and limit > 0:
            species_list = species_list[:limit]

        return jsonify({
            'success': True,
            'species': species_list,
            'total': len(species_list)
        })

    except Exception as e:
        logger.error(f"Error getting species list: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/<species_name>', methods=['GET'])
def get_species_profile(species_name):
    """
    Get detailed profile for a specific species

    Returns:
    - Species metadata
    - All related actions
    - Timeline of management
    - Summary statistics
    """
    try:
        # URL decode and clean species name
        species_name = species_name.replace('-', ' ').replace('_', ' ').title()

        profile = SpeciesService.get_species_profile(species_name)

        if not profile:
            return jsonify({
                'success': False,
                'error': f'Species not found: {species_name}'
            }), 404

        return jsonify({
            'success': True,
            'species': profile
        })

    except Exception as e:
        logger.error(f"Error getting species profile for {species_name}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/<species_name>/timeline', methods=['GET'])
def get_species_timeline(species_name):
    """
    Get timeline of all management actions for a species

    Returns chronologically ordered list of actions
    """
    try:
        species_name = species_name.replace('-', ' ').replace('_', ' ').title()

        profile = SpeciesService.get_species_profile(species_name)

        if not profile:
            return jsonify({
                'success': False,
                'error': f'Species not found: {species_name}'
            }), 404

        return jsonify({
            'success': True,
            'species': species_name,
            'timeline': profile['timeline']
        })

    except Exception as e:
        logger.error(f"Error getting timeline for {species_name}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/stats', methods=['GET'])
def get_species_stats():
    """
    Get summary statistics about species data

    Returns:
    - Total species count
    - Most managed species
    - Species by FMP
    """
    try:
        all_species = SpeciesService.get_all_species()

        # Calculate stats
        total_species = len(all_species)
        total_actions = sum(sp['actionCount'] for sp in all_species)

        # Top 10 species by action count
        top_species = all_species[:10]

        # Species by FMP
        fmp_breakdown = {}
        for sp in all_species:
            for fmp in sp.get('fmps', []):
                if fmp not in fmp_breakdown:
                    fmp_breakdown[fmp] = []
                fmp_breakdown[fmp].append(sp['name'])

        return jsonify({
            'success': True,
            'stats': {
                'totalSpecies': total_species,
                'totalActions': total_actions,
                'averageActionsPerSpecies': round(total_actions / total_species, 2) if total_species > 0 else 0,
                'topSpecies': top_species,
                'speciesByFmp': {fmp: len(species) for fmp, species in fmp_breakdown.items()}
            }
        })

    except Exception as e:
        logger.error(f"Error getting species stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
