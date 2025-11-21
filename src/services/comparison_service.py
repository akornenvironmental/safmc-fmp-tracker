"""
Amendment Comparison Service
Provides functionality to compare actions/amendments side-by-side
"""

import logging
from typing import Dict, List, Optional
from collections import defaultdict
from rapidfuzz import fuzz
from sqlalchemy import or_

from src.config.extensions import db
from src.models.action import Action

logger = logging.getLogger(__name__)


class ComparisonService:
    """Service for comparing amendments and finding similar actions"""

    @staticmethod
    def compare_actions(action_ids: List[str]) -> Dict:
        """
        Compare multiple actions side-by-side

        Args:
            action_ids: List of action IDs to compare

        Returns:
            Comparison data with differences highlighted
        """
        if len(action_ids) < 2:
            return {'error': 'Need at least 2 actions to compare'}

        # Fetch actions
        actions = Action.query.filter(Action.action_id.in_(action_ids)).all()

        if len(actions) < 2:
            return {'error': 'One or more actions not found'}

        # Build comparison matrix
        comparison = {
            'actions': [a.to_dict() for a in actions],
            'fields': {},
            'differences': [],
            'similarities': []
        }

        # Fields to compare
        compare_fields = [
            ('fmp', 'FMP'),
            ('type', 'Type'),
            ('status', 'Status'),
            ('progress_stage', 'Progress Stage'),
            ('progress_percentage', 'Progress'),
            ('phase', 'Phase'),
            ('lead_staff', 'Lead Staff'),
            ('committee', 'Committee'),
            ('start_date', 'Start Date'),
            ('target_date', 'Target Date'),
        ]

        for field_key, field_label in compare_fields:
            values = []
            for action in actions:
                val = getattr(action, field_key)
                if hasattr(val, 'isoformat'):
                    val = val.isoformat()
                values.append(val)

            # Check if all values are the same
            unique_values = set(str(v) if v else 'N/A' for v in values)
            is_different = len(unique_values) > 1

            comparison['fields'][field_key] = {
                'label': field_label,
                'values': values,
                'isDifferent': is_different
            }

            if is_different:
                comparison['differences'].append(field_label)
            else:
                comparison['similarities'].append(field_label)

        # Compare descriptions using text similarity
        if len(actions) == 2 and actions[0].description and actions[1].description:
            similarity = fuzz.ratio(
                actions[0].description or '',
                actions[1].description or ''
            )
            comparison['descriptionSimilarity'] = similarity

        return comparison

    @staticmethod
    def find_similar_actions(action_id: str, limit: int = 10) -> List[Dict]:
        """
        Find actions similar to a given action

        Args:
            action_id: ID of the action to find similar ones for
            limit: Maximum number of results

        Returns:
            List of similar actions with similarity scores
        """
        # Get the source action
        source = Action.query.filter_by(action_id=action_id).first()
        if not source:
            return []

        # Get all other actions
        other_actions = Action.query.filter(
            Action.action_id != action_id
        ).all()

        # Calculate similarity scores
        similar = []
        for action in other_actions:
            score = ComparisonService._calculate_similarity(source, action)
            if score > 30:  # Minimum threshold
                similar.append({
                    'action': action.to_dict(),
                    'similarityScore': score,
                    'matchReasons': ComparisonService._get_match_reasons(source, action)
                })

        # Sort by similarity score
        similar.sort(key=lambda x: x['similarityScore'], reverse=True)

        return similar[:limit]

    @staticmethod
    def _calculate_similarity(action1: Action, action2: Action) -> float:
        """Calculate similarity score between two actions"""
        score = 0.0
        weights = {
            'fmp': 25,
            'type': 20,
            'title': 35,
            'description': 20
        }

        # FMP match
        if action1.fmp and action2.fmp and action1.fmp == action2.fmp:
            score += weights['fmp']

        # Type match
        if action1.type and action2.type and action1.type == action2.type:
            score += weights['type']

        # Title similarity
        if action1.title and action2.title:
            title_sim = fuzz.ratio(action1.title, action2.title)
            score += (title_sim / 100) * weights['title']

        # Description similarity
        if action1.description and action2.description:
            desc_sim = fuzz.ratio(action1.description[:500], action2.description[:500])
            score += (desc_sim / 100) * weights['description']

        return round(score, 1)

    @staticmethod
    def _get_match_reasons(action1: Action, action2: Action) -> List[str]:
        """Get reasons why two actions are similar"""
        reasons = []

        if action1.fmp and action2.fmp and action1.fmp == action2.fmp:
            reasons.append(f"Same FMP: {action1.fmp}")

        if action1.type and action2.type and action1.type == action2.type:
            reasons.append(f"Same type: {action1.type}")

        if action1.title and action2.title:
            title_sim = fuzz.ratio(action1.title, action2.title)
            if title_sim > 50:
                reasons.append(f"Similar title ({title_sim}%)")

        return reasons

    @staticmethod
    def get_action_versions(base_title: str) -> List[Dict]:
        """
        Find all versions/amendments of a similar action

        For example, find all "Snapper Grouper Amendment" versions
        """
        # Extract base pattern (e.g., "Snapper Grouper Amendment")
        actions = Action.query.filter(
            Action.title.ilike(f'%{base_title}%')
        ).order_by(Action.start_date.desc()).all()

        return [a.to_dict() for a in actions]

    @staticmethod
    def get_fmp_amendment_history(fmp: str) -> Dict:
        """
        Get complete amendment history for an FMP

        Returns chronologically ordered list of all amendments
        with key changes tracked
        """
        actions = Action.query.filter(
            Action.fmp == fmp
        ).order_by(Action.start_date.asc()).all()

        if not actions:
            return {'fmp': fmp, 'amendments': [], 'timeline': []}

        # Group by type
        by_type = defaultdict(list)
        for action in actions:
            by_type[action.type or 'Other'].append(action.to_dict())

        # Build timeline
        timeline = []
        for action in actions:
            if action.start_date:
                timeline.append({
                    'date': action.start_date.isoformat(),
                    'action_id': action.action_id,
                    'title': action.title,
                    'type': action.type,
                    'status': action.status
                })

        return {
            'fmp': fmp,
            'totalActions': len(actions),
            'byType': dict(by_type),
            'timeline': sorted(timeline, key=lambda x: x['date']) if timeline else [],
            'amendments': [a.to_dict() for a in actions]
        }

    @staticmethod
    def get_species_regulation_history(species_name: str) -> Dict:
        """
        Get all regulatory actions affecting a specific species
        """
        actions = Action.query.filter(
            or_(
                Action.title.ilike(f'%{species_name}%'),
                Action.description.ilike(f'%{species_name}%')
            )
        ).order_by(Action.start_date.desc()).all()

        return {
            'species': species_name,
            'totalActions': len(actions),
            'actions': [a.to_dict() for a in actions]
        }
