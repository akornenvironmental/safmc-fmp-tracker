"""
SAFMC FMP Tracker - Main Application
Comprehensive tracking system for South Atlantic Fishery Management Plan amendments
"""

import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import logging
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__,
            template_folder='public',
            static_folder='public/assets')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Import routes
from src.routes import api_routes, web_routes

# Register blueprints
app.register_blueprint(api_routes.bp, url_prefix='/api')
app.register_blueprint(web_routes.bp)

# Initialize scheduler for automated scraping
from src.services.scheduler import init_scheduler
scheduler = init_scheduler(app)

@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

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

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

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
