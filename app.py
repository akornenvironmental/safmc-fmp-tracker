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

# Database connection pool settings to handle timeouts
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # Verify connections before using them
    'pool_recycle': 300,    # Recycle connections after 5 minutes
    'pool_size': 10,        # Number of connections to maintain
    'max_overflow': 20,     # Additional connections when pool is full
    'connect_args': {
        'connect_timeout': 10,
        'options': '-c statement_timeout=30000'  # 30 second query timeout
    }
}

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

# Initialize stock assessment tables if they don't exist
def init_stock_assessment_tables():
    """Create stock assessment tables on startup if they don't exist"""
    try:
        with app.app_context():
            # Check if stock_assessments table exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'stock_assessments'
                );
            """))
            table_exists = result.scalar()

            if not table_exists:
                logger.info("Creating stock assessment tables...")

                # Create stock_assessments table
                db.session.execute(text("""
                    CREATE TABLE stock_assessments (
                        id SERIAL PRIMARY KEY,
                        sedar_number VARCHAR(50),
                        species VARCHAR(255) NOT NULL,
                        scientific_name VARCHAR(255),
                        stock_name VARCHAR(255),
                        assessment_type VARCHAR(100),
                        status VARCHAR(50),
                        start_date DATE,
                        completion_date DATE,
                        stock_status VARCHAR(100),
                        overfishing_occurring BOOLEAN DEFAULT FALSE,
                        overfished BOOLEAN DEFAULT FALSE,
                        biomass_current DECIMAL(15, 2),
                        biomass_msy DECIMAL(15, 2),
                        fishing_mortality_current DECIMAL(10, 4),
                        fishing_mortality_msy DECIMAL(10, 4),
                        overfishing_limit DECIMAL(15, 2),
                        acceptable_biological_catch DECIMAL(15, 2),
                        annual_catch_limit DECIMAL(15, 2),
                        keywords TEXT[],
                        fmps_affected TEXT[],
                        source_url TEXT,
                        document_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))

                # Create assessment_comments table
                db.session.execute(text("""
                    CREATE TABLE assessment_comments (
                        id SERIAL PRIMARY KEY,
                        assessment_id INTEGER REFERENCES stock_assessments(id) ON DELETE CASCADE,
                        commenter_name VARCHAR(255),
                        organization VARCHAR(255),
                        comment_date DATE,
                        comment_type VARCHAR(100),
                        comment_text TEXT,
                        source_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))

                # Create indexes
                db.session.execute(text("""
                    CREATE INDEX idx_stock_assessments_species ON stock_assessments(species);
                    CREATE INDEX idx_stock_assessments_sedar ON stock_assessments(sedar_number);
                    CREATE INDEX idx_stock_assessments_status ON stock_assessments(status);
                    CREATE INDEX idx_stock_assessments_updated ON stock_assessments(updated_at);
                    CREATE INDEX idx_assessment_comments_assessment ON assessment_comments(assessment_id);
                """))

                db.session.commit()
                logger.info("✓ Stock assessment tables created successfully")
            else:
                logger.info("Stock assessment tables already exist")

    except Exception as e:
        logger.error(f"Error initializing stock assessment tables: {e}")
        db.session.rollback()

# Initialize FisheryPulse meeting columns
def init_fisherypulse_columns():
    """Add region, source, and is_virtual columns to meetings table if they don't exist"""
    try:
        with app.app_context():
            # Check if columns exist
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'meetings' AND column_name IN ('region', 'source', 'is_virtual');
            """))
            existing_columns = [row[0] for row in result.fetchall()]

            columns_to_add = []
            if 'region' not in existing_columns:
                columns_to_add.append("ADD COLUMN region VARCHAR(100)")
            if 'source' not in existing_columns:
                columns_to_add.append("ADD COLUMN source VARCHAR(100)")
            if 'is_virtual' not in existing_columns:
                columns_to_add.append("ADD COLUMN is_virtual BOOLEAN DEFAULT FALSE")

            if columns_to_add:
                logger.info(f"Adding {len(columns_to_add)} new columns to meetings table...")
                for column_sql in columns_to_add:
                    db.session.execute(text(f"ALTER TABLE meetings {column_sql}"))
                db.session.commit()
                logger.info("✓ FisheryPulse columns added successfully")
            else:
                logger.info("FisheryPulse columns already exist")

    except Exception as e:
        logger.error(f"Error adding FisheryPulse columns: {e}")
        db.session.rollback()

def run_comment_migration():
    """Run migration to make action_id nullable in comments table"""
    try:
        with app.app_context():
            # Check if action_id is already nullable
            result = db.session.execute(text("""
                SELECT is_nullable
                FROM information_schema.columns
                WHERE table_name = 'comments'
                AND column_name = 'action_id';
            """))
            row = result.fetchone()

            if row and row[0] == 'NO':
                logger.info("Making action_id nullable in comments table...")
                db.session.execute(text("""
                    ALTER TABLE comments
                    ALTER COLUMN action_id DROP NOT NULL;
                """))
                db.session.commit()
                logger.info("✓ action_id is now nullable")
            else:
                logger.info("action_id already nullable, skipping migration")
    except Exception as e:
        logger.error(f"Error running comment migration: {e}")
        db.session.rollback()

def init_contacts_and_orgs():
    """Create contacts and organizations tables on startup if they don't exist"""
    try:
        with app.app_context():
            # Check if organizations table exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'organizations'
                );
            """))
            orgs_exist = result.scalar()

            # Check if contacts table exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'contacts'
                );
            """))
            contacts_exist = result.scalar()

            if not orgs_exist or not contacts_exist:
                logger.info("Creating contacts and organizations tables...")

                # Run the migration script
                from migrations.create_contacts_and_orgs import upgrade
                upgrade()

                logger.info("✓ Contacts and organizations tables created")
            else:
                logger.info("Contacts and organizations tables already exist")
    except Exception as e:
        logger.error(f"Error creating contacts/orgs tables: {e}")
        db.session.rollback()

# Initialize tables on startup
with app.app_context():
    init_stock_assessment_tables()
    init_fisherypulse_columns()
    run_comment_migration()
    init_contacts_and_orgs()

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
