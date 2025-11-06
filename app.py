"""
SAFMC FMP Tracker - Main Application
Comprehensive tracking system for South Atlantic Fishery Management Plan amendments
"""

import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import logging
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
# Get the directory where app.py is located
app_dir = os.path.dirname(os.path.abspath(__file__))

# Client folder is in the same directory as app.py (both in src/ on Render)
static_path = os.path.join(app_dir, 'client', 'dist')
logger.info(f"App directory: {app_dir}")
logger.info(f"Static path: {static_path}")
logger.info(f"Static path exists: {os.path.exists(static_path)}")

app = Flask(__name__,
            static_folder=static_path,
            static_url_path='/static-internal')

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://localhost/safmc_fmp_tracker'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize extensions
from src.config.extensions import db, migrate
db.init_app(app)
migrate.init_app(app, db)
CORS(app)

# Import models after db initialization
from src.models.action import Action
from src.models.meeting import Meeting
from src.models.comment import Comment
from src.models.milestone import Milestone
from src.models.scrape_log import ScrapeLog
from src.models.user import User

# Health check endpoint (before blueprints)
@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

# Debug endpoint to list all routes
@app.route('/debug/routes')
def debug_routes():
    """List all registered routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify({'routes': sorted(routes, key=lambda x: x['path'])})

# Debug endpoint to check static folder
@app.route('/debug/static')
def debug_static():
    """Debug endpoint to check static folder setup"""
    import glob
    static_folder = static_path

    # Check various possible locations
    possible_locations = [
        os.path.join(app_dir, 'client', 'dist'),
        os.path.join(app_dir, 'client'),
        os.path.join(os.getcwd(), 'client', 'dist'),
        os.path.join(os.getcwd(), 'client'),
    ]

    location_checks = {}
    for loc in possible_locations:
        location_checks[loc] = {
            'exists': os.path.exists(loc),
            'files': os.listdir(loc) if os.path.exists(loc) else None
        }

    return jsonify({
        'static_folder': static_folder,
        'static_folder_exists': os.path.exists(static_folder) if static_folder else False,
        'static_folder_absolute': os.path.abspath(static_folder) if static_folder else None,
        'index_html_exists': os.path.exists(os.path.join(static_folder, 'index.html')) if static_folder else False,
        'files_in_static': os.listdir(static_folder) if static_folder and os.path.exists(static_folder) else [],
        'cwd': os.getcwd(),
        'app_dir': app_dir,
        'possible_client_locations': location_checks,
        'app_dir_files': os.listdir(app_dir) if os.path.exists(app_dir) else []
    })

# Import and register API routes
from src.routes import api_routes, auth_routes
from src.routes.stock_assessment_routes import stock_assessment_bp
app.register_blueprint(api_routes.bp, url_prefix='/api')
app.register_blueprint(auth_routes.bp)
app.register_blueprint(stock_assessment_bp)

# Initialize scheduler for automated scraping
from src.services.scheduler import init_scheduler
scheduler = init_scheduler(app)

# Serve React app (MUST be last - catch-all route)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React app for all non-API routes"""
    logger.info(f"Serve function called with path: '{path}'")

    # Check if this is an API route (should not reach here due to blueprint)
    if path.startswith('api/'):
        logger.info(f"Rejecting API path: {path}")
        return jsonify({'error': 'Not found'}), 404

    # If path is a file in dist (e.g., assets, js, css), serve it directly
    if path != "" and os.path.exists(os.path.join(static_path, path)):
        return send_from_directory(static_path, path)

    # Otherwise serve index.html for client-side routing
    try:
        return send_from_directory(static_path, 'index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        logger.error(f"Static folder: {static_path}")
        logger.error(f"Static folder exists: {os.path.exists(static_path)}")
        return jsonify({'error': 'Frontend not found', 'details': str(e)}), 500

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    logger.info(f"Starting SAFMC FMP Tracker on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
