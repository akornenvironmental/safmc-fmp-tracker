"""
Admin Routes - User Management and Activity Logging
Requires super_admin or admin permissions
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import text, desc
from datetime import datetime, timedelta
import logging
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.config.extensions import db
from src.models.user import User
from src.middleware.auth_middleware import (
    require_super_admin,
    require_admin,
    get_current_user,
    log_activity
)

# Email configuration
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
CLIENT_URL = os.getenv('CLIENT_URL', 'https://safmc-fmp-tracker.onrender.com')

# Rate limiting for admin endpoints
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    admin_limiter = Limiter(key_func=get_remote_address, default_limits=[])
    RATE_LIMITING_ENABLED = True
except ImportError:
    admin_limiter = None
    RATE_LIMITING_ENABLED = False


def admin_rate_limit(limit_string):
    """Apply rate limit if flask-limiter is available"""
    def decorator(f):
        if RATE_LIMITING_ENABLED and admin_limiter:
            return admin_limiter.limit(limit_string)(f)
        return f
    return decorator

logger = logging.getLogger(__name__)

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def send_user_invite_email(user_email, user_name, role, organization, magic_link, invited_by):
    """Send welcome/invite email to new user with magic link"""
    try:
        if not EMAIL_USER or not EMAIL_PASSWORD:
            logger.warning("Email not configured - skipping invite email")
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Welcome to SAFMC FMP Tracker - Your Account is Ready'
        msg['From'] = f'"SAFMC FMP Tracker" <{EMAIL_USER}>'
        msg['To'] = user_email

        role_display = {
            'super_admin': 'Super Admin',
            'admin': 'Admin',
            'editor': 'Editor'
        }.get(role, role)

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #08306b;">Welcome to SAFMC FMP Tracker!</h2>
            <p>Hello {user_name or 'there'},</p>
            <p><strong>{invited_by}</strong> has created an account for you on the SAFMC FMP Tracker system.</p>

            <div style="background: #f3f4f6; padding: 16px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0 0 8px 0;"><strong>Your Account Details:</strong></p>
                <p style="margin: 4px 0; font-size: 14px;">Email: {user_email}</p>
                <p style="margin: 4px 0; font-size: 14px;">Role: {role_display}</p>
                {f'<p style="margin: 4px 0; font-size: 14px;">Organization: {organization}</p>' if organization else ''}
            </div>

            <p>Click the button below to log in and get started:</p>
            <div style="margin: 30px 0;">
                <a href="{magic_link}"
                   style="background-color: #08306b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                  Log In to FMP Tracker
                </a>
            </div>

            <p style="color: #666; font-size: 14px;">
                This login link will expire in 24 hours. After that, you can request a new login link from the login page.
            </p>

            <div style="background: #e8f4f8; padding: 16px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px;"><strong>What is SAFMC FMP Tracker?</strong></p>
                <p style="margin: 8px 0 0 0; font-size: 14px; color: #666;">
                    A system for tracking South Atlantic Fishery Management Plan amendments, meetings, public comments, and stock assessments.
                    All data is sourced from publicly available information on SAFMC.net, SEDAR, and NOAA.
                </p>
            </div>

            <p style="color: #666; font-size: 14px;">
                If the button doesn't work, copy and paste this link into your browser:<br>
                <code style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px; font-size: 12px; word-break: break-all;">{magic_link}</code>
            </p>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #9ca3af; font-size: 12px;">
                SAFMC FMP Tracker<br>
                Built by <a href="https://akornenvironmental.com" style="color: #08306b;">akorn environmental</a>
            </p>
        </div>
        """

        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)

        logger.info(f"Invite email sent to {user_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending invite email: {e}")
        return False


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
@admin_rate_limit("10 per hour")  # Strict limit on user creation
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
        organization = data.get('organization', '').strip()
        role = data.get('role', 'editor')

        # Validate role
        if role not in ['super_admin', 'admin', 'editor']:
            return jsonify({'error': 'Invalid role'}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409

        # Get current admin user for invite email
        current_user = get_current_user()

        # Generate magic link token for invite (24 hour expiry)
        login_token = secrets.token_urlsafe(32)
        token_expiry = datetime.utcnow() + timedelta(hours=24)

        # Create new user with login token already set
        user = User(
            email=email,
            name=name,
            organization=organization or None,
            role=role,
            is_active=True,
            login_token=login_token,
            token_expiry=token_expiry
        )

        db.session.add(user)
        db.session.commit()

        # Send invite email with magic link
        magic_link = f"{CLIENT_URL}/auth/verify?token={login_token}&email={email}"
        invite_sent = send_user_invite_email(
            user_email=email,
            user_name=name,
            role=role,
            organization=organization,
            magic_link=magic_link,
            invited_by=current_user.name or current_user.email
        )

        # Log activity
        log_activity(
            activity_type='user.created',
            description=f'Created user {email} with role {role}',
            category='admin',
            resource_type='user',
            resource_id=user.id,
            resource_name=email,
            changes_made={'created': True, 'invite_sent': invite_sent},
            new_values={'email': email, 'name': name, 'role': role}
        )

        logger.info(f"User {email} created by {current_user.email}, invite sent: {invite_sent}")

        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': 'User created successfully' + (' and invite email sent' if invite_sent else ' (invite email failed to send)'),
            'invite_sent': invite_sent
        }), 201

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create user'}), 500


