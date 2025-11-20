"""
Workplan Service
Handles importing workplan data into the database with versioning
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from src.config.extensions import db
from src.models.workplan import (
    WorkplanVersion,
    WorkplanItem,
    WorkplanMilestone,
    WorkplanUploadLog
)
from src.models.action import Action
from src.scrapers.workplan_parser import parse_workplan_file

logger = logging.getLogger(__name__)


class WorkplanService:
    """Service for managing workplan data"""

    @staticmethod
    def import_workplan_file(
        file_path: str,
        version_name: str,
        upload_type: str = 'manual_upload',
        user_id: Optional[int] = None,
        council_meeting_id: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> Dict:
        """
        Import a workplan Excel file into the database

        Args:
            file_path: Path to the Excel file
            version_name: Name for this version (e.g., "Q3 2025", "September 2025 Meeting")
            upload_type: 'manual_upload' or 'auto_scraped'
            user_id: ID of user who uploaded (for manual uploads)
            council_meeting_id: Optional link to council meeting
            source_url: URL where file was downloaded from

        Returns:
            {
                'success': bool,
                'version_id': int,
                'items_created': int,
                'items_updated': int,
                'milestones_created': int,
                'errors': []
            }
        """
        start_time = datetime.utcnow()

        try:
            # Parse the Excel file
            logger.info(f"Parsing workplan file: {file_path}")
            parse_result = parse_workplan_file(file_path)

            if parse_result['errors']:
                return {
                    'success': False,
                    'errors': parse_result['errors']
                }

            metadata = parse_result['metadata']
            amendments = parse_result['amendments']

            # Deactivate previous active versions
            WorkplanVersion.query.filter_by(is_active=True).update({'is_active': False})

            # Create new workplan version
            version = WorkplanVersion(
                version_name=version_name,
                council_meeting_id=council_meeting_id,
                source_url=source_url,
                source_file_name=metadata.get('file_name'),
                upload_type=upload_type,
                uploaded_by_user_id=user_id,
                quarter=metadata.get('quarter'),
                fiscal_year=metadata.get('fiscal_year'),
                effective_date=datetime.utcnow().date(),
                is_active=True
            )

            db.session.add(version)
            db.session.flush()  # Get the ID

            logger.info(f"Created workplan version: {version.id} - {version_name}")

            # Import amendments and milestones
            items_created = 0
            items_updated = 0
            milestones_created = 0

            for amend_data in amendments:
                # Try to match to existing action
                action_id = WorkplanService._match_action(amend_data)

                # Create workplan item
                item = WorkplanItem(
                    workplan_version_id=version.id,
                    amendment_id=amend_data['amendment_id'],
                    action_id=action_id,
                    topic=amend_data['topic'],
                    status=amend_data['status'],
                    lead_staff=amend_data.get('lead_staff'),
                    sero_priority=amend_data.get('sero_priority')
                )

                db.session.add(item)
                db.session.flush()  # Get the ID
                items_created += 1

                # Create milestones
                for milestone_data in amend_data.get('milestones', []):
                    milestone = WorkplanMilestone(
                        workplan_item_id=item.id,
                        milestone_type=milestone_data['type'],
                        scheduled_date=milestone_data['scheduled_date'],
                        scheduled_meeting=milestone_data['scheduled_meeting']
                    )
                    db.session.add(milestone)
                    milestones_created += 1

                # Update the linked action with current workplan info
                if action_id:
                    action = Action.query.filter_by(action_id=action_id).first()
                    if action:
                        action.current_workplan_status = amend_data['status']
                        action.lead_staff = amend_data.get('lead_staff')
                        action.sero_priority = amend_data.get('sero_priority')

                        # Find next milestone
                        next_milestone = min(
                            amend_data.get('milestones', []),
                            key=lambda m: m['scheduled_date'],
                            default=None
                        )
                        if next_milestone:
                            action.next_milestone_type = next_milestone['type']
                            action.next_milestone_date = next_milestone['scheduled_date']

            db.session.commit()

            # Log the upload
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            upload_log = WorkplanUploadLog(
                workplan_version_id=version.id,
                upload_type=upload_type,
                file_name=metadata.get('file_name'),
                uploaded_by_user_id=user_id,
                status='success',
                items_found=len(amendments),
                items_created=items_created,
                items_updated=items_updated,
                milestones_created=milestones_created,
                processing_duration_ms=duration_ms
            )
            db.session.add(upload_log)
            db.session.commit()

            logger.info(f"Workplan import complete: {items_created} items, {milestones_created} milestones")

            return {
                'success': True,
                'version_id': version.id,
                'version_name': version_name,
                'items_created': items_created,
                'items_updated': items_updated,
                'milestones_created': milestones_created,
                'errors': []
            }

        except Exception as e:
            logger.error(f"Error importing workplan: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

            # Log the failed upload
            try:
                upload_log = WorkplanUploadLog(
                    upload_type=upload_type,
                    file_name=file_path.split('/')[-1],
                    status='error',
                    error_message=str(e)
                )
                db.session.add(upload_log)
                db.session.commit()
            except:
                pass

            return {
                'success': False,
                'errors': [str(e)]
            }

    @staticmethod
    def _match_action(amend_data: Dict) -> Optional[str]:
        """
        Try to match an amendment to an existing action

        Matching strategies:
        1. Exact amendment_id match
        2. Fuzzy title match
        3. Create new action if no match
        """
        from rapidfuzz import fuzz

        amendment_id = amend_data['amendment_id']
        topic = amend_data['topic']

        # Try exact ID match first
        action = Action.query.filter(
            db.func.lower(Action.action_id) == amendment_id.lower()
        ).first()

        if action:
            logger.debug(f"Exact match: {amendment_id} -> {action.action_id}")
            return action.action_id

        # Try fuzzy title match
        candidates = Action.query.limit(200).all()
        best_match = None
        best_score = 0

        for candidate in candidates:
            if not candidate.title:
                continue

            # Compare topic with action title
            score = fuzz.ratio(topic.lower(), candidate.title.lower())

            if score > best_score and score >= 70:  # 70% threshold
                best_score = score
                best_match = candidate

        if best_match:
            logger.debug(f"Fuzzy match: {amendment_id} -> {best_match.action_id} (score: {best_score})")
            return best_match.action_id

        # No match found - create new action
        logger.info(f"No match found for {amendment_id}, creating new action")

        # Generate action_id from amendment_id
        action_id = amendment_id.lower().replace(' ', '-').strip()

        new_action = Action(
            action_id=action_id,
            title=topic,
            type='Amendment',
            status=amend_data['status'],
            start_date=datetime.utcnow()
        )

        db.session.add(new_action)
        db.session.flush()

        return new_action.action_id

    @staticmethod
    def get_current_workplan() -> Dict:
        """Get the current active workplan with all items and milestones"""
        version = WorkplanVersion.query.filter_by(is_active=True).first()

        if not version:
            return {
                'version': None,
                'items': []
            }

        items = WorkplanItem.query.filter_by(workplan_version_id=version.id).all()

        return {
            'version': version.to_dict(),
            'items': [item.to_dict(include_milestones=True) for item in items]
        }

    @staticmethod
    def get_workplan_history(amendment_id: str) -> List[Dict]:
        """Get version history for a specific amendment"""
        items = db.session.query(WorkplanItem, WorkplanVersion).\
            join(WorkplanVersion).\
            filter(WorkplanItem.amendment_id == amendment_id).\
            order_by(WorkplanVersion.effective_date.desc()).\
            all()

        history = []
        for item, version in items:
            history.append({
                'version': version.to_dict(),
                'item': item.to_dict(include_milestones=True)
            })

        return history

    @staticmethod
    def link_milestone_to_meeting(milestone_id: int, meeting_id: str) -> bool:
        """Link a workplan milestone to an actual meeting"""
        milestone = WorkplanMilestone.query.get(milestone_id)
        if not milestone:
            return False

        milestone.meeting_id = meeting_id
        db.session.commit()

        return True

    @staticmethod
    def mark_milestone_completed(milestone_id: int) -> bool:
        """Mark a milestone as completed"""
        milestone = WorkplanMilestone.query.get(milestone_id)
        if not milestone:
            return False

        milestone.is_completed = True
        milestone.completed_date = datetime.utcnow().date()
        db.session.commit()

        return True
