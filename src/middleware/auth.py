"""Authentication Middleware"""
import os
import jwt
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'You must be logged in to access this resource'
            }), 401

        token = auth_header.split(' ')[1]

        try:
            # Verify JWT
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            request.user = decoded  # Attach user info to request
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Your session has expired. Please log in again.'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid authentication token'
            }), 401
        except Exception as e:
            logger.error(f"Error in auth middleware: {e}")
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication failed'
            }), 401

    return decorated_function


def require_role(*roles):
    """Decorator to require specific role(s) for a route"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'You must be logged in to access this resource'
                }), 401

            token = auth_header.split(' ')[1]

            try:
                # Verify JWT
                decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                user_role = decoded.get('role')

                if not user_role or user_role not in roles:
                    logger.warning(f"Access denied for user {decoded.get('email')} with role {user_role}")
                    return jsonify({
                        'error': 'Forbidden',
                        'message': 'You do not have permission to access this resource'
                    }), 403

                request.user = decoded  # Attach user info to request
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Your session has expired. Please log in again.'
                }), 401
            except jwt.InvalidTokenError:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Invalid authentication token'
                }), 401
            except Exception as e:
                logger.error(f"Error in role middleware: {e}")
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Authentication failed'
                }), 401

        return decorated_function
    return decorator


def require_admin(f):
    """Decorator to require admin role"""
    return require_role('admin')(f)
