"""
Resource Allocation API Routes
Handles data collection, analysis, and visualization for resource allocation across fishery management councils
"""

import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
from sqlalchemy import text, func
from src.config.extensions import db
from src.models.resource_allocation import (
    ResourceCouncil,
    ResourceRegionalOffice,
    ResourceScienceCenter,
    ResourceCouncilBudget,
    ResourceCouncilStaffing,
    ResourceROCapacity,
    ResourceSCCapacity,
    ResourceWorkloadMetric,
    ResourceDataSource,
    ResourceAnalysisDocument
)

logger = logging.getLogger(__name__)

bp = Blueprint('resource_allocation', __name__, url_prefix='/api/resource-allocation')


# =====================================================
# MIGRATION & SETUP
# =====================================================

@bp.route('/migrate', methods=['POST'])
def run_migration():
    """Run the resource allocation system migration"""
    try:
        logger.info("Running resource allocation migration...")

        migration_file = 'migrations/create_resource_allocation_system.sql'

        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        # Execute migration
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
        created_tables = []
        errors = []

        for statement in statements:
            if statement.startswith('--') or statement.startswith('/*') or not statement:
                continue

            try:
                db.session.execute(text(statement))
                db.session.commit()

                if 'CREATE TABLE' in statement:
                    table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip()
                    if 'IF NOT EXISTS' in statement:
                        table_name = table_name.replace('IF NOT EXISTS', '').strip()
                    created_tables.append(table_name)

            except Exception as e:
                if 'already exists' not in str(e).lower():
                    errors.append(str(e))
                    logger.warning(f"Migration statement error: {e}")

        # Verify tables
        result = db.session.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name LIKE 'resource_%'
            ORDER BY table_name
        """))

        tables = [row[0] for row in result]

        return jsonify({
            'success': True,
            'created_tables': created_tables,
            'existing_tables': tables,
            'errors': errors
        })

    except Exception as e:
        logger.error(f"Migration error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# COUNCILS
# =====================================================

@bp.route('/councils', methods=['GET'])
def get_councils():
    """Get all fishery management councils"""
    try:
        councils = ResourceCouncil.query.all()
        return jsonify({
            'success': True,
            'councils': [c.to_dict() for c in councils]
        })
    except Exception as e:
        logger.error(f"Error getting councils: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/councils/<code>', methods=['GET'])
def get_council_by_code(code):
    """Get a specific council by code"""
    try:
        council = ResourceCouncil.query.filter_by(code=code.upper()).first()
        if not council:
            return jsonify({'success': False, 'error': 'Council not found'}), 404

        return jsonify({
            'success': True,
            'council': council.to_dict()
        })
    except Exception as e:
        logger.error(f"Error getting council: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/councils/<code>', methods=['PUT'])
def update_council(code):
    """Update council information"""
    try:
        council = ResourceCouncil.query.filter_by(code=code.upper()).first()
        if not council:
            return jsonify({'success': False, 'error': 'Council not found'}), 404

        data = request.json

        # Update allowed fields
        if 'geographicScope' in data:
            council.geographic_scope = data['geographicScope']
        if 'eezSquareMiles' in data:
            council.eez_square_miles = data['eezSquareMiles']
        if 'websiteUrl' in data:
            council.website_url = data['websiteUrl']
        if 'notes' in data:
            council.notes = data['notes']

        council.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'council': council.to_dict()
        })
    except Exception as e:
        logger.error(f"Error updating council: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# COUNCIL BUDGETS
# =====================================================

@bp.route('/councils/<code>/budgets', methods=['GET'])
def get_council_budgets(code):
    """Get budget data for a specific council"""
    try:
        council = ResourceCouncil.query.filter_by(code=code.upper()).first()
        if not council:
            return jsonify({'success': False, 'error': 'Council not found'}), 404

        budgets = ResourceCouncilBudget.query.filter_by(council_id=council.id)\
            .order_by(ResourceCouncilBudget.fiscal_year.desc()).all()

        return jsonify({
            'success': True,
            'councilCode': code.upper(),
            'budgets': [b.to_dict() for b in budgets]
        })
    except Exception as e:
        logger.error(f"Error getting council budgets: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/councils/<code>/budgets', methods=['POST'])
def add_council_budget(code):
    """Add budget data for a council"""
    try:
        council = ResourceCouncil.query.filter_by(code=code.upper()).first()
        if not council:
            return jsonify({'success': False, 'error': 'Council not found'}), 404

        data = request.json

        budget = ResourceCouncilBudget(
            council_id=council.id,
            fiscal_year=data['fiscalYear'],
            budget_period=data.get('budgetPeriod'),
            operating_budget=data.get('operatingBudget'),
            programmatic_funding=data.get('programmaticFunding'),
            total_budget=data.get('totalBudget'),
            inflation_adjusted_total=data.get('inflationAdjustedTotal'),
            base_year=data.get('baseYear'),
            source_document=data.get('sourceDocument'),
            source_page=data.get('sourcePage'),
            data_quality=data.get('dataQuality', 'Entered'),
            notes=data.get('notes'),
            entered_by_user_id=data.get('enteredByUserId')
        )

        db.session.add(budget)
        db.session.commit()

        return jsonify({
            'success': True,
            'budget': budget.to_dict()
        })
    except Exception as e:
        logger.error(f"Error adding council budget: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/budgets/<int:budget_id>', methods=['PUT'])
def update_council_budget(budget_id):
    """Update budget data"""
    try:
        budget = ResourceCouncilBudget.query.get(budget_id)
        if not budget:
            return jsonify({'success': False, 'error': 'Budget not found'}), 404

        data = request.json

        # Update fields
        for field in ['operatingBudget', 'programmaticFunding', 'totalBudget',
                      'inflationAdjustedTotal', 'baseYear', 'sourceDocument',
                      'sourcePage', 'dataQuality', 'notes']:
            if field in data:
                snake_field = ''.join(['_' + c.lower() if c.isupper() else c for c in field]).lstrip('_')
                setattr(budget, snake_field, data[field])

        budget.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'budget': budget.to_dict()
        })
    except Exception as e:
        logger.error(f"Error updating budget: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# COUNCIL STAFFING
# =====================================================

@bp.route('/councils/<code>/staffing', methods=['GET'])
def get_council_staffing(code):
    """Get staffing data for a specific council"""
    try:
        council = ResourceCouncil.query.filter_by(code=code.upper()).first()
        if not council:
            return jsonify({'success': False, 'error': 'Council not found'}), 404

        staffing = ResourceCouncilStaffing.query.filter_by(council_id=council.id)\
            .order_by(ResourceCouncilStaffing.fiscal_year.desc()).all()

        return jsonify({
            'success': True,
            'councilCode': code.upper(),
            'staffing': [s.to_dict() for s in staffing]
        })
    except Exception as e:
        logger.error(f"Error getting council staffing: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/councils/<code>/staffing', methods=['POST'])
def add_council_staffing(code):
    """Add staffing data for a council"""
    try:
        council = ResourceCouncil.query.filter_by(code=code.upper()).first()
        if not council:
            return jsonify({'success': False, 'error': 'Council not found'}), 404

        data = request.json

        staffing = ResourceCouncilStaffing(
            council_id=council.id,
            fiscal_year=data['fiscalYear'],
            as_of_date=datetime.strptime(data['asOfDate'], '%Y-%m-%d').date() if data.get('asOfDate') else None,
            total_fte=data.get('totalFte'),
            professional_staff=data.get('professionalStaff'),
            administrative_staff=data.get('administrativeStaff'),
            executive_staff=data.get('executiveStaff'),
            unfilled_positions=data.get('unfilledPositions'),
            source_document=data.get('sourceDocument'),
            data_quality=data.get('dataQuality', 'Entered'),
            notes=data.get('notes'),
            entered_by_user_id=data.get('enteredByUserId')
        )

        db.session.add(staffing)
        db.session.commit()

        return jsonify({
            'success': True,
            'staffing': staffing.to_dict()
        })
    except Exception as e:
        logger.error(f"Error adding council staffing: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# COMPARATIVE ANALYSIS
# =====================================================

@bp.route('/analysis/budget-comparison', methods=['GET'])
def get_budget_comparison():
    """Get budget comparison across all councils for a specific fiscal year"""
    try:
        fiscal_year = request.args.get('fiscalYear', type=int)

        if not fiscal_year:
            # Get most recent year with data
            result = db.session.query(func.max(ResourceCouncilBudget.fiscal_year)).scalar()
            fiscal_year = result if result else 2024

        # Get all councils with budget data for the specified year
        councils = db.session.query(ResourceCouncil, ResourceCouncilBudget)\
            .join(ResourceCouncilBudget, ResourceCouncil.id == ResourceCouncilBudget.council_id)\
            .filter(ResourceCouncilBudget.fiscal_year == fiscal_year)\
            .all()

        comparison_data = []
        for council, budget in councils:
            comparison_data.append({
                'councilCode': council.code,
                'councilName': council.name,
                'fiscalYear': fiscal_year,
                'totalBudget': float(budget.total_budget) if budget.total_budget else None,
                'operatingBudget': float(budget.operating_budget) if budget.operating_budget else None,
                'inflationAdjustedTotal': float(budget.inflation_adjusted_total) if budget.inflation_adjusted_total else None
            })

        return jsonify({
            'success': True,
            'fiscalYear': fiscal_year,
            'comparison': comparison_data
        })
    except Exception as e:
        logger.error(f"Error getting budget comparison: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/analysis/efficiency-metrics', methods=['GET'])
def get_efficiency_metrics():
    """Get efficiency metrics from the view"""
    try:
        fiscal_year = request.args.get('fiscalYear', type=int)

        query = text("""
            SELECT *
            FROM v_resource_efficiency_metrics
            WHERE fiscal_year = :fiscal_year
            ORDER BY council_code
        """)

        result = db.session.execute(query, {'fiscal_year': fiscal_year})

        metrics = []
        for row in result:
            metrics.append({
                'councilCode': row.council_code,
                'councilName': row.council_name,
                'fiscalYear': row.fiscal_year,
                'totalBudget': float(row.total_budget) if row.total_budget else None,
                'inflationAdjustedTotal': float(row.inflation_adjusted_total) if row.inflation_adjusted_total else None,
                'staffFte': float(row.staff_fte) if row.staff_fte else None,
                'managedSpecies': row.managed_species,
                'activeFmps': row.active_fmps,
                'amendmentsInDevelopment': row.amendments_in_development,
                'budgetPerSpecies': float(row.budget_per_species) if row.budget_per_species else None,
                'ftePerSpecies': float(row.fte_per_species) if row.fte_per_species else None,
                'budgetPerFte': float(row.budget_per_fte) if row.budget_per_fte else None,
                'budgetPerSqMile': float(row.budget_per_sq_mile) if row.budget_per_sq_mile else None,
                'ftePerSqMile': float(row.fte_per_sq_mile) if row.fte_per_sq_mile else None
            })

        return jsonify({
            'success': True,
            'fiscalYear': fiscal_year,
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Error getting efficiency metrics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/analysis/regional-comparison', methods=['GET'])
def get_regional_comparison():
    """Get regional resource comparison from the view"""
    try:
        fiscal_year = request.args.get('fiscalYear', type=int)

        query = text("""
            SELECT *
            FROM v_regional_resource_comparison
            WHERE fiscal_year = :fiscal_year
            ORDER BY regional_office_code
        """)

        result = db.session.execute(query, {'fiscal_year': fiscal_year})

        comparison = []
        for row in result:
            comparison.append({
                'regionalOfficeCode': row.regional_office_code,
                'regionalOfficeName': row.regional_office_name,
                'scienceCenterCode': row.science_center_code,
                'scienceCenterName': row.science_center_name,
                'fiscalYear': row.fiscal_year,
                'councilsServedCount': row.councils_served_count,
                'councilsServed': row.councils_served,
                'roTotalFte': float(row.ro_total_fte) if row.ro_total_fte else None,
                'roBudget': float(row.ro_budget) if row.ro_budget else None,
                'scTotalFte': float(row.sc_total_fte) if row.sc_total_fte else None,
                'scBudget': float(row.sc_budget) if row.sc_budget else None,
                'roFtePerCouncil': float(row.ro_fte_per_council) if row.ro_fte_per_council else None,
                'scFtePerCouncil': float(row.sc_fte_per_council) if row.sc_fte_per_council else None
            })

        return jsonify({
            'success': True,
            'fiscalYear': fiscal_year,
            'comparison': comparison
        })
    except Exception as e:
        logger.error(f"Error getting regional comparison: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# DATA COLLECTION TRACKING
# =====================================================

@bp.route('/data-sources', methods=['GET'])
def get_data_sources():
    """Get all data sources with collection status"""
    try:
        sources = ResourceDataSource.query.order_by(
            ResourceDataSource.priority,
            ResourceDataSource.collection_status
        ).all()

        return jsonify({
            'success': True,
            'sources': [s.to_dict() for s in sources]
        })
    except Exception as e:
        logger.error(f"Error getting data sources: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/data-sources', methods=['POST'])
def add_data_source():
    """Add a new data source to track"""
    try:
        data = request.json

        source = ResourceDataSource(
            source_name=data['sourceName'],
            source_type=data.get('sourceType'),
            source_url=data.get('sourceUrl'),
            document_name=data.get('documentName'),
            fiscal_years=data.get('fiscalYears', []),
            councils_covered=data.get('councilsCovered', []),
            data_categories=data.get('dataCategories', []),
            collection_status=data.get('collectionStatus', 'Not Started'),
            priority=data.get('priority', 'Tier 2'),
            assigned_to_user_id=data.get('assignedToUserId'),
            percent_complete=data.get('percentComplete', 0),
            notes=data.get('notes')
        )

        db.session.add(source)
        db.session.commit()

        return jsonify({
            'success': True,
            'source': source.to_dict()
        })
    except Exception as e:
        logger.error(f"Error adding data source: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/data-sources/<int:source_id>', methods=['PUT'])
def update_data_source(source_id):
    """Update data source collection status"""
    try:
        source = ResourceDataSource.query.get(source_id)
        if not source:
            return jsonify({'success': False, 'error': 'Data source not found'}), 404

        data = request.json

        if 'collectionStatus' in data:
            source.collection_status = data['collectionStatus']
        if 'percentComplete' in data:
            source.percent_complete = data['percentComplete']
        if 'notes' in data:
            source.notes = data['notes']

        # Auto-set dates based on status
        if data.get('collectionStatus') == 'Completed' and not source.data_entered_date:
            source.data_entered_date = datetime.utcnow().date()

        source.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'source': source.to_dict()
        })
    except Exception as e:
        logger.error(f"Error updating data source: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# DOCUMENT REPOSITORY
# =====================================================

@bp.route('/documents', methods=['GET'])
def get_documents():
    """Get all analysis documents"""
    try:
        doc_type = request.args.get('type')

        query = ResourceAnalysisDocument.query.filter_by(is_current=True)

        if doc_type:
            query = query.filter_by(document_type=doc_type)

        documents = query.order_by(ResourceAnalysisDocument.created_at.desc()).all()

        return jsonify({
            'success': True,
            'documents': [d.to_dict() for d in documents]
        })
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/documents', methods=['POST'])
def add_document():
    """Add a new analysis document"""
    try:
        data = request.json

        document = ResourceAnalysisDocument(
            title=data['title'],
            document_type=data.get('documentType'),
            file_name=data.get('fileName'),
            file_path=data.get('filePath'),
            file_type=data.get('fileType'),
            file_size_bytes=data.get('fileSizeBytes'),
            description=data.get('description'),
            summary=data.get('summary'),
            tags=data.get('tags', []),
            fiscal_years=data.get('fiscalYears', []),
            version=data.get('version'),
            is_current=data.get('isCurrent', True),
            is_public=data.get('isPublic', False),
            uploaded_by_user_id=data.get('uploadedByUserId')
        )

        db.session.add(document)
        db.session.commit()

        return jsonify({
            'success': True,
            'document': document.to_dict()
        })
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# DASHBOARD SUMMARY
# =====================================================

@bp.route('/dashboard', methods=['GET'])
def get_dashboard_summary():
    """Get summary data for the resource allocation dashboard"""
    try:
        # Get councils count
        councils_count = ResourceCouncil.query.count()

        # Get data collection progress
        total_sources = ResourceDataSource.query.count()
        completed_sources = ResourceDataSource.query.filter_by(collection_status='Completed').count()

        avg_progress = db.session.query(func.avg(ResourceDataSource.percent_complete)).scalar()

        # Get latest fiscal year with data
        latest_budget_year = db.session.query(func.max(ResourceCouncilBudget.fiscal_year)).scalar()

        # Get document counts
        total_documents = ResourceAnalysisDocument.query.filter_by(is_current=True).count()

        return jsonify({
            'success': True,
            'summary': {
                'councilsCount': councils_count,
                'dataSourcesTotal': total_sources,
                'dataSourcesCompleted': completed_sources,
                'dataCollectionProgress': round(avg_progress, 1) if avg_progress else 0,
                'latestFiscalYear': latest_budget_year,
                'documentsCount': total_documents
            }
        })
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
