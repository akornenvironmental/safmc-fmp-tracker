"""
Authentication and Authorization Middleware
Provides decorators for protecting routes and logging user activity
"""
import jwt
import os
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime
from sqlalchemy import text
import logging

from src.config.extensions import db
from src.models.user import User

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


def get_current_user():
    """Extract user from JWT token in Authorization header"""
    try:
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning(f"Missing or invalid Authorization header for {request.path}")
            return None

        token = auth_header.split(' ')[1]

        # Verify JWT
        decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])

        # Get user from database to ensure they're still active
        user = User.query.filter_by(id=decoded.get('user_id')).first()

        if not user:
            logger.warning(f"User not found for ID: {decoded.get('user_id')}")
            return None

        if not user.is_active:
            logger.warning(f"Inactive user attempted access: {user.email}")
            return None

        return user

    except jwt.ExpiredSignatureError:
        logger.warning(f"Expired JWT token for {request.path}")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token for {request.path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error extracting user from token for {request.path}: {e}")
        return None


def require_auth(f):
    """
    Decorator to require authentication for a route
    Adds the current user to Flask's g object
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()

        if not user:
            return jsonify({
                'error': 'Authentication required',
                'authenticated': False
            }), 401

        # Store user in Flask's request context
        g.current_user = user

        return f(*args, **kwargs)

    return decorated_function


def require_role(*allowed_roles):
    """
    Decorator to require specific roles for a route
    Usage:
        @require_role('admin')
        @require_role('super_admin', 'admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({
                    'error': 'Authentication required',
                    'authenticated': False
                }), 401

            # Check if user has required role
            if user.role not in allowed_roles:
                logger.warning(
                    f"User {user.email} (role: {user.role}) attempted to access "
                    f"{request.endpoint} which requires roles: {allowed_roles}"
                )
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_role': list(allowed_roles),
                    'your_role': user.role
                }), 403

            # Store user in Flask's request context
            g.current_user = user

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def require_admin(f):
    """
    Decorator to require admin or super_admin role
    Convenience wrapper for require_role('super_admin', 'admin')
    """
    return require_role('super_admin', 'admin')(f)


def require_super_admin(f):
    """
    Decorator to require super_admin role only
    Use for sensitive operations like user management
    """
    return require_role('super_admin')(f)


def log_activity(
    activity_type,
    description=None,
    resource_type=None,
    resource_id=None,
    resource_name=None,
    category=None,
    changes_made=None,
    old_values=None,
    new_values=None
):
    """
    Log user activity to the database
    Can be used as a function or decorator

    Usage as function:
        log_activity('action.created', description='Created new action', resource_id=action.id)

    Usage as decorator:
        @log_activity('action.viewed', category='data_access')
        def get_action(action_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function first
            start_time = datetime.utcnow()
            response = None
            error = None
            status_code = 200

            try:
                response = f(*args, **kwargs)

                # Extract status code from response if it's a tuple
                if isinstance(response, tuple):
                    status_code = response[1] if len(response) > 1 else 200

                return response

            except Exception as e:
                error = str(e)
                status_code = 500
                raise

            finally:
                # Log the activity after function execution
                end_time = datetime.utcnow()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)

                try:
                    _log_activity_to_db(
                        activity_type=activity_type,
                        description=description,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        resource_name=resource_name,
                        category=category,
                        status_code=status_code,
                        success=(error is None and 200 <= status_code < 400),
                        error_message=error,
                        request_duration_ms=duration_ms,
                        changes_made=changes_made,
                        old_values=old_values,
                        new_values=new_values
                    )
                except Exception as log_error:
                    # Don't let logging errors break the request
                    logger.error(f"Failed to log activity: {log_error}")

        return decorated_function

    # If used as a function instead of decorator, log immediately
    if callable(activity_type):
        # It's being used as @log_activity without arguments
        return decorator(activity_type)

    return decorator


def _log_activity_to_db(
    activity_type,
    description=None,
    resource_type=None,
    resource_id=None,
    resource_name=None,
    category=None,
    status_code=200,
    success=True,
    error_message=None,
    request_duration_ms=None,
    changes_made=None,
    old_values=None,
    new_values=None
):
    """Internal function to actually write activity log to database"""
    try:
        # Get current user
        user = get_current_user()

        # Extract request details
        http_method = request.method
        endpoint = request.endpoint or request.path
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')

        # Get request params with comprehensive sensitive data filtering
        request_params = {}
        try:
            from src.utils.security import filter_sensitive_data
            if request.method == 'GET':
                request_params = filter_sensitive_data(dict(request.args))
            elif request.method in ['POST', 'PUT', 'PATCH']:
                if request.is_json:
                    request_params = filter_sensitive_data(request.get_json() or {})
        except Exception:
            request_params = {'_error': 'Could not parse request params'}

        # Insert activity log
        db.session.execute(text("""
            INSERT INTO user_activity_logs (
                user_id, user_email, user_role,
                activity_type, activity_category, description,
                resource_type, resource_id, resource_name,
                http_method, endpoint, request_params,
                status_code, success, error_message,
                ip_address, user_agent, request_duration_ms,
                changes_made, old_values, new_values,
                created_at
            ) VALUES (
                :user_id, :user_email, :user_role,
                :activity_type, :activity_category, :description,
                :resource_type, :resource_id, :resource_name,
                :http_method, :endpoint, :request_params,
                :status_code, :success, :error_message,
                :ip_address, :user_agent, :request_duration_ms,
                :changes_made, :old_values, :new_values,
                CURRENT_TIMESTAMP
            )
        """), {
            'user_id': user.id if user else None,
            'user_email': user.email if user else 'anonymous',
            'user_role': user.role if user else None,
            'activity_type': activity_type,
            'activity_category': category,
            'description': description,
            'resource_type': resource_type,
            'resource_id': str(resource_id) if resource_id else None,
            'resource_name': resource_name,
            'http_method': http_method,
            'endpoint': endpoint,
            'request_params': request_params or None,
            'status_code': status_code,
            'success': success,
            'error_message': error_message,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'request_duration_ms': request_duration_ms,
            'changes_made': changes_made,
            'old_values': old_values,
            'new_values': new_values
        })

        db.session.commit()

    except Exception as e:
        logger.error(f"Failed to log activity to database: {e}")
        db.session.rollback()
