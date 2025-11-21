"""
SAFE Reports API Routes
"""

import logging
from flask import Blueprint, jsonify, request
from sqlalchemy import desc, or_

from src.config.extensions import db
from src.models.safe_sedar import SAFEReport, SAFEReportStock, SAFEReportSection, SAFESEDARScrapeLog

logger = logging.getLogger(__name__)

bp = Blueprint('safe_reports', __name__, url_prefix='/api/safe-reports')


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
def get_safe_reports():
    """
    Get all SAFE reports with optional filters

    Query params:
    - fmp: Filter by FMP
    - year: Filter by report year
    - current_only: Boolean (default False)
    """
    try:
        query = SAFEReport.query

        # Filters
        fmp = request.args.get('fmp')
        if fmp:
            query = query.filter(SAFEReport.fmp == fmp)

        year = request.args.get('year')
        if year:
            query = query.filter(SAFEReport.report_year == int(year))

        current_only = request.args.get('current_only', 'false').lower() == 'true'
        if current_only:
            query = query.filter(SAFEReport.is_current == True)

        # Order by year desc
        query = query.order_by(desc(SAFEReport.report_year))

        reports = query.all()

        return jsonify({
            'success': True,
            'reports': [r.to_dict() for r in reports],
            'count': len(reports)
        })

    except Exception as e:
        logger.error(f"Error getting SAFE reports: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:report_id>', methods=['GET'])
def get_safe_report(report_id):
    """Get specific SAFE report with all stock data"""
    try:
        report = SAFEReport.query.get(report_id)

        if not report:
            return jsonify({'success': False, 'error': 'Report not found'}), 404

        # Get stocks
        stocks = SAFEReportStock.query.filter_by(safe_report_id=report_id).all()

        return jsonify({
            'success': True,
            'report': report.to_dict(),
            'stocks': [s.to_dict() for s in stocks]
        })

    except Exception as e:
        logger.error(f"Error getting SAFE report {report_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:report_id>/stocks', methods=['GET'])
def get_safe_report_stocks(report_id):
    """Get all stock data from a specific SAFE report"""
    try:
        stocks = SAFEReportStock.query.filter_by(safe_report_id=report_id).all()

        return jsonify({
            'success': True,
            'reportId': report_id,
            'stocks': [s.to_dict() for s in stocks],
            'count': len(stocks)
        })

    except Exception as e:
        logger.error(f"Error getting stocks for report {report_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/stocks/<species_name>', methods=['GET'])
def get_stock_history(species_name):
    """Get historical SAFE data for a species across multiple years"""
    try:
        stocks = db.session.query(SAFEReportStock, SAFEReport).join(
            SAFEReport, SAFEReportStock.safe_report_id == SAFEReport.id
        ).filter(
            SAFEReportStock.species_name.ilike(f'%{species_name}%')
        ).order_by(desc(SAFEReport.report_year)).all()

        results = []
        for stock, report in stocks:
            stock_dict = stock.to_dict()
            stock_dict['report_year'] = report.report_year
            stock_dict['fmp'] = report.fmp
            results.append(stock_dict)

        return jsonify({
            'success': True,
            'species': species_name,
            'history': results,
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"Error getting stock history for {species_name}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/acl-compliance', methods=['GET'])
def get_acl_compliance():
    """Get ACL compliance summary across all current SAFE reports"""
    try:
        from sqlalchemy import func

        # Get current reports
        current_reports = SAFEReport.query.filter_by(is_current=True).all()
        report_ids = [r.id for r in current_reports]

        # Get all stocks from current reports
        stocks = SAFEReportStock.query.filter(
            SAFEReportStock.safe_report_id.in_(report_ids)
        ).all()

        # Calculate summary stats
        total_stocks = len(stocks)
        acl_exceeded = sum(1 for s in stocks if s.acl_exceeded)
        overfished = sum(1 for s in stocks if s.stock_status == 'Overfished')
        overfishing = sum(1 for s in stocks if 'Occurring' in (s.overfishing_status or ''))

        # By FMP
        by_fmp = {}
        for stock in stocks:
            report = next((r for r in current_reports if r.id == stock.safe_report_id), None)
            if report:
                if report.fmp not in by_fmp:
                    by_fmp[report.fmp] = {
                        'total': 0,
                        'acl_exceeded': 0,
                        'overfished': 0,
                        'overfishing': 0
                    }

                by_fmp[report.fmp]['total'] += 1
                if stock.acl_exceeded:
                    by_fmp[report.fmp]['acl_exceeded'] += 1
                if stock.stock_status == 'Overfished':
                    by_fmp[report.fmp]['overfished'] += 1
                if 'Occurring' in (stock.overfishing_status or ''):
                    by_fmp[report.fmp]['overfishing'] += 1

        return jsonify({
            'success': True,
            'summary': {
                'totalStocks': total_stocks,
                'aclExceeded': acl_exceeded,
                'overfished': overfished,
                'overfishing': overfishing
            },
            'byFmp': by_fmp
        })

    except Exception as e:
        logger.error(f"Error getting ACL compliance: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/scrape', methods=['POST'])
def trigger_safe_scrape():
    """
    Trigger SAFE reports scraping

    Body params:
    - fmp: Optional specific FMP to scrape
    """
    try:
        data = request.get_json() or {}
        fmp = data.get('fmp')

        logger.info(f"Starting SAFE reports scrape (FMP: {fmp or 'all'})...")

        # Lazy import to avoid loading heavy dependencies at module level
        from src.services.safe_import_service import SAFEImportService

        service = SAFEImportService()

        if fmp:
            result = service.import_single_fmp_report(fmp)
        else:
            result = service.import_all_safe_reports()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error triggering SAFE scrape: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
def get_safe_stats():
    """Get summary statistics for SAFE reports"""
    try:
        from sqlalchemy import func

        # Total reports
        total_reports = SAFEReport.query.count()
        current_reports = SAFEReport.query.filter_by(is_current=True).count()

        # Reports by FMP
        fmp_counts = db.session.query(
            SAFEReport.fmp,
            func.count(SAFEReport.id).label('count')
        ).group_by(SAFEReport.fmp).all()

        # Total stocks tracked
        total_stocks = SAFEReportStock.query.count()

        # Current report IDs
        current_report_ids = [r.id for r in SAFEReport.query.filter_by(is_current=True).all()]

        # Stocks needing attention
        overfished_count = SAFEReportStock.query.filter(
            SAFEReportStock.safe_report_id.in_(current_report_ids),
            SAFEReportStock.stock_status == 'Overfished'
        ).count()

        acl_exceeded_count = SAFEReportStock.query.filter(
            SAFEReportStock.safe_report_id.in_(current_report_ids),
            SAFEReportStock.acl_exceeded == True
        ).count()

        return jsonify({
            'success': True,
            'stats': {
                'totalReports': total_reports,
                'currentReports': current_reports,
                'byFmp': {fmp: count for fmp, count in fmp_counts},
                'totalStocks': total_stocks,
                'overfished': overfished_count,
                'aclExceeded': acl_exceeded_count
            }
        })

    except Exception as e:
        logger.error(f"Error getting SAFE stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/scrape-logs', methods=['GET'])
def get_scrape_logs():
    """Get SAFE scraping history"""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)

        logs = SAFESEDARScrapeLog.query.filter(
            SAFESEDARScrapeLog.scrape_type == 'safe_reports'
        ).order_by(desc(SAFESEDARScrapeLog.started_at)).limit(limit).all()

        return jsonify({
            'success': True,
            'logs': [log.to_dict() for log in logs]
        })

    except Exception as e:
        logger.error(f"Error getting scrape logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
