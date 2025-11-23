"""Authentication Routes"""
import os
import secrets
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from src.config.extensions import db
from src.models.user import User
from src.middleware.auth_middleware import log_activity
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Rate limiting
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address, default_limits=[])
    RATE_LIMITING_ENABLED = True
except ImportError:
    limiter = None
    RATE_LIMITING_ENABLED = False

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# JWT Configuration - enforce strong secret in production
JWT_SECRET = os.getenv('SECRET_KEY')
if not JWT_SECRET:
    if os.getenv('FLASK_ENV') == 'production' or os.getenv('RENDER'):
        raise ValueError("SECRET_KEY must be set in production!")
    JWT_SECRET = 'dev-secret-key-for-local-only'
    logger.warning("Using development JWT_SECRET - NOT FOR PRODUCTION")

JWT_EXPIRATION_HOURS = 8  # 8 hours for active sessions (a workday)
REFRESH_TOKEN_DAYS = 7  # Refresh tokens valid for 7 days

# Email Configuration
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
CLIENT_URL = os.getenv('CLIENT_URL', 'https://safmc-fmp-tracker.onrender.com')


def send_magic_link_email(user_email, user_name, magic_link):
    """Send magic link email"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Login to SAFMC FMP Tracker'
        msg['From'] = f'"SAFMC FMP Tracker" <{EMAIL_USER}>'
        msg['To'] = user_email

        # HTML content
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #08306b;">SAFMC FMP Tracker Login</h2>
            <p>Hello {user_name or 'there'},</p>
            <p>Click the button below to log in to the SAFMC FMP Tracker:</p>
            <div style="margin: 30px 0;">
                <a href="{magic_link}"
                   style="background-color: #08306b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                  Log In to FMP Tracker
                </a>
            </div>
            <p style="color: #666; font-size: 14px;">
                This link will expire in 15 minutes. If you didn't request this login, you can safely ignore this email.
            </p>
            <p style="color: #666; font-size: 14px;">
                If the button doesn't work, copy and paste this link into your browser:<br>
                <code style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{magic_link}</code>
            </p>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #9ca3af; font-size: 12px;">
                SAFMC FMP Tracker<br>
                Built by <a href="https://akornenvironmental.com" style="color: #08306b;">akorn environmental</a>
            </p>
        </div>
        """

        # Attach HTML
        msg.attach(MIMEText(html, 'html'))

        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)

        logger.info(f"Magic link email sent to {user_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


def rate_limit_decorator(limit_string):
    """Apply rate limit if flask-limiter is available"""
    def decorator(f):
        if RATE_LIMITING_ENABLED and limiter:
            return limiter.limit(limit_string)(f)
        return f
    return decorator


@bp.route('/request-login', methods=['POST'])
@rate_limit_decorator("5 per hour")  # Limit login requests to prevent brute force
def request_login():
    """Request a magic link for login"""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Validate email format
        email = email.lower().strip()
        if len(email) > 255 or '@' not in email or '.' not in email.split('@')[-1]:
            return jsonify({'error': 'Invalid email format'}), 400

        # Find user - use generic error to prevent user enumeration
        user = User.query.filter_by(email=email).first()

        if not user:
            # Generic error to prevent user enumeration
            logger.warning(f"Login attempt for non-existent user: {email}")
            return jsonify({
                'error': 'If this email is registered, a login link has been sent.'
            }), 200  # Return 200 to not reveal if email exists

        if not user.is_active:
            logger.warning(f"Login attempt for deactivated user: {email}")
            return jsonify({
                'error': 'If this email is registered, a login link has been sent.'
            }), 200  # Return 200 to not reveal account status

        # Generate secure token
        login_token = secrets.token_urlsafe(32)
        token_expiry = datetime.utcnow() + timedelta(minutes=15)

        # Save token to user
        user.login_token = login_token
        user.token_expiry = token_expiry
        db.session.commit()

        # Create magic link
        magic_link = f"{CLIENT_URL}/auth/verify?token={login_token}&email={email}"

        # Send email - fail if not configured
        if not EMAIL_USER or not EMAIL_PASSWORD:
            logger.error("Email not configured! Set EMAIL_USER and EMAIL_PASSWORD environment variables.")
            return jsonify({'error': 'Email service not configured. Please contact the administrator.'}), 500

        email_sent = send_magic_link_email(email, user.name, magic_link)

        if not email_sent:
            return jsonify({'error': 'Failed to send email. Please try again.'}), 500

        return jsonify({
            'success': True,
            'message': 'Check your email for the login link'
        })

    except Exception as e:
        logger.error(f"Error in request_login: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/verify', methods=['GET'])
def verify_login():
    """Verify magic link token and issue JWT"""
    try:
        token = request.args.get('token')
        email = request.args.get('email')

        if not token or not email:
            return jsonify({'error': 'Token and email are required'}), 400

        email = email.lower().strip()

        # Find user with valid token
        user = User.query.filter_by(email=email, login_token=token).first()

        if not user:
            # Log failed login attempt - invalid token or email
            log_activity(
                activity_type='user.login_failed',
                description=f'Failed login attempt for {email} - invalid link',
                category='auth'
            )
            return jsonify({'error': 'Invalid login link'}), 401

        # Check if token is expired
        if user.token_expiry < datetime.utcnow():
            # Log failed login attempt - expired token
            log_activity(
                activity_type='user.login_failed',
                description=f'Failed login attempt for {user.email} - link expired',
                category='auth',
                resource_type='user',
                resource_id=user.id,
                resource_name=user.email
            )
            return jsonify({'error': 'Login link has expired. Please request a new one.'}), 401

        # Update last login and clear token
        user.last_login = datetime.utcnow()
        user.login_token = None
        user.token_expiry = None
        db.session.commit()

        # Generate JWT token
        jwt_token = jwt.encode(
            {
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
            },
            JWT_SECRET,
            algorithm='HS256'
        )

        # Generate refresh token for persistent sessions
        refresh_token = secrets.token_urlsafe(48)
        user.refresh_token = refresh_token
        user.refresh_token_expiry = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_DAYS)
        db.session.commit()

        logger.info(f"User {user.email} logged in successfully")

        # Log successful login activity
        log_activity(
            activity_type='user.login',
            description=f'User logged in successfully',
            category='auth',
            resource_type='user',
            resource_id=user.id,
            resource_name=user.email
        )

        return jsonify({
            'success': True,
            'token': jwt_token,
            'refreshToken': refresh_token,
            'expiresIn': JWT_EXPIRATION_HOURS * 3600,  # seconds
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        })

    except Exception as e:
        logger.error(f"Error in verify_login: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh JWT using refresh token - allows persistent sessions"""
    try:
        data = request.get_json()
        refresh_tok = data.get('refreshToken')

        if not refresh_tok:
            return jsonify({'error': 'Refresh token required'}), 400

        # Find user with valid refresh token
        user = User.query.filter_by(refresh_token=refresh_tok).first()

        if not user:
            logger.warning("Invalid refresh token attempted")
            return jsonify({'error': 'Invalid refresh token'}), 401

        # Check if refresh token is expired
        if user.refresh_token_expiry < datetime.utcnow():
            # Clear expired refresh token
            user.refresh_token = None
            user.refresh_token_expiry = None
            db.session.commit()
            logger.warning(f"Expired refresh token for {user.email}")
            return jsonify({'error': 'Refresh token expired. Please log in again.'}), 401

        # Check if user is still active
        if not user.is_active:
            logger.warning(f"Refresh attempt for deactivated user: {user.email}")
            return jsonify({'error': 'Account is deactivated'}), 401

        # Generate new JWT token
        jwt_token = jwt.encode(
            {
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
            },
            JWT_SECRET,
            algorithm='HS256'
        )

        # Optionally rotate refresh token for extra security
        new_refresh_token = secrets.token_urlsafe(48)
        user.refresh_token = new_refresh_token
        user.refresh_token_expiry = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_DAYS)
        db.session.commit()

        logger.info(f"Token refreshed for {user.email}")

        return jsonify({
            'success': True,
            'token': jwt_token,
            'refreshToken': new_refresh_token,
            'expiresIn': JWT_EXPIRATION_HOURS * 3600,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        })

    except Exception as e:
        logger.error(f"Error in refresh_token: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint - invalidates refresh token server-side"""
    try:
        # Try to get refresh token from request to invalidate it
        data = request.get_json() or {}
        refresh_tok = data.get('refreshToken')

        if refresh_tok:
            # Find and invalidate the refresh token
            user = User.query.filter_by(refresh_token=refresh_tok).first()
            if user:
                user.refresh_token = None
                user.refresh_token_expiry = None
                db.session.commit()
                logger.info(f"Refresh token invalidated for {user.email}")

        # Log logout activity
        log_activity(
            activity_type='user.logout',
            description='User logged out',
            category='auth'
        )

        return jsonify({'success': True, 'message': 'Logged out successfully'})

    except Exception as e:
        logger.error(f"Error in logout: {e}")
        return jsonify({'success': True, 'message': 'Logged out successfully'})


@bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'authenticated': False}), 401

        token = auth_header.split(' ')[1]

        # Verify JWT
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])

            return jsonify({
                'authenticated': True,
                'user': {
                    'id': decoded.get('user_id'),
                    'email': decoded.get('email'),
                    'name': decoded.get('name'),
                    'role': decoded.get('role')
                }
            })
        except jwt.ExpiredSignatureError:
            return jsonify({'authenticated': False, 'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'authenticated': False, 'error': 'Invalid token'}), 401

    except Exception as e:
        logger.error(f"Error in check_auth: {e}")
        return jsonify({'authenticated': False}), 401
