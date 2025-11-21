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

# CORS configuration - allows frontend to communicate with backend API
# Supports both monolithic deployment (same origin) and separated deployment (different domains)
CORS(app, origins=[
    "http://localhost:5173",  # Local development (Vite dev server)
    "https://safmc-fmp-tracker.onrender.com",  # Current monolithic deployment
    "https://safmc-fmp-tracker-frontend.onrender.com",  # New separated frontend Static Site
])

# Import models after db initialization
from src.models.action import Action
from src.models.meeting import Meeting
from src.models.comment import Comment
from src.models.milestone import Milestone
from src.models.scrape_log import ScrapeLog
from src.models.user import User

# Import workplan models
from src.models.workplan import (
    WorkplanVersion,
    WorkplanItem,
    WorkplanMilestone,
    MilestoneType,
    WorkplanUploadLog
)

# Import SAFE/SEDAR models
from src.models.safe_sedar import (
    SAFEReport,
    SAFEReportStock,
    SAFEReportSection,
    SEDARAssessment,
    AssessmentActionLink,
    SAFESEDARScrapeLog,
    StockStatusDefinition
)

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

def ensure_stock_assessment_columns():
    """Ensure all required columns exist in stock_assessments table"""
    try:
        with app.app_context():
            # Check which columns exist
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'stock_assessments';
            """))
            existing_columns = {row[0] for row in result.fetchall()}

            if not existing_columns:
                logger.info("Stock assessments table doesn't exist yet, skipping column check")
                return

            required_columns = {
                'last_scraped': "ADD COLUMN last_scraped TIMESTAMP",
                'overfishing_occurring': "ADD COLUMN overfishing_occurring BOOLEAN DEFAULT FALSE",
                'overfished': "ADD COLUMN overfished BOOLEAN DEFAULT FALSE",
                'fmps_affected': "ADD COLUMN fmps_affected TEXT[]",
                'keywords': "ADD COLUMN keywords TEXT[]"
            }

            columns_to_add = []
            for col_name, col_sql in required_columns.items():
                if col_name not in existing_columns:
                    columns_to_add.append(col_sql)
                    logger.info(f"Will add missing column: {col_name}")

            if columns_to_add:
                logger.info(f"Adding {len(columns_to_add)} missing columns to stock_assessments table...")
                for column_sql in columns_to_add:
                    db.session.execute(text(f"ALTER TABLE stock_assessments {column_sql}"))
                db.session.commit()
                logger.info("✓ Missing stock assessment columns added successfully")
            else:
                logger.info("All required stock assessment columns exist")

    except Exception as e:
        logger.error(f"Error ensuring stock assessment columns: {e}")
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

def init_ai_query_log():
    """Create AI query log table for tracking and troubleshooting"""
    try:
        with app.app_context():
            # Check if table already exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'ai_query_log'
                );
            """))
            table_exists = result.scalar()

            if not table_exists:
                logger.info("Creating ai_query_log table...")

                # Create AI query log table
                db.session.execute(text("""
                    CREATE TABLE ai_query_log (
                        id SERIAL PRIMARY KEY,

                        -- User information
                        user_id INTEGER,
                        user_email VARCHAR(255),
                        user_ip VARCHAR(50),

                        -- Query details
                        question TEXT NOT NULL,
                        response TEXT,

                        -- Context provided to AI
                        context_documents INTEGER[],
                        context_size_chars INTEGER,

                        -- API details
                        model VARCHAR(100),
                        tokens_used INTEGER,
                        response_time_ms INTEGER,

                        -- Status
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT,

                        -- Metadata
                        user_agent TEXT,
                        session_id VARCHAR(100),

                        -- Timestamps
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                        -- Full text search on queries
                        search_vector TSVECTOR
                    );
                """))

                # Create indices
                db.session.execute(text("""
                    CREATE INDEX idx_ai_log_user ON ai_query_log(user_id);
                    CREATE INDEX idx_ai_log_created ON ai_query_log(created_at DESC);
                    CREATE INDEX idx_ai_log_success ON ai_query_log(success);
                    CREATE INDEX idx_ai_log_search ON ai_query_log USING GIN(search_vector);
                """))

                # Create trigger for search vector
                db.session.execute(text("""
                    CREATE OR REPLACE FUNCTION ai_log_search_vector_update() RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.search_vector :=
                            setweight(to_tsvector('english', COALESCE(NEW.question, '')), 'A') ||
                            setweight(to_tsvector('english', COALESCE(NEW.response, '')), 'B');
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;

                    CREATE TRIGGER ai_log_search_vector_trigger
                    BEFORE INSERT OR UPDATE OF question, response
                    ON ai_query_log
                    FOR EACH ROW
                    EXECUTE FUNCTION ai_log_search_vector_update();
                """))

                db.session.commit()
                logger.info("✓ AI query log table created successfully")
            else:
                logger.info("AI query log table already exists")
    except Exception as e:
        logger.error(f"Error creating AI query log table: {e}")
        db.session.rollback()

