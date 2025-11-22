"""
Admin Routes - User Management and Activity Logging
Requires super_admin or admin permissions
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import text, desc
from datetime import datetime, timedelta
import logging

from src.config.extensions import db
from src.models.user import User
from src.middleware.auth_middleware import (
    require_super_admin,
    require_admin,
    get_current_user,
    log_activity
)

logger = logging.getLogger(__name__)

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ==================== USER MANAGEMENT (SUPER ADMIN ONLY) ====================

@bp.route('/users', methods=['GET'])
@require_admin
def list_users():
    """List all users (admin+)"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '').strip()
        role_filter = request.args.get('role', '').strip()
        active_only = request.args.get('active_only', 'false').lower() == 'true'

        # Build query
        query = User.query

        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    User.email.ilike(f'%{search}%'),
                    User.name.ilike(f'%{search}%')
                )
            )

        if role_filter:
            query = query.filter(User.role == role_filter)

        if active_only:
            query = query.filter(User.is_active == True)

        # Get total count
        total = query.count()

        # Apply pagination
        users = query.order_by(User.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Log activity
        log_activity(
            activity_type='admin.users_viewed',
            description=f'Viewed user list (page {page})',
            category='admin',
            resource_type='users'
        )

        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': users.pages
            }
        })

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        return jsonify({'error': 'Failed to list users'}), 500


@bp.route('/users/<user_id>', methods=['GET'])
@require_admin
def get_user(user_id):
    """Get user details (admin+)"""
    try:
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Log activity
        log_activity(
            activity_type='user.viewed',
            description=f'Viewed user details for {user.email}',
            category='admin',
            resource_type='user',
            resource_id=user_id,
            resource_name=user.email
        )

        return jsonify({
            'success': True,
            'user': user.to_dict()
        })

    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return jsonify({'error': 'Failed to get user'}), 500


