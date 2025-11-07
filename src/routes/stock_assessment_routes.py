"""
Stock Assessment Routes for SAFMC FMP Tracker
Handles API endpoints for stock assessment data from SEDAR and StockSMART
"""

from flask import Blueprint, jsonify, request
import logging
from datetime import datetime
from sqlalchemy import text, func
from src.config.extensions import db

logger = logging.getLogger(__name__)

stock_assessment_bp = Blueprint('stock_assessments', __name__)


@stock_assessment_bp.route('/api/assessments', methods=['GET'])
def get_assessments():
    """
    Get all stock assessments with optional filtering

    Query params:
        - species: Filter by species name
        - status: Filter by assessment status
        - overfished: Filter by overfished flag (true/false)
        - overfishing: Filter by overfishing flag (true/false)
        - fmp: Filter by FMP
        - limit: Limit number of results (default 100)
        - offset: Pagination offset (default 0)
    """
    try:
        from src.database import get_db_connection

        # Get query parameters
        species = request.args.get('species')
        status = request.args.get('status')
        overfished = request.args.get('overfished')
        overfishing = request.args.get('overfishing')
        fmp = request.args.get('fmp')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        conn = get_db_connection()
        cur = conn.cursor()

        # Build query with filters
        query = """
            SELECT
                id, sedar_number, species, scientific_name, stock_name,
                assessment_type, status, start_date, completion_date,
                stock_status, overfishing_occurring, overfished,
                biomass_current, biomass_msy,
                fishing_mortality_current, fishing_mortality_msy,
                overfishing_limit, acceptable_biological_catch, annual_catch_limit,
                keywords, fmps_affected, source_url, document_url,
                created_at, updated_at
            FROM stock_assessments
            WHERE 1=1
        """
        params = []

        if species:
            query += " AND species ILIKE %s"
            params.append(f"%{species}%")

        if status:
            query += " AND status = %s"
            params.append(status)

        if overfished is not None:
            query += " AND overfished = %s"
            params.append(overfished.lower() == 'true')

        if overfishing is not None:
            query += " AND overfishing_occurring = %s"
            params.append(overfishing.lower() == 'true')

        if fmp:
            query += " AND %s = ANY(fmps_affected)"
            params.append(fmp)

        query += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(query, params)
        rows = cur.fetchall()

        # Get total count
        count_query = "SELECT COUNT(*) FROM stock_assessments WHERE 1=1"
        count_params = []

        if species:
            count_query += " AND species ILIKE %s"
            count_params.append(f"%{species}%")

        if status:
            count_query += " AND status = %s"
            count_params.append(status)

        if overfished is not None:
            count_query += " AND overfished = %s"
            count_params.append(overfished.lower() == 'true')

        if overfishing is not None:
            count_query += " AND overfishing_occurring = %s"
            count_params.append(overfishing.lower() == 'true')

        if fmp:
            count_query += " AND %s = ANY(fmps_affected)"
            count_params.append(fmp)

        cur.execute(count_query, count_params)
        total_count = cur.fetchone()[0]

        assessments = []
        for row in rows:
            assessments.append({
                'id': row[0],
                'sedar_number': row[1],
                'species': row[2],
                'scientific_name': row[3],
                'stock_name': row[4],
                'assessment_type': row[5],
                'status': row[6],
                'start_date': row[7].isoformat() if row[7] else None,
                'completion_date': row[8].isoformat() if row[8] else None,
                'stock_status': row[9],
                'overfishing_occurring': row[10],
                'overfished': row[11],
                'biomass_current': float(row[12]) if row[12] else None,
                'biomass_msy': float(row[13]) if row[13] else None,
                'b_bmsy': float(row[12] / row[13]) if row[12] and row[13] and row[13] != 0 else None,
                'fishing_mortality_current': float(row[14]) if row[14] else None,
                'fishing_mortality_msy': float(row[15]) if row[15] else None,
                'f_fmsy': float(row[14] / row[15]) if row[14] and row[15] and row[15] != 0 else None,
                'overfishing_limit': float(row[16]) if row[16] else None,
                'acceptable_biological_catch': float(row[17]) if row[17] else None,
                'annual_catch_limit': float(row[18]) if row[18] else None,
                'keywords': row[19],
                'fmps_affected': row[20],
                'source_url': row[21],
                'document_url': row[22],
                'created_at': row[23].isoformat() if row[23] else None,
                'updated_at': row[24].isoformat() if row[24] else None
            })

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'assessments': assessments,
            'total': total_count,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"Error fetching assessments: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@stock_assessment_bp.route('/api/assessments/<int:assessment_id>', methods=['GET'])