def init_fmp_document_tables():
    """Create FMP document tables for document management system"""
    try:
        with app.app_context():
            # Check if tables already exist
            result = db.session.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_name IN ('fmp_documents', 'document_chunks', 'document_scrape_queue');
            """))
            existing_tables = {row[0] for row in result.fetchall()}

            if len(existing_tables) == 3:
                logger.info("FMP document tables already exist")
                return

            logger.info("Creating FMP document tables...")

            # Create fmp_documents table
            if 'fmp_documents' not in existing_tables:
                db.session.execute(text("""
                    CREATE TABLE fmp_documents (
                        id SERIAL PRIMARY KEY,
                        document_id VARCHAR(64) UNIQUE NOT NULL,

                        -- Basic metadata
                        title TEXT NOT NULL,
                        document_type VARCHAR(100),
                        fmp VARCHAR(100),
                        amendment_number VARCHAR(50),

                        -- Dates
                        document_date DATE,
                        publication_date DATE,
                        effective_date DATE,

                        -- Status and source
                        status VARCHAR(50),
                        source_url TEXT,
                        download_url TEXT,

                        -- Content
                        description TEXT,
                        full_text TEXT,
                        summary TEXT,

                        -- Categorization
                        keywords TEXT[],
                        species TEXT[],
                        topics TEXT[],

                        -- File info
                        file_size_bytes INTEGER,
                        page_count INTEGER,

                        -- Processing status
                        processed BOOLEAN DEFAULT FALSE,
                        indexed BOOLEAN DEFAULT FALSE,

                        -- Search
                        search_vector TSVECTOR,

                        -- Metadata
                        metadata JSONB,

                        -- Timestamps
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_scraped TIMESTAMP
                    );
                """))

                db.session.execute(text("""
                    CREATE INDEX idx_fmp_docs_type ON fmp_documents(document_type);
                    CREATE INDEX idx_fmp_docs_fmp ON fmp_documents(fmp);
                    CREATE INDEX idx_fmp_docs_status ON fmp_documents(status);
                    CREATE INDEX idx_fmp_docs_date ON fmp_documents(document_date DESC);
                    CREATE INDEX idx_fmp_docs_search ON fmp_documents USING GIN(search_vector);
                    CREATE INDEX idx_fmp_docs_keywords ON fmp_documents USING GIN(keywords);
                """))

                db.session.execute(text("""
                    CREATE OR REPLACE FUNCTION fmp_docs_search_vector_update() RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.search_vector :=
                            setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                            setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
                            setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'C') ||
                            setweight(to_tsvector('english', COALESCE(NEW.full_text, '')), 'D');
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;

                    CREATE TRIGGER fmp_docs_search_vector_trigger
                    BEFORE INSERT OR UPDATE OF title, description, summary, full_text
                    ON fmp_documents
                    FOR EACH ROW
                    EXECUTE FUNCTION fmp_docs_search_vector_update();
                """))

                logger.info("✓ fmp_documents table created")

            # Create document_chunks table
            if 'document_chunks' not in existing_tables:
                db.session.execute(text("""
                    CREATE TABLE document_chunks (
                        id SERIAL PRIMARY KEY,
                        document_id VARCHAR(64) REFERENCES fmp_documents(document_id) ON DELETE CASCADE,

                        chunk_index INTEGER NOT NULL,
                        chunk_text TEXT NOT NULL,
                        chunk_type VARCHAR(50),

                        section_title TEXT,
                        page_number INTEGER,

                        embedding_vector REAL[],

                        metadata JSONB,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                        UNIQUE(document_id, chunk_index)
                    );
                """))

                db.session.execute(text("""
                    CREATE INDEX idx_doc_chunks_doc_id ON document_chunks(document_id);
                    CREATE INDEX idx_doc_chunks_type ON document_chunks(chunk_type);
                """))

                logger.info("✓ document_chunks table created")

            # Create document_scrape_queue table
            if 'document_scrape_queue' not in existing_tables:
                db.session.execute(text("""
                    CREATE TABLE document_scrape_queue (
                        id SERIAL PRIMARY KEY,
                        url TEXT UNIQUE NOT NULL,
                        document_type VARCHAR(100),
                        fmp VARCHAR(100),

                        priority INTEGER DEFAULT 5,
                        status VARCHAR(50) DEFAULT 'pending',

                        attempts INTEGER DEFAULT 0,
                        max_attempts INTEGER DEFAULT 3,

                        metadata JSONB,
                        error_message TEXT,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        processed_at TIMESTAMP
                    );
                """))

                db.session.execute(text("""
                    CREATE INDEX idx_scrape_queue_status ON document_scrape_queue(status);
                    CREATE INDEX idx_scrape_queue_priority ON document_scrape_queue(priority, created_at);
                """))

                logger.info("✓ document_scrape_queue table created")

            db.session.commit()
            logger.info("✓ FMP document tables created successfully")

    except Exception as e:
        logger.error(f"Error creating FMP document tables: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

# Initialize tables on startup
with app.app_context():
    init_stock_assessment_tables()
    ensure_stock_assessment_columns()
    init_fisherypulse_columns()
    run_comment_migration()
    init_contacts_and_orgs()
    init_ai_query_log()
    init_fmp_document_tables()

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
from src.routes.api_routes import bp as api_bp
from src.routes.auth_routes import bp as auth_bp
from src.routes.admin_routes import bp as admin_bp
from src.routes.stock_assessment_routes import stock_assessment_bp
from src.routes.workplan_routes import bp as workplan_bp
from src.routes.species_routes import bp as species_bp
from src.routes.sedar_routes import bp as sedar_bp
from src.routes.safe_report_routes import bp as safe_reports_bp
from src.routes.comparison_routes import bp as comparison_bp
from src.routes.export_routes import bp as export_bp

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_bp)
app.register_blueprint(stock_assessment_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(workplan_bp)
app.register_blueprint(species_bp)
app.register_blueprint(sedar_bp)
app.register_blueprint(safe_reports_bp)
app.register_blueprint(comparison_bp)
app.register_blueprint(export_bp)

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
