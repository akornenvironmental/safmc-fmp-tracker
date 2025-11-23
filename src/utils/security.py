"""
Security Utilities
Common security functions for the application
"""

import logging
import re
from functools import wraps

logger = logging.getLogger(__name__)

# Sensitive field patterns to filter from logs
SENSITIVE_PATTERNS = [
    'password', 'passwd', 'pwd',
    'secret', 'token', 'jwt',
    'api_key', 'apikey', 'api-key',
    'auth', 'authorization',
    'credential', 'cred',
    'key', 'private',
    'ssn', 'social_security',
    'credit_card', 'card_number', 'cvv', 'cvc',
    'bank_account', 'routing_number',
    'email_password', 'smtp_password',
]

# Compile regex for sensitive field detection (case-insensitive)
SENSITIVE_REGEX = re.compile(
    '|'.join(f'({pattern})' for pattern in SENSITIVE_PATTERNS),
    re.IGNORECASE
)


def filter_sensitive_data(data: dict, depth: int = 0, max_depth: int = 5) -> dict:
    """
    Recursively filter sensitive data from dictionaries for logging.

    Args:
        data: Dictionary to filter
        depth: Current recursion depth
        max_depth: Maximum recursion depth

    Returns:
        Filtered dictionary with sensitive values masked
    """
    if not isinstance(data, dict) or depth > max_depth:
        return data

    filtered = {}
    for key, value in data.items():
        # Check if key matches sensitive patterns
        if SENSITIVE_REGEX.search(str(key)):
            filtered[key] = '[REDACTED]'
        elif isinstance(value, dict):
            filtered[key] = filter_sensitive_data(value, depth + 1, max_depth)
        elif isinstance(value, list):
            filtered[key] = [
                filter_sensitive_data(item, depth + 1, max_depth)
                if isinstance(item, dict) else item
                for item in value
            ]
        elif isinstance(value, str) and len(value) > 20:
            # Potentially sensitive long strings (like tokens)
            if any(pattern in key.lower() for pattern in ['token', 'key', 'secret', 'auth']):
                filtered[key] = '[REDACTED]'
            else:
                filtered[key] = value
        else:
            filtered[key] = value

    return filtered


def safe_error_response(error: Exception, log_details: bool = True) -> tuple:
    """
    Generate a safe error response without exposing internal details.

    Args:
        error: The exception that occurred
        log_details: Whether to log full error details server-side

    Returns:
        Tuple of (error_dict, status_code)
    """
    # Log full error details server-side
    if log_details:
        logger.error(f"Error occurred: {type(error).__name__}: {error}", exc_info=True)

    # Map known errors to user-friendly messages
    error_messages = {
        'IntegrityError': 'A database constraint was violated. Please check your input.',
        'OperationalError': 'A database operation failed. Please try again.',
        'ValidationError': 'The provided data is invalid. Please check your input.',
        'PermissionError': 'You do not have permission to perform this action.',
        'FileNotFoundError': 'The requested resource was not found.',
        'TimeoutError': 'The operation timed out. Please try again.',
        'ConnectionError': 'Unable to connect to a required service. Please try again.',
    }

    error_type = type(error).__name__

    # Return generic message for unknown errors
    user_message = error_messages.get(
        error_type,
        'An unexpected error occurred. Please try again or contact support.'
    )

    return {'error': user_message, 'error_code': error_type}, 500


def validate_pagination_params(limit: int, offset: int, max_limit: int = 1000, max_offset: int = 100000) -> tuple:
    """
    Validate and sanitize pagination parameters.

    Args:
        limit: Requested limit
        offset: Requested offset
        max_limit: Maximum allowed limit
        max_offset: Maximum allowed offset

    Returns:
        Tuple of (sanitized_limit, sanitized_offset)
    """
    # Ensure positive integers
    sanitized_limit = max(1, min(int(limit) if limit else 100, max_limit))
    sanitized_offset = max(0, min(int(offset) if offset else 0, max_offset))

    return sanitized_limit, sanitized_offset


def validate_string_length(value: str, max_length: int = 10000, field_name: str = 'input') -> str:
    """
    Validate string length to prevent DoS attacks.

    Args:
        value: String to validate
        max_length: Maximum allowed length
        field_name: Field name for error message

    Returns:
        Validated string

    Raises:
        ValueError: If string exceeds max_length
    """
    if value and len(value) > max_length:
        raise ValueError(f'{field_name} exceeds maximum length of {max_length} characters')
    return value


def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitize SQL identifiers (table names, column names).
    Only allows alphanumeric characters and underscores.

    Args:
        identifier: The identifier to sanitize

    Returns:
        Sanitized identifier

    Raises:
        ValueError: If identifier contains invalid characters
    """
    if not identifier:
        raise ValueError('Identifier cannot be empty')

    # Only allow alphanumeric and underscore
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(f'Invalid identifier: {identifier}')

    return identifier


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


def log_security_event(event_type: str, details: dict, user_id: str = None, ip_address: str = None):
    """
    Log security-relevant events for audit purposes.

    Args:
        event_type: Type of security event
        details: Event details (will be filtered for sensitive data)
        user_id: User ID if available
        ip_address: Client IP address
    """
    filtered_details = filter_sensitive_data(details)

    log_entry = {
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': ip_address,
        'details': filtered_details
    }

    logger.info(f"SECURITY_EVENT: {log_entry}")
