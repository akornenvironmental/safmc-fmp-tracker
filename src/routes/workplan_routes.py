"""
Workplan API Routes
"""

import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
from sqlalchemy import text

from src.config.extensions import db
from src.models.workplan import WorkplanVersion, WorkplanItem, WorkplanMilestone
from src.services.workplan_service import WorkplanService

logger = logging.getLogger(__name__)

bp = Blueprint('workplan', __name__, url_prefix='/api/workplan')


@bp.route('/migrate', methods=['POST'])
def run_migration():
    """Run the workplan system migration"""
    try:
        logger.info("Running workplan migration...")

        migration_file = 'migrations/create_workplan_system.sql'

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

        # Verify tables
        result = db.session.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND (table_name LIKE 'workplan%' OR table_name = 'milestone_types')
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


@bp.route('/current', methods=['GET'])
def get_current_workplan():
    """Get the current active workplan"""
    try:
        current = WorkplanService.get_current_workplan()

        return jsonify({
            'success': True,
            'version': current['version'],
            'items': current['items']
        })

    except Exception as e:
        logger.error(f"Error getting current workplan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/versions', methods=['GET'])
def get_workplan_versions():
    """Get all workplan versions"""
    try:
        versions = WorkplanVersion.query.order_by(WorkplanVersion.effective_date.desc()).all()

        return jsonify({
            'success': True,
            'versions': [v.to_dict() for v in versions]
        })

    except Exception as e:
        logger.error(f"Error getting workplan versions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/history/<amendment_id>', methods=['GET'])
def get_amendment_history(amendment_id):
    """Get version history for a specific amendment"""
    try:
        history = WorkplanService.get_workplan_history(amendment_id)

        return jsonify({
            'success': True,
            'amendmentId': amendment_id,
            'history': history
        })

    except Exception as e:
        logger.error(f"Error getting amendment history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/milestones/<int:milestone_id>/complete', methods=['POST'])
def mark_milestone_complete(milestone_id):
    """Mark a milestone as completed"""
    try:
        success = WorkplanService.mark_milestone_completed(milestone_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Milestone not found'}), 404

    except Exception as e:
        logger.error(f"Error marking milestone complete: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/milestones/<int:milestone_id>/link-meeting', methods=['POST'])
def link_milestone_to_meeting(milestone_id):
    """Link a milestone to a meeting"""
    try:
        data = request.get_json()
        meeting_id = data.get('meeting_id')

        if not meeting_id:
            return jsonify({'success': False, 'error': 'meeting_id required'}), 400

        success = WorkplanService.link_milestone_to_meeting(milestone_id, meeting_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Milestone not found'}), 404

    except Exception as e:
        logger.error(f"Error linking milestone to meeting: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Upload endpoint (for future implementation when we add file upload support)
@bp.route('/upload', methods=['POST'])
def upload_workplan():
    """Upload and import a workplan Excel file"""
    return jsonify({
        'success': False,
        'error': 'File upload not yet implemented. Use import_workplan.py script for now.'
    }), 501