def get_assessment(assessment_id):
    """Get detailed information for a specific stock assessment"""
    try:
        from src.database import get_db_connection

        conn = get_db_connection()
        cur = conn.cursor()

        # Get assessment details
        cur.execute("""
            SELECT
                id, sedar_number, species, scientific_name, stock_name,
                assessment_type, status, start_date, completion_date,
                stock_status, overfishing_occurring, overfished,
                biomass_current, biomass_msy,
                fishing_mortality_current, fishing_mortality_msy,
                overfishing_limit, acceptable_biological_catch, annual_catch_limit,
                keywords, fmps_affected, source_url, document_url,
                created_at, updated_at
            FROM stock_assessments
            WHERE id = %s
        """, (assessment_id,))

        row = cur.fetchone()

        if not row:
            return jsonify({'success': False, 'error': 'Assessment not found'}), 404

        assessment = {
            'id': row[0],
            'sedar_number': row[1],
            'species': row[2],
            'scientific_name': row[3],
            'stock_name': row[4],
            'assessment_type': row[5],
            'status': row[6],
            'start_date': row[7].isoformat() if row[7] else None,
            'completion_date': row[8].isoformat() if row[8] else None,
            'stock_status': row[9],
            'overfishing_occurring': row[10],
            'overfished': row[11],
            'biomass_current': float(row[12]) if row[12] else None,
            'biomass_msy': float(row[13]) if row[13] else None,
            'b_bmsy': float(row[12] / row[13]) if row[12] and row[13] and row[13] != 0 else None,
            'fishing_mortality_current': float(row[14]) if row[14] else None,
            'fishing_mortality_msy': float(row[15]) if row[15] else None,
            'f_fmsy': float(row[14] / row[15]) if row[14] and row[15] and row[15] != 0 else None,
            'overfishing_limit': float(row[16]) if row[16] else None,
            'acceptable_biological_catch': float(row[17]) if row[17] else None,
            'annual_catch_limit': float(row[18]) if row[18] else None,
            'keywords': row[19],
            'fmps_affected': row[20],
            'source_url': row[21],
            'document_url': row[22],
            'created_at': row[23].isoformat() if row[23] else None,
            'updated_at': row[24].isoformat() if row[24] else None
        }

        # Get comments for this assessment
        cur.execute("""
            SELECT
                id, commenter_name, organization, comment_date,
                comment_type, comment_text, source_url, created_at
            FROM assessment_comments
            WHERE assessment_id = %s
            ORDER BY comment_date DESC
        """, (assessment_id,))

        comment_rows = cur.fetchall()
        comments = []
        for c_row in comment_rows:
            comments.append({
                'id': c_row[0],
                'commenter_name': c_row[1],
                'organization': c_row[2],
                'comment_date': c_row[3].isoformat() if c_row[3] else None,
                'comment_type': c_row[4],
                'comment_text': c_row[5],
                'source_url': c_row[6],
                'created_at': c_row[7].isoformat() if c_row[7] else None
            })

        assessment['comments'] = comments

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'assessment': assessment
        })

    except Exception as e:
        logger.error(f"Error fetching assessment {assessment_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@stock_assessment_bp.route('/api/assessments/stats', methods=['GET'])
def get_assessment_stats():
    """Get summary statistics for stock assessments, separated by SAFMC-only and jointly-managed"""
    try:
        # Total assessments
        total_result = db.session.execute(text("SELECT COUNT(*) FROM stock_assessments"))
        total = total_result.scalar()

        # SAFMC-only stocks (array has 1 element or contains only South Atlantic FMP)
        safmc_only_result = db.session.execute(text("""
            SELECT COUNT(*) FROM stock_assessments
            WHERE array_length(fmps_affected, 1) = 1 OR fmps_affected IS NULL
        """))
        safmc_only_total = safmc_only_result.scalar()

        # Jointly-managed stocks (array has more than 1 element)
        joint_result = db.session.execute(text("""
            SELECT COUNT(*) FROM stock_assessments
            WHERE array_length(fmps_affected, 1) > 1
        """))
        joint_total = joint_result.scalar()

        # SAFMC-only stocks breakdown
        safmc_overfished = db.session.execute(text("""
            SELECT COUNT(*) FROM stock_assessments
            WHERE (array_length(fmps_affected, 1) = 1 OR fmps_affected IS NULL)
            AND overfished = TRUE
        """)).scalar()

        safmc_overfishing = db.session.execute(text("""
            SELECT COUNT(*) FROM stock_assessments
            WHERE (array_length(fmps_affected, 1) = 1 OR fmps_affected IS NULL)
            AND overfishing_occurring = TRUE
        """)).scalar()

        safmc_healthy = db.session.execute(text("""
            SELECT COUNT(*) FROM stock_assessments
            WHERE (array_length(fmps_affected, 1) = 1 OR fmps_affected IS NULL)
            AND overfished = FALSE AND overfishing_occurring = FALSE
        """)).scalar()

        # Jointly-managed stocks breakdown
        joint_overfished = db.session.execute(text("""
            SELECT COUNT(*) FROM stock_assessments
            WHERE array_length(fmps_affected, 1) > 1 AND overfished = TRUE
        """)).scalar()

        joint_overfishing = db.session.execute(text("""
            SELECT COUNT(*) FROM stock_assessments
            WHERE array_length(fmps_affected, 1) > 1 AND overfishing_occurring = TRUE
        """)).scalar()

        joint_healthy = db.session.execute(text("""
            SELECT COUNT(*) FROM stock_assessments
            WHERE array_length(fmps_affected, 1) > 1
            AND overfished = FALSE AND overfishing_occurring = FALSE
        """)).scalar()

        # Overall totals (for backward compatibility)
        overfished_result = db.session.execute(text("SELECT COUNT(*) FROM stock_assessments WHERE overfished = TRUE"))
        overfished = overfished_result.scalar()

        overfishing_result = db.session.execute(text("SELECT COUNT(*) FROM stock_assessments WHERE overfishing_occurring = TRUE"))
        overfishing = overfishing_result.scalar()

        healthy_result = db.session.execute(text("""
            SELECT COUNT(*) FROM stock_assessments
            WHERE overfished = FALSE AND overfishing_occurring = FALSE
        """))
        healthy = healthy_result.scalar()

        # In progress assessments
        in_progress_result = db.session.execute(text("""
            SELECT COUNT(*) FROM stock_assessments
            WHERE status IN ('In Progress', 'Planning')
        """))
        in_progress = in_progress_result.scalar()

        # By FMP
        fmp_result = db.session.execute(text("""
            SELECT unnest(fmps_affected) as fmp, COUNT(*)
            FROM stock_assessments
            WHERE fmps_affected IS NOT NULL
            GROUP BY fmp
            ORDER BY COUNT(*) DESC
        """))
        fmp_counts = {}
        for row in fmp_result.fetchall():
            fmp_counts[row[0]] = row[1]

        # Recent assessments (last 5 years)
        recent_result = db.session.execute(text("""
            SELECT species, sedar_number, completion_date, stock_status
            FROM stock_assessments
            WHERE completion_date >= (CURRENT_DATE - INTERVAL '5 years')
            ORDER BY completion_date DESC
            LIMIT 10
        """))
        recent_rows = recent_result.fetchall()
        recent_assessments = []
        for row in recent_rows:
            recent_assessments.append({
                'species': row[0],
                'sedar_number': row[1],
                'completion_date': row[2].isoformat() if row[2] else None,
                'stock_status': row[3]
            })

        return jsonify({
            'success': True,
            'stats': {
                'total': total or 0,
                'overfished': overfished or 0,
                'overfishing': overfishing or 0,
                'healthy': healthy or 0,
                'in_progress': in_progress or 0,
                'safmc_only': {
                    'total': safmc_only_total or 0,
                    'overfished': safmc_overfished or 0,
                    'overfishing': safmc_overfishing or 0,
                    'healthy': safmc_healthy or 0
                },
                'jointly_managed': {
                    'total': joint_total or 0,
                    'overfished': joint_overfished or 0,
                    'overfishing': joint_overfishing or 0,
                    'healthy': joint_healthy or 0
                },
                'by_fmp': fmp_counts,
                'recent_assessments': recent_assessments
            }
        })

    except Exception as e:
        logger.error(f"Error fetching assessment stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@stock_assessment_bp.route('/api/assessments/kobe-data', methods=['GET'])
def get_kobe_data():
    """
    Get B/BMSY and F/FMSY data for Kobe plot visualization
    Returns stocks with both biomass and fishing mortality ratios
    """
    try:
        from src.database import get_db_connection

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id, species, sedar_number,
                biomass_current, biomass_msy,
                fishing_mortality_current, fishing_mortality_msy,
                overfished, overfishing_occurring,
                stock_status, fmps_affected
            FROM stock_assessments
            WHERE biomass_current IS NOT NULL
              AND biomass_msy IS NOT NULL
              AND biomass_msy != 0
              AND fishing_mortality_current IS NOT NULL
              AND fishing_mortality_msy IS NOT NULL
              AND fishing_mortality_msy != 0
            ORDER BY species
        """)

        rows = cur.fetchall()
        kobe_data = []

        for row in rows:
            b_bmsy = float(row[3] / row[4])
            f_fmsy = float(row[5] / row[6])

            # Determine quadrant
            if b_bmsy >= 1.0 and f_fmsy <= 1.0:
                quadrant = 'healthy'  # Green - good condition
            elif b_bmsy < 1.0 and f_fmsy > 1.0:
                quadrant = 'critical'  # Red - overfished and overfishing
            elif b_bmsy < 1.0 and f_fmsy <= 1.0:
                quadrant = 'recovering'  # Yellow - overfished but not overfishing
            else:  # b_bmsy >= 1.0 and f_fmsy > 1.0
                quadrant = 'warning'  # Orange - overfishing but not overfished

            kobe_data.append({
                'id': row[0],
                'species': row[1],
                'sedar_number': row[2],
                'b_bmsy': round(b_bmsy, 3),
                'f_fmsy': round(f_fmsy, 3),
                'overfished': row[7],
                'overfishing_occurring': row[8],
                'stock_status': row[9],
                'fmps_affected': row[10],
                'quadrant': quadrant
            })

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'kobe_data': kobe_data,
            'total': len(kobe_data)
        })

    except Exception as e:
        logger.error(f"Error fetching Kobe data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@stock_assessment_bp.route('/api/scrape/sedar', methods=['POST'])
def scrape_sedar():
    """Trigger SEDAR scraper to update stock assessment data"""
    try:
        # Import scraper (will create this next)
        from src.scrapers.sedar_scraper import SEDARScraper

        scraper = SEDARScraper()
        results = scraper.scrape_assessments()

        return jsonify({
            'success': True,
            'message': 'SEDAR scraping completed',
            'results': results
        })

    except Exception as e:
        logger.error(f"Error scraping SEDAR: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@stock_assessment_bp.route('/api/scrape/stocksmart', methods=['POST'])
def scrape_stocksmart():
    """Trigger StockSMART scraper to update stock status data"""
    try:
        # Import scraper (will create this next)
        from src.scrapers.stocksmart_scraper import StockSMARTScraper

        scraper = StockSMARTScraper()
        results = scraper.get_stock_status()

        return jsonify({
            'success': True,
            'message': 'StockSMART scraping completed',
            'results': results
        })

    except Exception as e:
        logger.error(f"Error scraping StockSMART: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
