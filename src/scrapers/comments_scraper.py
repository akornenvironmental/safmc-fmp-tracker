"""
SAFMC Public Comments Scraper
Scrapes public comment data from various sources including Google Sheets
"""

import re
import csv
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import requests
from io import StringIO
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class CommentsScraper:
    """Scraper for SAFMC public comments"""

    # Known comment sources (Google Sheets pubhtml URLs)
    COMMENT_SOURCES = [
        {
            'url': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSjyRSAei_lEHn4bmBpCxlkhq_s0RpBdzoUhzM490fgfYTJZbJMuFT6SFF8oeW34JzkkoY6pYOKBjT3/pubhtml?gid=246666200&single=true',
            'name': 'Public Comments - Comprehensive',
            'source_id': 'comments-main',  # For ID generation only, not for action_id FK
            'phase': 'Public Comment'
        },
        {
            'url': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSjyRSAei_lEHn4bmBpCxlkhq_s0RpBdzoUhzM490fgfYTJZbJMuFT6SFF8oeW34JzkkoY6pYOKBjT3/pubhtml?gid=440075844&single=true',
            'name': 'Public Comments - Additional 1',
            'source_id': 'comments-1',  # For ID generation only, not for action_id FK
            'phase': 'Public Comment'
        },
        {
            'url': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSjyRSAei_lEHn4bmBpCxlkhq_s0RpBdzoUhzM490fgfYTJZbJMuFT6SFF8oeW34JzkkoY6pYOKBjT3/pubhtml?gid=2112604420&single=true',
            'name': 'Public Comments - Additional 2',
            'source_id': 'comments-2',  # For ID generation only, not for action_id FK
            'phase': 'Public Comment'
        }
    ]

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SAFMC-FMP-Tracker/1.0'
        })

    def scrape_all_comments(self) -> Dict:
        """Scrape all configured comment sources"""
        results = {
            'comments': [],
            'total_found': 0,
            'by_source': {},
            'errors': []
        }

        logger.info(f"Starting to scrape {len(self.COMMENT_SOURCES)} comment sources")

        for source in self.COMMENT_SOURCES:
            try:
                logger.info(f"Scraping: {source['name']}")
                metadata, comments = self.scrape_comment_sheet(source)

                # Enhance each comment with metadata
                enhanced_comments = []
                for i, comment in enumerate(comments, 1):
                    enhanced = self._enhance_comment(comment, source, i, metadata)
                    enhanced_comments.append(enhanced)

                results['comments'].extend(enhanced_comments)
                results['by_source'][source['name']] = len(enhanced_comments)
                results['total_found'] += len(enhanced_comments)

                logger.info(f"  Found {len(enhanced_comments)} comments")

            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {e}")
                results['errors'].append({
                    'source': source['name'],
                    'error': str(e)
                })

        # Remove duplicates
        results['comments'] = self._remove_duplicates(results['comments'])
        logger.info(f"Total unique comments: {len(results['comments'])}")

        return results

    def scrape_comment_sheet(self, source: Dict) -> Tuple[Dict, List[Dict]]:
        """
        Scrape a single comment sheet from Google Sheets

        Returns:
            Tuple of (metadata_dict, comments_list)
            metadata_dict contains: {'title': str, 'description': str}
        """
        try:
            # Convert /pubhtml URL to /pub?output=csv for direct CSV access
            csv_url = source['url'].replace('/pubhtml?', '/pub?').replace('/pubhtml', '/pub?')
            if 'output=csv' not in csv_url:
                csv_url = csv_url.replace('&single=true', '&single=true&output=csv')
                if '&single=true&output=csv' not in csv_url:
                    csv_url += '&output=csv'

            logger.info(f"  Fetching CSV from: {csv_url}")

            response = self.session.get(csv_url, timeout=self.timeout)
            response.raise_for_status()

            # Parse CSV data
            csv_content = response.content.decode('utf-8')
            lines = csv_content.strip().split('\n')

            # Google Sheets exports include metadata rows before headers
            # Row 1: ID/metadata
            # Row 2: "Public Reporting"
            # Row 3: "Amendment"
            # Row 4: Amendment title
            # Row 5: Amendment description
            # Row 6: Headers
            if len(lines) < 7:
                logger.warning(f"CSV has fewer than 7 rows, may not have data: {csv_url}")
                return ({}, [])

            # Extract metadata from rows 4 and 5
            metadata = {}
            if len(lines) >= 4:
                # Row 4: Amendment title (first column only)
                title_row = lines[3].split(',')[0].strip('"')
                metadata['title'] = title_row if title_row else None

            if len(lines) >= 5:
                # Row 5: Amendment description (first column only)
                desc_row = lines[4].split(',')[0].strip('"')
                metadata['description'] = desc_row if desc_row else None

            logger.info(f"  Amendment: {metadata.get('title', 'Unknown')}")

            # Reconstruct CSV starting from the headers (row 6, index 5)
            csv_data_from_headers = '\n'.join(lines[5:])
            csv_reader = csv.DictReader(StringIO(csv_data_from_headers))

            # Get headers from CSV
            headers = csv_reader.fieldnames
            if not headers:
                logger.warning(f"No headers found in CSV from {csv_url}")
                return (metadata, [])

            logger.info(f"  Found headers: {headers}")

            # Read all rows and parse them
            comments = []
            for row in csv_reader:
                # Skip empty rows
                if not any(row.values()):
                    continue

                # Parse the row to normalize field names
                parsed_comment = self._parse_comment_row(row)
                if parsed_comment:
                    comments.append(parsed_comment)

            return (metadata, comments)

        except Exception as e:
            logger.error(f"Error scraping comment sheet: {e}")
            import traceback
            traceback.print_exc()
            return ({}, [])

    def _parse_comment_row(self, row: Dict) -> Optional[Dict]:
        """Parse a single comment row from CSV"""
        # Map common header variations
        def get_field(variations: List[str]) -> str:
            for var in variations:
                for key, value in row.items():
                    if var.lower() in key.lower():
                        return value or ''
            return ''

        # Get raw fields
        submitted_by = get_field(['name', 'commenter', 'submitted by'])
        location_raw = get_field(['location', 'city/state', 'city', 'address'])

        # Parse "Submitted By" field which may contain multi-line format:
        # First Name: X\nLast Name: Y\nEmail: Z
        name = ''
        email = get_field(['email', 'e-mail', 'contact'])

        if submitted_by and '\n' in submitted_by:
            # Parse multi-line format
            lines = submitted_by.split('\n')
            first_name = ''
            last_name = ''
            for line in lines:
                if 'first name:' in line.lower():
                    first_name = line.split(':', 1)[1].strip()
                elif 'last name:' in line.lower():
                    last_name = line.split(':', 1)[1].strip()
                elif 'email:' in line.lower() and not email:
                    email = line.split(':', 1)[1].strip()
            name = f"{first_name} {last_name}".strip()
        else:
            name = submitted_by

        # Parse "Location" field which may contain multi-line format:
        # City: X\nState: Y
        location = location_raw
        if location_raw and '\n' in location_raw:
            # Parse multi-line format
            lines = location_raw.split('\n')
            city_part = ''
            state_part = ''
            for line in lines:
                if 'city:' in line.lower():
                    city_part = line.split(':', 1)[1].strip()
                elif 'state:' in line.lower():
                    state_part = line.split(':', 1)[1].strip()
            if city_part and state_part:
                location = f"{city_part}, {state_part}"

        return {
            'date': get_field(['date', 'submit date', 'timestamp']),
            'name': name,
            'organization': get_field(['organization', 'org', 'affiliation']),
            'location': location,
            'email': email,
            'comment_text': get_field(['comment', 'comments', 'text', 'submission'])
        }

    def _enhance_comment(self, comment: Dict, source: Dict, sequence: int, metadata: Dict) -> Dict:
        """
        Enhance comment with analysis, categorization, and entity linking

        Uses fuzzy matching to find/create:
        - Action (from amendment metadata)
        - Contact (from commenter info)
        - Organization (from affiliation)
        """
        from src.utils.entity_matcher import (
            find_or_create_action,
            find_or_create_contact,
            find_or_create_organization
        )
        from src.config.extensions import db

        # Generate unique ID using source_id
        year = datetime.now().year
        comment_id = f"PC-{year}-{source['source_id'].upper()}-{sequence:04d}"

        # Parse location
        city, state = self._parse_location(comment.get('location', ''))

        # Analyze comment
        commenter_type = self._determine_commenter_type(
            comment.get('organization', ''),
            comment.get('comment_text', '')
        )
        position = self._extract_position(comment.get('comment_text', ''))
        topics = self._extract_topics(comment.get('comment_text', ''))

        # Find or create Action from amendment metadata
        action = None
        action_id_str = None
        if metadata.get('title'):
            try:
                action = find_or_create_action(
                    amendment_title=metadata['title'],
                    description=metadata.get('description'),
                    phase=source['phase'],
                    data_source=source['name']
                )
                if action:
                    db.session.flush()  # Get the ID without committing
                    action_id_str = action.action_id
            except Exception as e:
                logger.error(f"Error creating action: {e}")

        # Find or create Contact
        contact = None
        contact_id_int = None
        full_name = comment.get('name', '')
        email = comment.get('email', '')

        if full_name or email:
            try:
                contact = find_or_create_contact(
                    full_name=full_name,
                    email=email,
                    city=city,
                    state=state,
                    sector=commenter_type,
                    data_source=source['name']
                )
                if contact:
                    db.session.flush()
                    contact_id_int = contact.id
            except Exception as e:
                logger.error(f"Error creating contact: {e}")

        # Find or create Organization
        organization = None
        organization_id_int = None
        org_name = comment.get('organization', '')

        if org_name and org_name.strip():
            try:
                organization = find_or_create_organization(
                    org_name=org_name,
                    state=state,
                    org_type=commenter_type,
                    data_source=source['name']
                )
                if organization:
                    db.session.flush()
                    organization_id_int = organization.id

                    # Link contact to organization if both exist
                    if contact and not contact.organization_id:
                        contact.organization_id = organization_id_int
            except Exception as e:
                logger.error(f"Error creating organization: {e}")

        return {
            'comment_id': comment_id,
            'submit_date': comment.get('date', ''),
            'amendment_id': action_id_str,  # Linked to Action
            'amendment_phase': source['phase'],
            'name': full_name,
            'organization': org_name,
            'city': city,
            'state': state,
            'email': email,
            'commenter_type': commenter_type,
            'position': position,
            'key_topics': ', '.join(topics),
            'comment_text': comment.get('comment_text', ''),
            'source_url': source['url'],
            'data_source': source['name'],
            # Linked entity IDs
            'contact_id': contact_id_int,
            'organization_id': organization_id_int
        }

    def _parse_location(self, location: str) -> tuple:
        """Parse city and state from location string"""
        if not location:
            return ('', '')

        parts = [p.strip() for p in location.split(',')]
        if len(parts) >= 2:
            return (parts[0], parts[1])
        return (parts[0] if parts else '', '')

    def _determine_commenter_type(self, organization: str, comment_text: str) -> str:
        """Determine commenter type from organization and text"""
        combined = (organization + ' ' + comment_text).lower()

        if 'charter' in combined or 'for-hire' in combined or 'captain' in combined:
            return 'For-Hire'
        elif 'commercial' in combined or 'fishermen' in combined:
            return 'Commercial'
        elif 'ngo' in combined or 'organization' in combined or 'foundation' in combined:
            return 'NGO'
        elif 'gov' in combined or 'agency' in combined or 'department' in combined:
            return 'Government'
        elif 'university' in combined or 'research' in combined or 'scientist' in combined:
            return 'Academic'

        return 'Private/Recreational'

    def _extract_position(self, comment_text: str) -> str:
        """Extract position (support/oppose) from comment text"""
        if not comment_text:
            return 'Neutral'

        text_lower = comment_text.lower()

        if 'strongly support' in text_lower or 'fully support' in text_lower:
            return 'Strong Support'
        elif 'support' in text_lower or 'favor' in text_lower or 'agree' in text_lower:
            return 'Support'
        elif 'strongly oppose' in text_lower or 'completely against' in text_lower:
            return 'Strong Oppose'
        elif 'oppose' in text_lower or 'against' in text_lower or 'disagree' in text_lower:
            return 'Oppose'
        elif ('support' in text_lower and 'oppose' in text_lower) or 'however' in text_lower:
            return 'Mixed'

        return 'Neutral'

    def _extract_topics(self, comment_text: str) -> List[str]:
        """Extract key topics from comment text"""
        topics = []

        if not comment_text:
            return topics

        text_lower = comment_text.lower()

        topic_keywords = {
            'Size Limits': ['size limit', 'minimum size', 'length', 'inches'],
            'Bag Limits': ['bag limit', 'catch limit', 'daily limit', 'possession'],
            'Season': ['season', 'closure', 'open', 'closed', 'year-round'],
            'Gear': ['gear', 'hook', 'net', 'trap', 'equipment', 'tackle'],
            'Charter/For-Hire': ['charter', 'for-hire', 'headboat', 'captain'],
            'Commercial': ['commercial', 'sale', 'market', 'pounds'],
            'Recreational': ['recreational', 'private', 'angler', 'sportfishing'],
            'Conservation': ['conservation', 'sustainability', 'overfishing', 'stock'],
            'Economic': ['economic', 'business', 'livelihood', 'income'],
            'Enforcement': ['enforcement', 'compliance', 'regulation', 'violation'],
            'Allocation': ['allocation', 'quota', 'share', 'percentage'],
            'Data': ['data', 'science', 'assessment', 'survey', 'mrip']
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _remove_duplicates(self, comments: List[Dict]) -> List[Dict]:
        """Remove duplicate comments"""
        unique_comments = []
        seen = set()

        for comment in comments:
            # Create unique key from email + name + comment text
            key_parts = [
                comment.get('email', '').lower(),
                comment.get('name', '').lower(),
                comment.get('comment_text', '')[:100].lower()
            ]
            key = '|'.join(key_parts)

            if key not in seen:
                unique_comments.append(comment)
                seen.add(key)

        return unique_comments

    def get_comment_analytics(self, comments: List[Dict], action_id: Optional[str] = None) -> Dict:
        """Get analytics for comments"""
        if action_id:
            comments = [c for c in comments if c.get('amendment_id') == action_id]

        analytics = {
            'total': len(comments),
            'by_phase': {},
            'by_position': {},
            'by_type': {},
            'by_state': {},
            'top_topics': {}
        }

        for comment in comments:
            # By phase
            phase = comment.get('amendment_phase', 'Unknown')
            analytics['by_phase'][phase] = analytics['by_phase'].get(phase, 0) + 1

            # By position
            position = comment.get('position', 'Unknown')
            analytics['by_position'][position] = analytics['by_position'].get(position, 0) + 1

            # By type
            comm_type = comment.get('commenter_type', 'Unknown')
            analytics['by_type'][comm_type] = analytics['by_type'].get(comm_type, 0) + 1

            # By state
            state = comment.get('state', '')
            if state:
                analytics['by_state'][state] = analytics['by_state'].get(state, 0) + 1

            # Topics
            topics = comment.get('key_topics', '')
            if topics:
                for topic in topics.split(','):
                    topic = topic.strip()
                    if topic:
                        analytics['top_topics'][topic] = analytics['top_topics'].get(topic, 0) + 1

        return analytics
