"""
Export API Routes
Provides data export functionality for actions, meetings, comments, and species
"""

import logging
import csv
import io
from datetime import datetime
from flask import Blueprint, jsonify, request, Response

from src.config.extensions import db
from src.models.action import Action
from src.models.meeting import Meeting
from src.models.comment import Comment
from src.utils.security import safe_error_response

logger = logging.getLogger(__name__)

bp = Blueprint('export', __name__, url_prefix='/api/export')


@bp.route('/actions', methods=['GET'])
def export_actions():
    """
    Export actions data

    Query params:
    - format: csv, tsv, json (default: json)
    - fmp: Filter by FMP
    - status: Filter by status
    """
    try:
        format_type = request.args.get('format', 'json')
        fmp = request.args.get('fmp')
        status = request.args.get('status')

        query = Action.query

        if fmp:
            query = query.filter(Action.fmp == fmp)
        if status:
            query = query.filter(Action.status == status)

        actions = query.order_by(Action.updated_at.desc()).all()

        if format_type == 'json':
            return jsonify({
                'success': True,
                'actions': [a.to_dict() for a in actions],
                'count': len(actions),
                'exported_at': datetime.utcnow().isoformat()
            })

        # CSV/TSV export
        output = io.StringIO()
        delimiter = '\t' if format_type == 'tsv' else ','
        writer = csv.writer(output, delimiter=delimiter)

        # Header
        headers = ['ID', 'Title', 'Type', 'FMP', 'Status', 'Stage', 'Progress',
                   'Start Date', 'Target Date', 'Lead Staff', 'Description', 'Source URL']
        writer.writerow(headers)

        # Data rows
        for action in actions:
            writer.writerow([
                action.action_id,
                action.title,
                action.type,
                action.fmp,
                action.status,
                action.progress_stage,
                action.progress_percentage,
                action.start_date.isoformat() if action.start_date else '',
                action.target_date.isoformat() if action.target_date else '',
                action.lead_staff,
                action.description,
                action.source_url
            ])

        output.seek(0)
        content_type = 'text/tab-separated-values' if format_type == 'tsv' else 'text/csv'
        filename = f'actions-export-{datetime.now().strftime("%Y%m%d")}.{format_type}'

        return Response(
            output.getvalue(),
            mimetype=content_type,
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        logger.error(f"Error exporting actions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/meetings', methods=['GET'])
def export_meetings():
    """
    Export meetings data

    Query params:
    - format: csv, tsv, json (default: json)
    - upcoming: Boolean - only future meetings
    """
    try:
        format_type = request.args.get('format', 'json')
        upcoming = request.args.get('upcoming', 'false').lower() == 'true'

        query = Meeting.query

        if upcoming:
            query = query.filter(Meeting.start_date >= datetime.now().date())

        meetings = query.order_by(Meeting.start_date.desc()).all()

        if format_type == 'json':
            return jsonify({
                'success': True,
                'meetings': [m.to_dict() for m in meetings],
                'count': len(meetings),
                'exported_at': datetime.utcnow().isoformat()
            })

        # CSV/TSV export
        output = io.StringIO()
        delimiter = '\t' if format_type == 'tsv' else ','
        writer = csv.writer(output, delimiter=delimiter)

        headers = ['ID', 'Title', 'Start Date', 'End Date', 'Location', 'Type', 'Source URL']
        writer.writerow(headers)

        for meeting in meetings:
            writer.writerow([
                meeting.meeting_id,
                meeting.title,
                meeting.start_date.isoformat() if meeting.start_date else '',
                meeting.end_date.isoformat() if meeting.end_date else '',
                meeting.location,
                meeting.meeting_type,
                meeting.source_url
            ])

        output.seek(0)
        content_type = 'text/tab-separated-values' if format_type == 'tsv' else 'text/csv'
        filename = f'meetings-export-{datetime.now().strftime("%Y%m%d")}.{format_type}'

        return Response(
            output.getvalue(),
            mimetype=content_type,
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        logger.error(f"Error exporting meetings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/comments', methods=['GET'])
def export_comments():
    """
    Export comments data

    Query params:
    - format: csv, tsv, json (default: json)
    - action_id: Filter by action
    """
    try:
        format_type = request.args.get('format', 'json')
        action_id = request.args.get('action_id')

        query = Comment.query

        if action_id:
            query = query.filter(Comment.action_id == action_id)

        comments = query.order_by(Comment.submitted_date.desc()).all()

        if format_type == 'json':
            return jsonify({
                'success': True,
                'comments': [c.to_dict() for c in comments],
                'count': len(comments),
                'exported_at': datetime.utcnow().isoformat()
            })

        # CSV/TSV export
        output = io.StringIO()
        delimiter = '\t' if format_type == 'tsv' else ','
        writer = csv.writer(output, delimiter=delimiter)

        headers = ['ID', 'Action ID', 'Commenter', 'Organization', 'Date', 'Comment Text', 'Source URL']
        writer.writerow(headers)

        for comment in comments:
            writer.writerow([
                comment.id,
                comment.action_id,
                comment.commenter_name,
                comment.organization,
                comment.submitted_date.isoformat() if comment.submitted_date else '',
                comment.comment_text[:500] if comment.comment_text else '',  # Truncate long comments
                comment.source_url
            ])

        output.seek(0)
        content_type = 'text/tab-separated-values' if format_type == 'tsv' else 'text/csv'
        filename = f'comments-export-{datetime.now().strftime("%Y%m%d")}.{format_type}'

        return Response(
            output.getvalue(),
            mimetype=content_type,
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        logger.error(f"Error exporting comments: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/species', methods=['GET'])
def export_species():
    """
    Export species data

    Query params:
    - format: csv, tsv, json (default: json)
    """
    try:
        format_type = request.args.get('format', 'json')

        from src.services.species_service import SpeciesService
        species_list = SpeciesService.get_all_species()

        if format_type == 'json':
            return jsonify({
                'success': True,
                'species': species_list,
                'count': len(species_list),
                'exported_at': datetime.utcnow().isoformat()
            })

        # CSV/TSV export
        output = io.StringIO()
        delimiter = '\t' if format_type == 'tsv' else ','
        writer = csv.writer(output, delimiter=delimiter)

        headers = ['Species', 'Action Count', 'FMPs', 'First Mention', 'Last Mention']
        writer.writerow(headers)

        for species in species_list:
            writer.writerow([
                species['name'],
                species['actionCount'],
                '; '.join(species.get('fmps', [])),
                species.get('firstMention', ''),
                species.get('lastMention', '')
            ])

        output.seek(0)
        content_type = 'text/tab-separated-values' if format_type == 'tsv' else 'text/csv'
        filename = f'species-export-{datetime.now().strftime("%Y%m%d")}.{format_type}'

        return Response(
            output.getvalue(),
            mimetype=content_type,
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        logger.error(f"Error exporting species: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/summary', methods=['GET'])
def export_summary():
    """
    Export a summary report of all data

    Query params:
    - format: json only for now
    """
    try:
        # Get counts
        action_count = Action.query.count()
        meeting_count = Meeting.query.count()
        comment_count = Comment.query.count()

        # Get FMP breakdown
        fmp_counts = db.session.query(
            Action.fmp,
            db.func.count(Action.id)
        ).group_by(Action.fmp).all()

        # Get status breakdown
        status_counts = db.session.query(
            Action.progress_stage,
            db.func.count(Action.id)
        ).group_by(Action.progress_stage).all()

        return jsonify({
            'success': True,
            'summary': {
                'generatedAt': datetime.utcnow().isoformat(),
                'totals': {
                    'actions': action_count,
                    'meetings': meeting_count,
                    'comments': comment_count
                },
                'actionsByFmp': {fmp: count for fmp, count in fmp_counts if fmp},
                'actionsByStage': {stage: count for stage, count in status_counts if stage}
            }
        })

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