@bp.route('/users/<user_id>/resend-invite', methods=['POST'])
@admin_rate_limit("10 per hour")
@require_super_admin
def resend_invite(user_id):
    """Resend invite email to existing user (super_admin only)"""
    try:
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Generate new magic link token (24 hour expiry)
        login_token = secrets.token_urlsafe(32)
        token_expiry = datetime.utcnow() + timedelta(hours=24)

        user.login_token = login_token
        user.token_expiry = token_expiry
        db.session.commit()

        # Get current admin for invite
        current_user = get_current_user()

        # Send invite email
        magic_link = f"{CLIENT_URL}/auth/verify?token={login_token}&email={user.email}"
        invite_sent = send_user_invite_email(
            user_email=user.email,
            user_name=user.name,
            role=user.role,
            organization=user.organization,
            magic_link=magic_link,
            invited_by=current_user.name or current_user.email
        )

        if not invite_sent:
            return jsonify({'error': 'Failed to send invite email'}), 500

        # Log activity
        log_activity(
            activity_type='user.invite_resent',
            description=f'Resent invite to {user.email}',
            category='admin',
            resource_type='user',
            resource_id=user_id,
            resource_name=user.email
        )

        logger.info(f"Invite resent to {user.email} by {current_user.email}")

        return jsonify({
            'success': True,
            'message': f'Invite email sent to {user.email}'
        })

    except Exception as e:
        logger.error(f"Error resending invite: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to resend invite'}), 500


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
            'organization': user.organization,
            'role': user.role,
            'is_active': user.is_active
        }

        changes = {}

        # Update fields
        if 'name' in data:
            user.name = data['name'].strip()
            changes['name'] = data['name']

        if 'organization' in data:
            user.organization = data['organization'].strip() or None
            changes['organization'] = data['organization']

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
@admin_rate_limit("5 per hour")  # Very strict limit on user deletion
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


# ==================== DUPLICATE CONTACT MANAGEMENT ====================

@bp.route('/contacts/duplicates', methods=['GET'])
@require_admin
def get_duplicate_contacts():
    """Find potential duplicate contacts"""
    try:
        from src.services.duplicate_detection_service import find_potential_duplicates

        min_score = request.args.get('min_score', 0.8, type=float)
        duplicates = find_potential_duplicates(min_score=min_score)

        return jsonify({
            'success': True,
            'duplicate_groups': duplicates,
            'total_groups': len(duplicates)
        })

    except Exception as e:
        logger.error(f"Error finding duplicate contacts: {e}")
        return jsonify({'error': 'Failed to find duplicates'}), 500


@bp.route('/contacts/duplicate-stats', methods=['GET'])
@require_admin
def get_duplicate_stats():
    """Get statistics about potential duplicate contacts"""
    try:
        from src.services.duplicate_detection_service import get_duplicate_stats

        stats = get_duplicate_stats()

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Error getting duplicate stats: {e}")
        return jsonify({'error': 'Failed to get duplicate stats'}), 500


@bp.route('/contacts/merge', methods=['POST'])
@admin_rate_limit("20 per hour")  # Limit contact merging
@require_super_admin
def merge_duplicate_contacts():
    """Merge duplicate contacts into a primary contact (super_admin only)"""
    try:
        from src.services.duplicate_detection_service import merge_contacts

        data = request.get_json()
        primary_id = data.get('primary_id')
        duplicate_ids = data.get('duplicate_ids', [])

        if not primary_id:
            return jsonify({'error': 'primary_id is required'}), 400

        if not duplicate_ids:
            return jsonify({'error': 'duplicate_ids is required'}), 400

        result = merge_contacts(primary_id, duplicate_ids)

        if result['success']:
            log_activity(
                activity_type='admin.contacts_merged',
                description=f'Merged {result["merged_count"]} contacts into primary contact',
                category='admin'
            )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error merging contacts: {e}")
        return jsonify({'error': 'Failed to merge contacts'}), 500


# ==================== DATABASE MIGRATIONS ====================

@bp.route('/run-migration', methods=['POST'])
@admin_rate_limit("5 per hour")  # Strict limit on migrations
@require_super_admin
def run_migration():
    """Run a database migration (super_admin only)"""
    try:
        data = request.get_json()
        migration_name = data.get('migration')

        if not migration_name:
            return jsonify({'error': 'migration name is required'}), 400

        # Whitelist of allowed migrations
        allowed_migrations = [
            'add_invitation_tracking_to_users',
            'add_organization_to_users',
            'add_refresh_token_to_users'
        ]

        if migration_name not in allowed_migrations:
            return jsonify({'error': f'Migration {migration_name} not allowed'}), 400

        # Import and run the migration
        import sys
        import importlib.util

        migration_path = f'migrations/{migration_name}.py'
        spec = importlib.util.spec_from_file_location(migration_name, migration_path)

        if not spec or not spec.loader:
            return jsonify({'error': f'Migration file not found: {migration_path}'}), 404

        migration_module = importlib.util.module_from_spec(spec)
        sys.modules[migration_name] = migration_module
        spec.loader.exec_module(migration_module)

        # Run the migration
        success = migration_module.run_migration()

        if success:
            current_user = get_current_user()
            log_activity(
                activity_type='admin.migration_executed',
                description=f'Executed migration: {migration_name}',
                category='admin',
                changes_made={'migration': migration_name}
            )

            logger.info(f"Migration {migration_name} executed by {current_user.email}")

            return jsonify({
                'success': True,
                'message': f'Migration {migration_name} completed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Migration failed - check logs for details'
            }), 500

    except Exception as e:
        logger.error(f"Error running migration: {e}")
        return jsonify({'error': f'Failed to run migration: {str(e)}'}), 500
