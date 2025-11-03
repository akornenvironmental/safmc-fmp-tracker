"""
Web Routes for SAFMC FMP Tracker
Serves HTML pages for the web interface
"""

from flask import Blueprint, render_template

bp = Blueprint('web', __name__)

@bp.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

@bp.route('/actions')
def actions_page():
    """Serve the actions page"""
    return render_template('actions.html')

@bp.route('/meetings')
def meetings_page():
    """Serve the meetings page"""
    return render_template('meetings.html')

@bp.route('/comments')
def comments_page():
    """Serve the comments page"""
    return render_template('comments.html')
