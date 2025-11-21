"""
Species Service
Extracts and manages species information from actions and other data sources
"""

import logging
import re
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime
from sqlalchemy import or_

from src.config.extensions import db
from src.models.action import Action

logger = logging.getLogger(__name__)


class SpeciesService:
    """Service for managing species data and profiles"""

    # Common fish species names found in SAFMC actions
    KNOWN_SPECIES = {
        # Snappers
        'Red Snapper', 'Vermilion Snapper', 'Yellowtail Snapper', 'Mutton Snapper',
        'Lane Snapper', 'Cubera Snapper', 'Gray Snapper', 'Mahogany Snapper',
        'Dog Snapper', 'Schoolmaster Snapper', 'Silk Snapper', 'Blackfin Snapper',

        # Groupers
        'Gag Grouper', 'Red Grouper', 'Black Grouper', 'Scamp', 'Yellowfin Grouper',
        'Yellowmouth Grouper', 'Graysby', 'Coney', 'Red Hind', 'Rock Hind',
        'Speckled Hind', 'Warsaw Grouper', 'Snowy Grouper', 'Yellowedge Grouper',
        'Misty Grouper', 'Nassau Grouper', 'Goliath Grouper',

        # Jacks
        'Greater Amberjack', 'Lesser Amberjack', 'Almaco Jack', 'Banded Rudderfish',
        'Bar Jack', 'Blue Runner', 'Crevalle Jack', 'Florida Pompano', 'Permit',
        'Rainbow Runner', 'Yellow Jack',

        # Triggerfish
        'Gray Triggerfish', 'Queen Triggerfish', 'Ocean Triggerfish',

        # Tilefish
        'Blueline Tilefish', 'Golden Tilefish', 'Goldface Tilefish', 'Anchor Tilefish',
        'Blackline Tilefish', 'Sand Tilefish',

        # Wrasses
        'Hogfish', 'Puddingwife', 'Spanish Hogfish',

        # Grunts
        'White Grunt', 'Margate', 'Porkfish', 'Sailors Choice', 'Tomtate',

        # Porgies
        'Jolthead Porgy', 'Knobbed Porgy', 'Red Porgy', 'Saucereye Porgy',
        'Scup', 'Sheepshead Porgy', 'Whitebone Porgy',

        # Other Species
        'Black Sea Bass', 'Gray Triggerfish', 'Red Drum', 'Spotted Seatrout',
        'Weakfish', 'Atlantic Spadefish', 'Tripletail',

        # Pelagics
        'King Mackerel', 'Spanish Mackerel', 'Cobia', 'Dolphin', 'Wahoo',
        'Sailfish', 'Blue Marlin', 'White Marlin',

        # Sharks
        'Atlantic Sharpnose Shark', 'Blacknose Shark', 'Blacktip Shark',
        'Bonnethead', 'Bull Shark', 'Finetooth Shark', 'Lemon Shark',
        'Nurse Shark', 'Scalloped Hammerhead', 'Sandbar Shark', 'Tiger Shark',

        # Invertebrates
        'Rock Shrimp', 'Pink Shrimp', 'White Shrimp', 'Brown Shrimp',
        'Spiny Lobster', 'Stone Crab', 'Golden Crab',

        # Corals
        'Octocoral', 'Deepwater Coral', 'Oculina',
    }

    # FMP mappings
    FMP_SPECIES_MAP = {
        'Snapper Grouper': ['Snapper', 'Grouper', 'Tilefish', 'Hogfish', 'Porgy', 'Bass', 'Grunt'],
        'Dolphin Wahoo': ['Dolphin', 'Wahoo'],
        'Shrimp': ['Shrimp'],
        'Spiny Lobster': ['Lobster'],
        'Golden Crab': ['Crab'],
        'Sargassum': ['Sargassum'],
        'Coral': ['Coral', 'Octocoral', 'Oculina'],
    }

    @staticmethod
    def extract_species_from_text(text: str) -> List[str]:
        """
        Extract species names from text using pattern matching

        Args:
            text: Text to search for species names

        Returns:
            List of species names found
        """
        if not text:
            return []

        found_species = set()
        text_lower = text.lower()

        for species in SpeciesService.KNOWN_SPECIES:
            # Check for exact species name (case-insensitive)
            if species.lower() in text_lower:
                found_species.add(species)

        return sorted(list(found_species))

    @staticmethod
    def get_all_species() -> List[Dict]:
        """
        Get all unique species mentioned across all actions

        Returns:
            List of species with counts and metadata
        """
        logger.info("Extracting all species from actions...")

        # Get all actions
        actions = Action.query.all()

        # Track species occurrences
        species_data = defaultdict(lambda: {
            'count': 0,
            'actions': [],
            'fmps': set(),
            'statuses': set(),
            'first_mention': None,
            'last_mention': None
        })

        for action in actions:
            # Extract species from title and description
            text = f"{action.title or ''} {action.description or ''}"
            species_list = SpeciesService.extract_species_from_text(text)

            for species in species_list:
                species_data[species]['count'] += 1
                species_data[species]['actions'].append({
                    'id': action.id,
                    'title': action.title,
                    'status': action.status,
                    'start_date': action.start_date.isoformat() if action.start_date else None
                })

                if action.fmp:
                    species_data[species]['fmps'].add(action.fmp)
                if action.status:
                    species_data[species]['statuses'].add(action.status)

                # Track dates
                if action.start_date:
                    if not species_data[species]['first_mention'] or action.start_date < species_data[species]['first_mention']:
                        species_data[species]['first_mention'] = action.start_date
                    if not species_data[species]['last_mention'] or action.start_date > species_data[species]['last_mention']:
                        species_data[species]['last_mention'] = action.start_date

        # Convert to list format
        result = []
        for species_name, data in species_data.items():
            result.append({
                'name': species_name,
                'actionCount': data['count'],
                'fmps': sorted(list(data['fmps'])),
                'statuses': sorted(list(data['statuses'])),
                'firstMention': data['first_mention'].isoformat() if data['first_mention'] else None,
                'lastMention': data['last_mention'].isoformat() if data['last_mention'] else None,
                'actions': sorted(data['actions'], key=lambda x: x['start_date'] or '', reverse=True)[:5]  # Most recent 5
            })

        # Sort by action count descending
        result.sort(key=lambda x: x['actionCount'], reverse=True)

        logger.info(f"Found {len(result)} species across {len(actions)} actions")
        return result

    @staticmethod
    def get_species_profile(species_name: str) -> Optional[Dict]:
        """
        Get detailed profile for a specific species

        Args:
            species_name: Name of the species

        Returns:
            Species profile with all related data
        """
        logger.info(f"Getting profile for species: {species_name}")

        # Find all actions mentioning this species
        actions = Action.query.filter(
            or_(
                Action.title.ilike(f'%{species_name}%'),
                Action.description.ilike(f'%{species_name}%')
            )
        ).order_by(Action.start_date.desc()).all()

        if not actions:
            return None

        # Build timeline
        timeline = []
        fmps = set()
        statuses = defaultdict(int)

        for action in actions:
            if action.fmp:
                fmps.add(action.fmp)
            if action.status:
                statuses[action.status] += 1

            timeline.append({
                'id': action.id,
                'title': action.title,
                'description': action.description,
                'status': action.status,
                'fmp': action.fmp,
                'type': action.type,
                'start_date': action.start_date.isoformat() if action.start_date else None,
                'target_date': action.target_date.isoformat() if action.target_date else None,
                'completion_date': action.completion_date.isoformat() if action.completion_date else None,
                'progress': action.progress_percentage,
                'source_url': action.source_url
            })

        return {
            'name': species_name,
            'actionCount': len(actions),
            'fmps': sorted(list(fmps)),
            'statusBreakdown': dict(statuses),
            'firstMention': timeline[-1]['start_date'] if timeline else None,
            'lastMention': timeline[0]['start_date'] if timeline else None,
            'timeline': timeline,
            'summary': SpeciesService._generate_species_summary(species_name, actions)
        }

    @staticmethod
    def _generate_species_summary(species_name: str, actions: List[Action]) -> str:
        """Generate a text summary for a species"""
        if not actions:
            return f"No management actions found for {species_name}."

        fmps = set(a.fmp for a in actions if a.fmp)
        statuses = [a.status for a in actions if a.status]

        fmp_text = f"managed under {', '.join(sorted(fmps))}" if fmps else "being managed"
        status_text = f"{len([s for s in statuses if 'Approved' in s])} approved, {len([s for s in statuses if 'Comment' in s])} in comment period"

        return f"{species_name} is {fmp_text} with {len(actions)} management actions tracked ({status_text})."

    @staticmethod
    def search_species(query: str) -> List[Dict]:
        """
        Search for species by name

        Args:
            query: Search query

        Returns:
            List of matching species
        """
        all_species = SpeciesService.get_all_species()

        if not query:
            return all_species

        query_lower = query.lower()
        return [
            sp for sp in all_species
            if query_lower in sp['name'].lower()
        ]


def main():
    """Test the species service"""
    from flask import Flask
    import os

    # Create minimal Flask app for testing
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://localhost/safmc_fmp_tracker'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from src.config.extensions import db
    db.init_app(app)

    with app.app_context():
        print("Testing Species Service...")
        print("=" * 60)

        # Test 1: Get all species
        print("\n1. Getting all species...")
        species_list = SpeciesService.get_all_species()
        print(f"   Found {len(species_list)} species")
        print(f"   Top 5 species:")
        for sp in species_list[:5]:
            print(f"     - {sp['name']}: {sp['actionCount']} actions")

        # Test 2: Get species profile
        if species_list:
            test_species = species_list[0]['name']
            print(f"\n2. Getting profile for {test_species}...")
            profile = SpeciesService.get_species_profile(test_species)
            if profile:
                print(f"   Actions: {profile['actionCount']}")
                print(f"   FMPs: {', '.join(profile['fmps'])}")
                print(f"   Summary: {profile['summary']}")


if __name__ == '__main__':
    main()
