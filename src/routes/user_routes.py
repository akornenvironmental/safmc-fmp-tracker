"""
User Routes for SAFMC FMP Tracker
Provides API endpoints for user profile and favorites management
"""

from flask import Blueprint, jsonify, request, g
from sqlalchemy import desc, or_
from datetime import datetime
import logging

from src.config.extensions import db
from src.models.user import User
from src.models.user_favorite import UserFavorite
from src.models.action import Action
from src.models.meeting import Meeting
from src.models.stock_assessment import StockAssessment
from src.models.document import Document
from src.middleware.auth_middleware import require_auth
from src.utils.security import validate_string_length, safe_error_response

bp = Blueprint('user', __name__)
logger = logging.getLogger(__name__)

# ==================== USER PROFILE ENDPOINTS ====================

@bp.route('/api/users/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user's profile information"""
    try:
        user = g.current_user
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        return safe_error_response("Failed to fetch user profile", 500)


@bp.route('/api/users/preferences', methods=['PATCH'])
@require_auth
def update_user_preferences():
    """Update user notification preferences"""
    try:
        user = g.current_user
        data = request.get_json()

        # Update notification preferences
        if 'email_notifications' in data:
            user.email_notifications = bool(data['email_notifications'])
        if 'notify_new_comments' in data:
            user.notify_new_comments = bool(data['notify_new_comments'])
        if 'notify_weekly_digest' in data:
            user.notify_weekly_digest = bool(data['notify_weekly_digest'])

        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Preferences updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user preferences: {e}")
        return safe_error_response("Failed to update preferences", 500)


# ==================== FAVORITES ENDPOINTS ====================

@bp.route('/api/user/favorites', methods=['GET'])
@require_auth
def get_user_favorites():
    """Get all favorites for the current user"""
    try:
        user = g.current_user

        # Get query parameters
        item_type = request.args.get('type')  # Filter by type
        flagged_as = request.args.get('flag')  # Filter by flag category
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, max(1, int(request.args.get('per_page', 20))))

        # Build query
        query = UserFavorite.query.filter_by(user_id=user.id)

        if item_type:
            query = query.filter_by(item_type=item_type)
        if flagged_as:
            query = query.filter_by(flagged_as=flagged_as)

        # Order by most recently added
        query = query.order_by(desc(UserFavorite.created_at))

        # Paginate
        total = query.count()
        favorites = query.offset((page - 1) * per_page).limit(per_page).all()

        # Enrich favorites with item details
        enriched_favorites = []
        for fav in favorites:
            fav_dict = fav.to_dict()
            fav_dict['item'] = get_item_details(fav.item_type, fav.item_id)
            enriched_favorites.append(fav_dict)

        return jsonify({
            'success': True,
            'favorites': enriched_favorites,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
    except Exception as e:
        logger.error(f"Error fetching user favorites: {e}")
        return safe_error_response("Failed to fetch favorites", 500)


@bp.route('/api/user/favorites', methods=['POST'])
@require_auth
def create_favorite():
    """Add an item to user's favorites"""
    try:
        user = g.current_user
        data = request.get_json()

        # Validate required fields
        if not data or 'item_type' not in data or 'item_id' not in data:
            return jsonify({
                'success': False,
                'error': 'item_type and item_id are required'
            }), 400

        item_type = validate_string_length(data['item_type'], 'item_type', max_length=50)
        item_id = validate_string_length(data['item_id'], 'item_id', max_length=100)

        # Optional fields
        notes = data.get('notes')
        if notes:
            notes = validate_string_length(notes, 'notes', max_length=5000)

        flagged_as = data.get('flagged_as')
        if flagged_as:
            flagged_as = validate_string_length(flagged_as, 'flagged_as', max_length=50)

        # Check if already favorited
        existing = UserFavorite.query.filter_by(
            user_id=user.id,
            item_type=item_type,
            item_id=item_id
        ).first()

        if existing:
            return jsonify({
                'success': False,
                'error': 'Item already in favorites'
            }), 409

        # Create new favorite
        favorite = UserFavorite(
            user_id=user.id,
            item_type=item_type,
            item_id=item_id,
            notes=notes,
            flagged_as=flagged_as
        )

        db.session.add(favorite)
        db.session.commit()

        # Return enriched favorite
        fav_dict = favorite.to_dict()
        fav_dict['item'] = get_item_details(favorite.item_type, favorite.item_id)

        return jsonify({
            'success': True,
            'message': 'Added to favorites',
            'favorite': fav_dict
        }), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating favorite: {e}")
        return safe_error_response("Failed to add favorite", 500)


@bp.route('/api/user/favorites/<int:favorite_id>', methods=['PATCH'])
@require_auth
def update_favorite(favorite_id):
    """Update notes or flag for a favorite"""
    try:
        user = g.current_user
        data = request.get_json()

        # Find favorite
        favorite = UserFavorite.query.filter_by(
            id=favorite_id,
            user_id=user.id
        ).first()

        if not favorite:
            return jsonify({
                'success': False,
                'error': 'Favorite not found'
            }), 404

        # Update fields
        if 'notes' in data:
            favorite.notes = validate_string_length(data['notes'], 'notes', max_length=5000) if data['notes'] else None

        if 'flagged_as' in data:
            favorite.flagged_as = validate_string_length(data['flagged_as'], 'flagged_as', max_length=50) if data['flagged_as'] else None

        favorite.updated_at = datetime.utcnow()
        db.session.commit()

        # Return enriched favorite
        fav_dict = favorite.to_dict()
        fav_dict['item'] = get_item_details(favorite.item_type, favorite.item_id)

        return jsonify({
            'success': True,
            'message': 'Favorite updated',
            'favorite': fav_dict
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating favorite: {e}")
        return safe_error_response("Failed to update favorite", 500)


@bp.route('/api/user/favorites/<int:favorite_id>', methods=['DELETE'])
@require_auth
def delete_favorite(favorite_id):
    """Remove an item from favorites"""
    try:
        user = g.current_user

        # Find favorite
        favorite = UserFavorite.query.filter_by(
            id=favorite_id,
            user_id=user.id
        ).first()

        if not favorite:
            return jsonify({
                'success': False,
                'error': 'Favorite not found'
            }), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Removed from favorites'
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting favorite: {e}")
        return safe_error_response("Failed to remove favorite", 500)


@bp.route('/api/user/favorites/check', methods=['POST'])
@require_auth
def check_favorite_status():
    """Check if item(s) are favorited by the current user"""
    try:
        user = g.current_user
        data = request.get_json()

        if not data or 'items' not in data:
            return jsonify({
                'success': False,
                'error': 'items array is required'
            }), 400

        # Build a dict of favorited items
        favorited = {}
        for item in data['items']:
            item_type = item.get('item_type')
            item_id = item.get('item_id')

            if not item_type or not item_id:
                continue

            favorite = UserFavorite.query.filter_by(
                user_id=user.id,
                item_type=item_type,
                item_id=item_id
            ).first()

            key = f"{item_type}:{item_id}"
            favorited[key] = {
                'is_favorited': favorite is not None,
                'favorite_id': favorite.id if favorite else None,
                'flagged_as': favorite.flagged_as if favorite else None
            }

        return jsonify({
            'success': True,
            'favorited': favorited
        }), 200
    except Exception as e:
        logger.error(f"Error checking favorite status: {e}")
        return safe_error_response("Failed to check favorite status", 500)


# ==================== HELPER FUNCTIONS ====================

def get_item_details(item_type, item_id):
    """Fetch details about the favorited item"""
    try:
        if item_type == 'action':
            action = Action.query.filter_by(action_id=item_id).first()
            if action:
                return {
                    'id': action.action_id,
                    'title': action.title,
                    'type': action.type,
                    'fmp': action.fmp,
                    'status': action.status,
                    'progress_stage': action.progress_stage
                }

        elif item_type == 'meeting':
            meeting = Meeting.query.filter_by(meeting_id=item_id).first()
            if meeting:
                return {
                    'id': meeting.meeting_id,
                    'title': meeting.title,
                    'type': meeting.type,
                    'start_date': meeting.start_date.isoformat() if meeting.start_date else None,
                    'location': meeting.location
                }

        elif item_type == 'assessment':
            assessment = StockAssessment.query.filter_by(sedar_number=item_id).first()
            if assessment:
                return {
                    'id': assessment.sedar_number,
                    'species_common_name': assessment.species_common_name,
                    'assessment_type': assessment.assessment_type,
                    'status': assessment.status,
                    'stock_status': assessment.stock_status
                }

        elif item_type == 'document':
            document = Document.query.filter_by(id=int(item_id)).first()
            if document:
                return {
                    'id': document.id,
                    'title': document.title,
                    'type': document.type,
                    'summary': document.summary
                }

        # Add more item types as needed

        return None
    except Exception as e:
        logger.error(f"Error fetching item details for {item_type}:{item_id}: {e}")
        return None