@bp.route('/users', methods=['POST'])
@require_super_admin
def create_user():
    """Create new user (super_admin only)"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400

        email = data['email'].lower().strip()
        name = data.get('name', '').strip()
        role = data.get('role', 'editor')

        # Validate role
        if role not in ['super_admin', 'admin', 'editor']:
            return jsonify({'error': 'Invalid role'}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409

        # Create new user
        user = User(
            email=email,
            name=name,
            role=role,
            is_active=True
        )

        db.session.add(user)
        db.session.commit()

        # Log activity
        current_user = get_current_user()
        log_activity(
            activity_type='user.created',
            description=f'Created user {email} with role {role}',
            category='admin',
            resource_type='user',
            resource_id=user.id,
            resource_name=email,
            changes_made={'created': True},
            new_values={'email': email, 'name': name, 'role': role}
        )

        logger.info(f"User {email} created by {current_user.email}")

        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': 'User created successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create user'}), 500


@bp.route('/users/<user_id>', methods=['PUT', 'PATCH'])
@require_super_admin
def update_user(user_id):
    """Update user (super_admin only)"""
    try:
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Track old values for audit
        old_values = {
            'name': user.name,
            'role': user.role,
            'is_active': user.is_active
        }

        changes = {}

        # Update fields
        if 'name' in data:
            user.name = data['name'].strip()
            changes['name'] = data['name']

        if 'role' in data:
            if data['role'] not in ['super_admin', 'admin', 'editor']:
                return jsonify({'error': 'Invalid role'}), 400
            user.role = data['role']
            changes['role'] = data['role']

        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
            changes['is_active'] = data['is_active']

        user.updated_at = datetime.utcnow()

        db.session.commit()

        # Log activity
        current_user = get_current_user()
        log_activity(
            activity_type='user.updated',
            description=f'Updated user {user.email}',
            category='admin',
            resource_type='user',
            resource_id=user_id,
            resource_name=user.email,
            changes_made=changes,
            old_values=old_values,
            new_values=changes
        )

        logger.info(f"User {user.email} updated by {current_user.email}")

        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': 'User updated successfully'
        })

    except Exception as e:
        logger.error(f"Error updating user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update user'}), 500


@bp.route('/users/<user_id>', methods=['DELETE'])
@require_super_admin
def delete_user(user_id):
    """Delete user (super_admin only)"""
    try:
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Don't allow deleting yourself
        current_user = get_current_user()
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete your own account'}), 400

        user_email = user.email
        user_role = user.role

        # Delete user
        db.session.delete(user)
        db.session.commit()

        # Log activity
        log_activity(
            activity_type='user.deleted',
            description=f'Deleted user {user_email}',
            category='admin',
            resource_type='user',
            resource_id=user_id,
            resource_name=user_email,
            changes_made={'deleted': True},
            old_values={'email': user_email, 'role': user_role}
        )

        logger.info(f"User {user_email} deleted by {current_user.email}")

        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user'}), 500


# ==================== ACTIVITY LOG VIEWING (ADMIN+) ====================

@bp.route('/activity-logs', methods=['GET'])
@require_admin
def get_activity_logs():
    """Get activity logs with filtering (admin+)"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        user_id = request.args.get('user_id', '').strip()
        activity_type = request.args.get('activity_type', '').strip()
        category = request.args.get('category', '').strip()
        success_only = request.args.get('success_only', '').lower()
        days = request.args.get('days', 7, type=int)  # Default last 7 days
        search = request.args.get('search', '').strip()

        # Build query
        query_parts = []
        params = {}

        # Time filter
        start_date = datetime.utcnow() - timedelta(days=days)
        query_parts.append("created_at >= :start_date")
        params['start_date'] = start_date

        # User filter
        if user_id:
            query_parts.append("user_id = :user_id")
            params['user_id'] = user_id

        # Activity type filter
        if activity_type:
            query_parts.append("activity_type = :activity_type")
            params['activity_type'] = activity_type

        # Category filter
        if category:
            query_parts.append("activity_category = :category")
            params['category'] = category

        # Success filter
        if success_only == 'true':
            query_parts.append("success = TRUE")
        elif success_only == 'false':
            query_parts.append("success = FALSE")

        # Search filter
        if search:
            query_parts.append(
                "(user_email ILIKE :search OR description ILIKE :search OR resource_name ILIKE :search)"
            )
            params['search'] = f'%{search}%'

        # Build WHERE clause
        where_clause = " AND ".join(query_parts) if query_parts else "1=1"

        # Get total count
        count_query = f"""
            SELECT COUNT(*) FROM user_activity_logs
            WHERE {where_clause}
        """
        result = db.session.execute(text(count_query), params)
        total = result.scalar()

        # Get paginated results
        offset = (page - 1) * per_page
        logs_query = f"""
            SELECT
                id, user_id, user_email, user_role,
                activity_type, activity_category, description,
                resource_type, resource_id, resource_name,
                http_method, endpoint, status_code, success,
                error_message, ip_address, request_duration_ms,
                created_at
            FROM user_activity_logs
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """
        params['limit'] = per_page
        params['offset'] = offset

        result = db.session.execute(text(logs_query), params)
        logs = [dict(row._mapping) for row in result]

        # Format timestamps
        for log in logs:
            if log['created_at']:
                log['created_at'] = log['created_at'].isoformat()

        # Calculate pages
        pages = (total + per_page - 1) // per_page

        # Log this activity too
        log_activity(
            activity_type='admin.logs_viewed',
            description=f'Viewed activity logs (page {page})',
            category='admin'
        )

        return jsonify({
            'success': True,
            'logs': logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages
            }
        })

    except Exception as e:
        logger.error(f"Error getting activity logs: {e}")
        return jsonify({'error': 'Failed to get activity logs'}), 500


@bp.route('/activity-logs/stats', methods=['GET'])
@require_admin
def get_activity_stats():
    """Get activity statistics (admin+)"""
    try:
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get stats
        stats_query = """
            SELECT
                COUNT(*) as total_activities,
                COUNT(DISTINCT user_id) as active_users,
                COUNT(CASE WHEN success = TRUE THEN 1 END) as successful_activities,
                COUNT(CASE WHEN success = FALSE THEN 1 END) as failed_activities,
                AVG(request_duration_ms) as avg_response_time
            FROM user_activity_logs
            WHERE created_at >= :start_date
        """
        result = db.session.execute(text(stats_query), {'start_date': start_date})
        stats = dict(result.fetchone()._mapping)

        # Get top activity types
        top_activities_query = """
            SELECT activity_type, COUNT(*) as count
            FROM user_activity_logs
            WHERE created_at >= :start_date
            GROUP BY activity_type
            ORDER BY count DESC
            LIMIT 10
        """
        result = db.session.execute(text(top_activities_query), {'start_date': start_date})
        top_activities = [dict(row._mapping) for row in result]

        # Get activity by category
        category_query = """
            SELECT activity_category, COUNT(*) as count
            FROM user_activity_logs
            WHERE created_at >= :start_date AND activity_category IS NOT NULL
            GROUP BY activity_category
            ORDER BY count DESC
        """
        result = db.session.execute(text(category_query), {'start_date': start_date})
        by_category = [dict(row._mapping) for row in result]

        # Get most active users
        active_users_query = """
            SELECT user_email, user_role, COUNT(*) as activity_count
            FROM user_activity_logs
            WHERE created_at >= :start_date AND user_email IS NOT NULL
            GROUP BY user_email, user_role
            ORDER BY activity_count DESC
            LIMIT 10
        """
        result = db.session.execute(text(active_users_query), {'start_date': start_date})
        active_users = [dict(row._mapping) for row in result]

        return jsonify({
            'success': True,
            'period_days': days,
            'stats': stats,
            'top_activities': top_activities,
            'by_category': by_category,
            'active_users': active_users
        })

    except Exception as e:
        logger.error(f"Error getting activity stats: {e}")
        return jsonify({'error': 'Failed to get activity stats'}), 500


