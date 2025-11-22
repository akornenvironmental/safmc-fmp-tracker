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
                id, sedar_number, species_common_name, species_scientific_name, stock_region,
                assessment_type, status, start_date, completion_date,
                stock_status, overfished, overfishing_occurring,
                b_bmsy, f_fmsy, fmp, sedar_url, assessment_report_url,
                fmps_affected, created_at, updated_at
            FROM stock_assessments
            WHERE 1=1
        """
        params = []

        if species:
            query += " AND species_common_name ILIKE %s"
            params.append(f"%{species}%")

        if status:
            query += " AND status = %s"
            params.append(status)

        if overfished is not None:
            query += " AND stock_status ILIKE %s"
            params.append('%overfished%' if overfished.lower() == 'true' else '%not overfished%')

        if overfishing is not None:
            query += " AND stock_status ILIKE %s"
            params.append('%overfishing%' if overfishing.lower() == 'true' else '%not overfishing%')

        if fmp:
            query += " AND fmp = %s"
            params.append(fmp)

        query += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(query, params)
        rows = cur.fetchall()

        # Get total count
        count_query = "SELECT COUNT(*) FROM stock_assessments WHERE 1=1"
        count_params = []

        if species:
            count_query += " AND species_common_name ILIKE %s"
            count_params.append(f"%{species}%")

        if status:
            count_query += " AND status = %s"
            count_params.append(status)

        if overfished is not None:
            count_query += " AND stock_status ILIKE %s"
            count_params.append('%overfished%' if overfished.lower() == 'true' else '%not overfished%')

        if overfishing is not None:
            count_query += " AND stock_status ILIKE %s"
            count_params.append('%overfishing%' if overfishing.lower() == 'true' else '%not overfishing%')

        if fmp:
            count_query += " AND fmp = %s"
            count_params.append(fmp)

        cur.execute(count_query, count_params)
        total_count = cur.fetchone()[0]

        assessments = []
        for row in rows:
            assessments.append({
                'id': row[0],
                'sedar_number': row[1],
                'species': row[2],  # species_common_name
                'scientific_name': row[3],
                'stock_name': row[4],  # stock_region
                'assessment_type': row[5],
                'status': row[6],
                'start_date': row[7].isoformat() if row[7] else None,
                'completion_date': row[8].isoformat() if row[8] else None,
                'stock_status': row[9],
                'overfished': row[10],
                'overfishing_occurring': row[11],
                'b_bmsy': float(row[12]) if row[12] else None,
                'f_fmsy': float(row[13]) if row[13] else None,
                'fmp': row[14],
                'source_url': row[15],
                'document_url': row[16],
                'fmps_affected': row[17],
                'created_at': row[18].isoformat() if row[18] else None,
                'updated_at': row[19].isoformat() if row[19] else None
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
                id, sedar_number, species_common_name, species_scientific_name, stock_region,
                assessment_type, status, start_date, completion_date,
                stock_status,
                overfishing_limit, acceptable_biological_catch, annual_catch_limit,
                optimum_yield, units, fmp, sedar_url, assessment_report_url,
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
            'species': row[2],  # species_common_name
            'scientific_name': row[3],  # species_scientific_name
            'stock_region': row[4],
            'assessment_type': row[5],
            'status': row[6],
            'start_date': row[7].isoformat() if row[7] else None,
            'completion_date': row[8].isoformat() if row[8] else None,
            'stock_status': row[9],
            'overfishing_limit': float(row[10]) if row[10] else None,
            'acceptable_biological_catch': float(row[11]) if row[11] else None,
            'annual_catch_limit': float(row[12]) if row[12] else None,
            'optimum_yield': float(row[13]) if row[13] else None,
            'units': row[14],
            'fmp': row[15],
            'sedar_url': row[16],
            'assessment_report_url': row[17],
            'created_at': row[18].isoformat() if row[18] else None,
            'updated_at': row[19].isoformat() if row[19] else None
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
            SELECT fmp, COUNT(*)
            FROM stock_assessments
            WHERE fmp IS NOT NULL
            GROUP BY fmp
            ORDER BY COUNT(*) DESC
        """))
        fmp_counts = {}
        for row in fmp_result.fetchall():
            fmp_counts[row[0]] = row[1]

        # Recent assessments (last 5 years)
        recent_result = db.session.execute(text("""
            SELECT species_common_name, sedar_number, completion_date, stock_status
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


@stock_assessment_bp.route('/api/assessments/seed', methods=['POST'])
def seed_assessments():
    """Seed the database with known SAFMC stock assessment data"""
    try:
        from datetime import date as dt_date
        from src.database import get_db_connection

        # Stock assessment data
        stock_data = [
            {'sedar_number': 'SEDAR 73', 'species_common_name': 'Red Snapper', 'species_scientific_name': 'Lutjanus campechanus', 'stock_region': 'South Atlantic', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2021, 10, 1), 'stock_status': 'Rebuilding', 'overfished': True, 'overfishing_occurring': False, 'b_bmsy': 0.42, 'f_fmsy': 0.85, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-73/'},
            {'sedar_number': 'SEDAR 68', 'species_common_name': 'Golden Tilefish', 'species_scientific_name': 'Lopholatilus chamaeleonticeps', 'stock_region': 'South Atlantic', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2020, 6, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.45, 'f_fmsy': 0.62, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-68/'},
            {'sedar_number': 'SEDAR 76', 'species_common_name': 'Blueline Tilefish', 'species_scientific_name': 'Caulolatilus microps', 'stock_region': 'South Atlantic', 'assessment_type': 'Update', 'status': 'Completed', 'completion_date': dt_date(2022, 3, 1), 'stock_status': 'Overfished', 'overfished': True, 'overfishing_occurring': False, 'b_bmsy': 0.78, 'f_fmsy': 0.89, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-76/'},
            {'sedar_number': 'SEDAR 41', 'species_common_name': 'Gray Triggerfish', 'species_scientific_name': 'Balistes capriscus', 'stock_region': 'South Atlantic', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2016, 7, 1), 'stock_status': 'Overfished, overfishing occurring', 'overfished': True, 'overfishing_occurring': True, 'b_bmsy': 0.35, 'f_fmsy': 1.45, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-41/'},
            {'sedar_number': 'SEDAR 24', 'species_common_name': 'Vermilion Snapper', 'species_scientific_name': 'Rhomboplites aurorubens', 'stock_region': 'South Atlantic', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2020, 5, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.52, 'f_fmsy': 0.78, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-24/'},
            {'sedar_number': 'SEDAR 25', 'species_common_name': 'Black Sea Bass', 'species_scientific_name': 'Centropristis striata', 'stock_region': 'South Atlantic', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2018, 9, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.89, 'f_fmsy': 0.54, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-25/'},
            {'sedar_number': 'SEDAR 36', 'species_common_name': 'Red Porgy', 'species_scientific_name': 'Pagrus pagrus', 'stock_region': 'South Atlantic', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2015, 8, 1), 'stock_status': 'Overfished', 'overfished': True, 'overfishing_occurring': False, 'b_bmsy': 0.65, 'f_fmsy': 0.72, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-36/'},
            {'sedar_number': 'SEDAR 53', 'species_common_name': 'Greater Amberjack', 'species_scientific_name': 'Seriola dumerili', 'stock_region': 'South Atlantic', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2020, 1, 1), 'stock_status': 'Overfished, overfishing occurring', 'overfished': True, 'overfishing_occurring': True, 'b_bmsy': 0.52, 'f_fmsy': 1.32, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-53/'},
            {'sedar_number': 'SEDAR 10', 'species_common_name': 'Gag Grouper', 'species_scientific_name': 'Mycteroperca microlepis', 'stock_region': 'South Atlantic', 'assessment_type': 'Update', 'status': 'Completed', 'completion_date': dt_date(2014, 4, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.15, 'f_fmsy': 0.68, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-10/'},
            {'sedar_number': 'SEDAR 36U', 'species_common_name': 'Snowy Grouper', 'species_scientific_name': 'Hyporthodus niveatus', 'stock_region': 'South Atlantic', 'assessment_type': 'Update', 'status': 'Completed', 'completion_date': dt_date(2023, 6, 1), 'stock_status': 'Overfished', 'overfished': True, 'overfishing_occurring': False, 'b_bmsy': 0.58, 'f_fmsy': 0.92, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-36/'},
            {'sedar_number': 'SEDAR 19', 'species_common_name': 'Red Grouper', 'species_scientific_name': 'Epinephelus morio', 'stock_region': 'South Atlantic', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2010, 12, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.35, 'f_fmsy': 0.72, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-19/'},
            {'sedar_number': 'SEDAR 37', 'species_common_name': 'Hogfish', 'species_scientific_name': 'Lachnolaimus maximus', 'stock_region': 'Florida Keys/East Florida', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2014, 10, 1), 'stock_status': 'Overfished', 'overfished': True, 'overfishing_occurring': True, 'b_bmsy': 0.48, 'f_fmsy': 1.28, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-37/'},
            {'sedar_number': 'SEDAR 64', 'species_common_name': 'Yellowtail Snapper', 'species_scientific_name': 'Ocyurus chrysurus', 'stock_region': 'South Atlantic/Gulf of Mexico', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2020, 8, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 2.12, 'f_fmsy': 0.45, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-64/'},
            {'sedar_number': 'SEDAR 15A', 'species_common_name': 'Mutton Snapper', 'species_scientific_name': 'Lutjanus analis', 'stock_region': 'South Atlantic/Gulf of Mexico', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2023, 2, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.67, 'f_fmsy': 0.58, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-15a/'},
            {'sedar_number': 'SEDAR 47', 'species_common_name': 'Goliath Grouper', 'species_scientific_name': 'Epinephelus itajara', 'stock_region': 'South Atlantic', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2016, 5, 1), 'stock_status': 'Unknown - rebuilding', 'overfished': None, 'overfishing_occurring': False, 'b_bmsy': None, 'f_fmsy': None, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-47/'},
            {'sedar_number': 'SEDAR 38', 'species_common_name': 'King Mackerel', 'species_scientific_name': 'Scomberomorus cavalla', 'stock_region': 'South Atlantic Migratory Group', 'assessment_type': 'Update', 'status': 'Completed', 'completion_date': dt_date(2020, 11, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.62, 'f_fmsy': 0.52, 'fmp': 'Coastal Migratory Pelagics', 'sedar_url': 'https://sedarweb.org/sedar-38/'},
            {'sedar_number': 'SEDAR 28', 'species_common_name': 'Spanish Mackerel', 'species_scientific_name': 'Scomberomorus maculatus', 'stock_region': 'South Atlantic Migratory Group', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2020, 3, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.89, 'f_fmsy': 0.42, 'fmp': 'Coastal Migratory Pelagics', 'sedar_url': 'https://sedarweb.org/sedar-28/'},
            {'sedar_number': 'SEDAR 28U', 'species_common_name': 'Cobia', 'species_scientific_name': 'Rachycentron canadum', 'stock_region': 'South Atlantic Migratory Group', 'assessment_type': 'Update', 'status': 'Completed', 'completion_date': dt_date(2020, 7, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.42, 'f_fmsy': 0.65, 'fmp': 'Coastal Migratory Pelagics', 'sedar_url': 'https://sedarweb.org/sedar-28/'},
            {'sedar_number': 'SEDAR 82', 'species_common_name': 'Dolphin', 'species_scientific_name': 'Coryphaena hippurus', 'stock_region': 'Atlantic', 'assessment_type': 'Benchmark', 'status': 'In Progress', 'completion_date': None, 'stock_status': 'Unknown', 'overfished': None, 'overfishing_occurring': None, 'b_bmsy': None, 'f_fmsy': None, 'fmp': 'Dolphin Wahoo', 'sedar_url': 'https://sedarweb.org/sedar-82/'},
            {'sedar_number': None, 'species_common_name': 'Wahoo', 'species_scientific_name': 'Acanthocybium solandri', 'stock_region': 'Atlantic', 'assessment_type': None, 'status': 'No Assessment', 'completion_date': None, 'stock_status': 'Unknown', 'overfished': None, 'overfishing_occurring': None, 'b_bmsy': None, 'f_fmsy': None, 'fmp': 'Dolphin Wahoo', 'sedar_url': None},
            {'sedar_number': None, 'species_common_name': 'Spiny Lobster', 'species_scientific_name': 'Panulirus argus', 'stock_region': 'Southeast US', 'assessment_type': 'Data-limited', 'status': 'Completed', 'completion_date': dt_date(2019, 1, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.25, 'f_fmsy': 0.72, 'fmp': 'Spiny Lobster', 'sedar_url': None},
            {'sedar_number': None, 'species_common_name': 'Golden Crab', 'species_scientific_name': 'Chaceon fenneri', 'stock_region': 'South Atlantic', 'assessment_type': 'Data-limited', 'status': 'No Assessment', 'completion_date': None, 'stock_status': 'Unknown', 'overfished': None, 'overfishing_occurring': None, 'b_bmsy': None, 'f_fmsy': None, 'fmp': 'Golden Crab', 'sedar_url': None},
            {'sedar_number': None, 'species_common_name': 'Rock Shrimp', 'species_scientific_name': 'Sicyonia brevirostris', 'stock_region': 'South Atlantic', 'assessment_type': 'Data-limited', 'status': 'Completed', 'completion_date': dt_date(2018, 1, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': None, 'f_fmsy': None, 'fmp': 'Shrimp', 'sedar_url': None},
            {'sedar_number': None, 'species_common_name': 'Pink Shrimp', 'species_scientific_name': 'Penaeus duorarum', 'stock_region': 'South Atlantic', 'assessment_type': 'Data-limited', 'status': 'Completed', 'completion_date': dt_date(2018, 1, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': None, 'f_fmsy': None, 'fmp': 'Shrimp', 'sedar_url': None},
            {'sedar_number': 'SEDAR 50', 'species_common_name': 'Wreckfish', 'species_scientific_name': 'Polyprion americanus', 'stock_region': 'South Atlantic', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2016, 12, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.78, 'f_fmsy': 0.35, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-50/'},
            {'sedar_number': 'SEDAR 36S', 'species_common_name': 'Scamp', 'species_scientific_name': 'Mycteroperca phenax', 'stock_region': 'South Atlantic', 'assessment_type': 'Benchmark', 'status': 'Completed', 'completion_date': dt_date(2022, 11, 1), 'stock_status': 'Not overfished, overfishing not occurring', 'overfished': False, 'overfishing_occurring': False, 'b_bmsy': 1.32, 'f_fmsy': 0.68, 'fmp': 'Snapper Grouper', 'sedar_url': 'https://sedarweb.org/sedar-36/'},
            {'sedar_number': None, 'species_common_name': 'Black Grouper', 'species_scientific_name': 'Mycteroperca bonaci', 'stock_region': 'South Atlantic', 'assessment_type': 'Data-limited', 'status': 'Completed', 'completion_date': dt_date(2015, 6, 1), 'stock_status': 'Unknown', 'overfished': None, 'overfishing_occurring': None, 'b_bmsy': None, 'f_fmsy': None, 'fmp': 'Snapper Grouper', 'sedar_url': None},
        ]

        conn = get_db_connection()
        cur = conn.cursor()

        # Drop and recreate table with correct schema
        cur.execute("DROP TABLE IF EXISTS stock_assessments CASCADE")
        cur.execute("""
            CREATE TABLE stock_assessments (
                id SERIAL PRIMARY KEY,
                sedar_number VARCHAR(50),
                species_common_name VARCHAR(255),
                species_scientific_name VARCHAR(255),
                stock_region VARCHAR(255),
                assessment_type VARCHAR(100),
                status VARCHAR(100),
                start_date DATE,
                completion_date DATE,
                stock_status TEXT,
                overfished BOOLEAN,
                overfishing_occurring BOOLEAN,
                b_bmsy DECIMAL(10,4),
                f_fmsy DECIMAL(10,4),
                biomass_current DECIMAL(20,4),
                biomass_msy DECIMAL(20,4),
                fishing_mortality_current DECIMAL(10,4),
                fishing_mortality_msy DECIMAL(10,4),
                overfishing_limit DECIMAL(20,4),
                acceptable_biological_catch DECIMAL(20,4),
                annual_catch_limit DECIMAL(20,4),
                optimum_yield DECIMAL(20,4),
                units VARCHAR(100),
                fmp VARCHAR(255),
                fmps_affected TEXT[],
                sedar_url TEXT,
                assessment_report_url TEXT,
                source VARCHAR(100) DEFAULT 'SEDAR',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        inserted = 0
        updated = 0

        for stock in stock_data:
            cur.execute("SELECT id FROM stock_assessments WHERE species_common_name = %s", (stock['species_common_name'],))
            existing = cur.fetchone()

            if existing:
                cur.execute("""
                    UPDATE stock_assessments SET
                        sedar_number = COALESCE(%s, sedar_number),
                        species_scientific_name = COALESCE(%s, species_scientific_name),
                        stock_region = COALESCE(%s, stock_region),
                        assessment_type = COALESCE(%s, assessment_type),
                        status = COALESCE(%s, status),
                        completion_date = COALESCE(%s, completion_date),
                        stock_status = COALESCE(%s, stock_status),
                        overfished = %s,
                        overfishing_occurring = %s,
                        b_bmsy = %s,
                        f_fmsy = %s,
                        fmp = COALESCE(%s, fmp),
                        sedar_url = COALESCE(%s, sedar_url),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (stock.get('sedar_number'), stock.get('species_scientific_name'), stock.get('stock_region'),
                      stock.get('assessment_type'), stock.get('status'), stock.get('completion_date'),
                      stock.get('stock_status'), stock.get('overfished'), stock.get('overfishing_occurring'),
                      stock.get('b_bmsy'), stock.get('f_fmsy'), stock.get('fmp'), stock.get('sedar_url'), existing[0]))
                updated += 1
            else:
                cur.execute("""
                    INSERT INTO stock_assessments (
                        sedar_number, species_common_name, species_scientific_name,
                        stock_region, assessment_type, status, completion_date,
                        stock_status, overfished, overfishing_occurring,
                        b_bmsy, f_fmsy, fmp, sedar_url, fmps_affected
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (stock.get('sedar_number'), stock.get('species_common_name'), stock.get('species_scientific_name'),
                      stock.get('stock_region'), stock.get('assessment_type'), stock.get('status'),
                      stock.get('completion_date'), stock.get('stock_status'), stock.get('overfished'),
                      stock.get('overfishing_occurring'), stock.get('b_bmsy'), stock.get('f_fmsy'),
                      stock.get('fmp'), stock.get('sedar_url'), [stock.get('fmp')] if stock.get('fmp') else None))
                inserted += 1

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Stock assessments seeded successfully',
            'inserted': inserted,
            'updated': updated,
            'total': len(stock_data)
        })

    except Exception as e:
        logger.error(f"Error seeding stock assessments: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
