"""
SAFMC Public Comments Scraper
Scrapes public comment data from various sources including Google Sheets
"""

import re
import csv
import logging
from typing import List, Dict, Optional
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
            'url': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSjyRSAei_lEHn4bmBpCxlkhq_s0RpBdzoUhzM490fgfYTJZbJMuFT6SFF8oeW34JzkkoY6pYOKBjT3/pubhtml?gid=440075844&single=true',
            'name': 'Public Comments - Sheet 1',
            'action_id': 'comments-1',
            'phase': 'Public Comment'
        },
        {
            'url': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSjyRSAei_lEHn4bmBpCxlkhq_s0RpBdzoUhzM490fgfYTJZbJMuFT6SFF8oeW34JzkkoY6pYOKBjT3/pubhtml?gid=2112604420&single=true',
            'name': 'Public Comments - Sheet 2',
            'action_id': 'comments-2',
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
                comments = self.scrape_comment_sheet(source)

                # Enhance each comment
                enhanced_comments = []
                for i, comment in enumerate(comments, 1):
                    enhanced = self._enhance_comment(comment, source, i)
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

    def scrape_comment_sheet(self, source: Dict) -> List[Dict]:
        """Scrape a single comment sheet from Google Sheets pubhtml"""
        try:
            response = self.session.get(source['url'], timeout=self.timeout)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')

            # Find the table in the HTML
            table = soup.find('table')
            if not table:
                logger.warning(f"No table found in {source['url']}")
                return []

            # Get headers from first row
            headers = []
            header_row = table.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

            if not headers:
                logger.warning(f"No headers found in {source['url']}")
                return []

            # Get data rows
            comments = []
            rows = table.find_all('tr')[1:]  # Skip header row

            for row in rows:
                cells = row.find_all('td')
                if len(cells) == 0:
                    continue

                # Create dict from headers and cells
                row_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        row_data[headers[i]] = cell.get_text(strip=True)

                # Skip empty rows
                if not any(row_data.values()):
                    continue

                # Parse comment from row
                comment = self._parse_comment_row(row_data)
                if comment and comment.get('comment_text'):
                    comments.append(comment)

            logger.info(f"  Parsed {len(comments)} comments from table with {len(headers)} columns")
            return comments

        except requests.RequestException as e:
            logger.error(f"Error fetching {source['url']}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing {source['url']}: {e}")
            return []

    def _parse_comment_row(self, row: Dict) -> Optional[Dict]:
        """Parse a single comment row from CSV"""
        # Map common header variations
        def get_field(variations: List[str]) -> str:
            for var in variations:
                for key, value in row.items():
                    if var.lower() in key.lower():
                        return value or ''
            return ''

        return {
            'date': get_field(['date', 'submit date', 'timestamp']),
            'name': get_field(['name', 'commenter', 'submitted by']),
            'organization': get_field(['organization', 'org', 'affiliation']),
            'location': get_field(['location', 'city/state', 'city', 'address']),
            'email': get_field(['email', 'e-mail', 'contact']),
            'comment_text': get_field(['comment', 'comments', 'text', 'submission'])
        }

    def _enhance_comment(self, comment: Dict, source: Dict, sequence: int) -> Dict:
        """Enhance comment with analysis and categorization"""
        # Generate unique ID
        year = datetime.now().year
        comment_id = f"PC-{year}-{source['action_id'].upper()}-{sequence:04d}"

        # Parse location
        city, state = self._parse_location(comment.get('location', ''))

        # Analyze comment
        commenter_type = self._determine_commenter_type(
            comment.get('organization', ''),
            comment.get('comment_text', '')
        )
        position = self._extract_position(comment.get('comment_text', ''))
        topics = self._extract_topics(comment.get('comment_text', ''))

        return {
            'comment_id': comment_id,
            'submit_date': comment.get('date', ''),
            'amendment_id': source['action_id'],
            'amendment_phase': source['phase'],
            'name': comment.get('name', ''),
            'organization': comment.get('organization', ''),
            'city': city,
            'state': state,
            'email': comment.get('email', ''),
            'commenter_type': commenter_type,
            'position': position,
            'key_topics': ', '.join(topics),
            'comment_text': comment.get('comment_text', ''),
            'source_url': source['url'],
            'data_source': source['name']
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