@bp.route('/activity-logs/export', methods=['GET'])
@require_admin
def export_activity_logs():
    """Export activity logs to CSV (admin+)"""
    try:
        # Get filters (same as get_activity_logs)
        days = request.args.get('days', 7, type=int)
        user_id = request.args.get('user_id', '').strip()
        activity_type = request.args.get('activity_type', '').strip()

        # Build query
        query_parts = []
        params = {}

        start_date = datetime.utcnow() - timedelta(days=days)
        query_parts.append("created_at >= :start_date")
        params['start_date'] = start_date

        if user_id:
            query_parts.append("user_id = :user_id")
            params['user_id'] = user_id

        if activity_type:
            query_parts.append("activity_type = :activity_type")
            params['activity_type'] = activity_type

        where_clause = " AND ".join(query_parts) if query_parts else "1=1"

        # Get all matching logs (limited to 10000 for performance)
        logs_query = f"""
            SELECT *
            FROM user_activity_logs
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT 10000
        """
        result = db.session.execute(text(logs_query), params)
        logs = [dict(row._mapping) for row in result]

        # Log the export
        log_activity(
            activity_type='admin.logs_exported',
            description=f'Exported {len(logs)} activity logs',
            category='admin'
        )

        return jsonify({
            'success': True,
            'logs': logs,
            'count': len(logs)
        })

    except Exception as e:
        logger.error(f"Error exporting activity logs: {e}")
        return jsonify({'error': 'Failed to export activity logs'}), 500


# ==================== NOTIFICATION SETTINGS ====================

@bp.route('/notification-settings', methods=['GET'])
@require_admin
def get_notification_settings():
    """Get current user's notification settings"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Not authenticated'}), 401

        return jsonify({
            'success': True,
            'settings': {
                'email_notifications': current_user.email_notifications,
                'notify_new_comments': current_user.notify_new_comments,
                'notify_weekly_digest': current_user.notify_weekly_digest
            }
        })

    except Exception as e:
        logger.error(f"Error getting notification settings: {e}")
        return jsonify({'error': 'Failed to get notification settings'}), 500


@bp.route('/notification-settings', methods=['PUT'])
@require_admin
def update_notification_settings():
    """Update current user's notification settings"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Not authenticated'}), 401

        data = request.get_json()

        # Update settings if provided
        if 'email_notifications' in data:
            current_user.email_notifications = bool(data['email_notifications'])
        if 'notify_new_comments' in data:
            current_user.notify_new_comments = bool(data['notify_new_comments'])
        if 'notify_weekly_digest' in data:
            current_user.notify_weekly_digest = bool(data['notify_weekly_digest'])

        db.session.commit()

        log_activity(
            activity_type='admin.notification_settings_updated',
            description='Updated notification settings',
            category='admin'
        )

        return jsonify({
            'success': True,
            'message': 'Notification settings updated',
            'settings': {
                'email_notifications': current_user.email_notifications,
                'notify_new_comments': current_user.notify_new_comments,
                'notify_weekly_digest': current_user.notify_weekly_digest
            }
        })

    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update notification settings'}), 500


@bp.route('/send-test-notification', methods=['POST'])
@require_admin
def send_test_notification():
    """Send a test notification email to the current user"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Not authenticated'}), 401

        from src.services.notification_service import send_new_comments_notification

        # Create a sample comment for the test
        test_comments = [{
            'name': 'Test User',
            'organization': 'Test Organization',
            'actionFmp': 'Snapper-Grouper',
            'commentText': 'This is a test comment to verify that email notifications are working correctly.'
        }]

        success = send_new_comments_notification(
            current_user.email,
            test_comments,
            current_user.name or 'Admin'
        )

        if success:
            log_activity(
                activity_type='admin.test_notification_sent',
                description=f'Sent test notification to {current_user.email}',
                category='admin'
            )
            return jsonify({
                'success': True,
                'message': f'Test notification sent to {current_user.email}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send test notification. Check email configuration.'
            }), 500

    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        return jsonify({'error': 'Failed to send test notification'}), 500
