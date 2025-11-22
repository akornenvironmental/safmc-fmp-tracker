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


@bp.route('/version/<int:version_id>', methods=['GET'])
def get_workplan_by_version(version_id):
    """Get a specific workplan version by ID"""
    try:
        version = WorkplanVersion.query.get(version_id)

        if not version:
            return jsonify({'success': False, 'error': 'Version not found'}), 404

        items = WorkplanItem.query.filter_by(workplan_version_id=version.id).all()

        return jsonify({
            'success': True,
            'version': version.to_dict(),
            'items': [item.to_dict(include_milestones=True) for item in items]
        })

    except Exception as e:
        logger.error(f"Error getting workplan version: {e}")
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


@bp.route('/compare', methods=['GET'])
def compare_workplan_versions():
    """Compare two workplan versions to see changes"""
    try:
        version1_id = request.args.get('v1', type=int)
        version2_id = request.args.get('v2', type=int)

        # If no versions specified, compare current vs previous
        if not version1_id or not version2_id:
            versions = WorkplanVersion.query.order_by(
                WorkplanVersion.effective_date.desc()
            ).limit(2).all()

            if len(versions) < 2:
                return jsonify({
                    'success': False,
                    'error': 'Need at least 2 versions to compare'
                }), 400

            version1_id = versions[0].id  # newer
            version2_id = versions[1].id  # older

        # Get items from both versions
        v1 = WorkplanVersion.query.get(version1_id)
        v2 = WorkplanVersion.query.get(version2_id)

        if not v1 or not v2:
            return jsonify({'success': False, 'error': 'Version not found'}), 404

        items1 = {item.amendment_id: item for item in
                  WorkplanItem.query.filter_by(workplan_version_id=version1_id).all()}
        items2 = {item.amendment_id: item for item in
                  WorkplanItem.query.filter_by(workplan_version_id=version2_id).all()}

        # Find differences
        added = []      # In v1 but not v2 (new items)
        removed = []    # In v2 but not v1 (removed items)
        changed = []    # In both but with changes
        unchanged = []  # Same in both

        # Check items in newer version
        for amend_id, item1 in items1.items():
            if amend_id not in items2:
                added.append(item1.to_dict(include_milestones=True))
            else:
                item2 = items2[amend_id]
                changes = []

                if item1.status != item2.status:
                    changes.append({
                        'field': 'status',
                        'old': item2.status,
                        'new': item1.status
                    })

                if item1.lead_staff != item2.lead_staff:
                    changes.append({
                        'field': 'lead_staff',
                        'old': item2.lead_staff,
                        'new': item1.lead_staff
                    })

                if item1.sero_priority != item2.sero_priority:
                    changes.append({
                        'field': 'sero_priority',
                        'old': item2.sero_priority,
                        'new': item1.sero_priority
                    })

                # Compare milestones
                milestones1 = WorkplanMilestone.query.filter_by(
                    workplan_item_id=item1.id
                ).all()
                milestones2 = WorkplanMilestone.query.filter_by(
                    workplan_item_id=item2.id
                ).all()

                if len(milestones1) != len(milestones2):
                    changes.append({
                        'field': 'milestones_count',
                        'old': len(milestones2),
                        'new': len(milestones1)
                    })

                if changes:
                    changed.append({
                        'item': item1.to_dict(include_milestones=True),
                        'changes': changes
                    })
                else:
                    unchanged.append(item1.to_dict())

        # Check items removed in newer version
        for amend_id, item2 in items2.items():
            if amend_id not in items1:
                removed.append(item2.to_dict(include_milestones=True))

        return jsonify({
            'success': True,
            'comparison': {
                'version1': v1.to_dict(),
                'version2': v2.to_dict(),
                'summary': {
                    'added': len(added),
                    'removed': len(removed),
                    'changed': len(changed),
                    'unchanged': len(unchanged)
                },
                'added': added,
                'removed': removed,
                'changed': changed
            }
        })

    except Exception as e:
        logger.error(f"Error comparing workplan versions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
def get_workplan_stats():
    """Get workplan statistics"""
    try:
        # Get current active version
        version = WorkplanVersion.query.filter_by(is_active=True).first()

        if not version:
            return jsonify({'success': False, 'error': 'No active workplan'}), 404

        # Get items by status
        items = WorkplanItem.query.filter_by(workplan_version_id=version.id).all()

        by_status = {}
        by_lead = {}
        by_priority = {}

        for item in items:
            # By status
            status = item.status or 'UNKNOWN'
            by_status[status] = by_status.get(status, 0) + 1

            # By lead staff
            lead = item.lead_staff or 'Unassigned'
            by_lead[lead] = by_lead.get(lead, 0) + 1

            # By priority
            priority = item.sero_priority or 'Not Set'
            by_priority[priority] = by_priority.get(priority, 0) + 1

        # Get milestone stats
        milestone_count = WorkplanMilestone.query.join(WorkplanItem).filter(
            WorkplanItem.workplan_version_id == version.id
        ).count()

        completed_milestones = WorkplanMilestone.query.join(WorkplanItem).filter(
            WorkplanItem.workplan_version_id == version.id,
            WorkplanMilestone.is_completed == True
        ).count()

        return jsonify({
            'success': True,
            'version': version.to_dict(),
            'stats': {
                'total_items': len(items),
                'by_status': by_status,
                'by_lead': by_lead,
                'by_priority': by_priority,
                'total_milestones': milestone_count,
                'completed_milestones': completed_milestones
            }
        })

    except Exception as e:
        logger.error(f"Error getting workplan stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Upload endpoint (for future implementation when we add file upload support)
@bp.route('/upload', methods=['POST'])
def upload_workplan():
    """Upload and import a workplan Excel file"""
    return jsonify({
        'success': False,
        'error': 'File upload not yet implemented. Use import_workplan.py script for now.'
    }), 501
