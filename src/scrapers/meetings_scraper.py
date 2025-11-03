"""
SAFMC Meetings Scraper
Scrapes meeting data from SAFMC website
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class MeetingsScraper:
    """Scraper for SAFMC meetings and events"""

    MEETINGS_URL = 'https://safmc.net/meetings/'

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SAFMC-FMP-Tracker/1.0'
        })

    def scrape_meetings(self) -> Dict:
        """Scrape meeting data from SAFMC website"""
        results = {
            'meetings': [],
            'total_found': 0,
            'errors': []
        }

        try:
            response = self.session.get(self.MEETINGS_URL, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Look for meeting entries (articles with event class)
            meetings = soup.find_all('article', class_=re.compile(r'event'))

            for article in meetings:
                try:
                    meeting = self._parse_meeting(article)
                    if meeting:
                        results['meetings'].append(meeting)
                        results['total_found'] += 1
                except Exception as e:
                    logger.error(f"Error parsing meeting: {e}")
                    results['errors'].append(str(e))

            # Also look for other meeting structures
            meeting_divs = soup.find_all('div', class_=re.compile(r'meeting'))
            for div in meeting_divs:
                try:
                    meeting = self._parse_meeting_div(div)
                    if meeting and not self._is_duplicate(meeting, results['meetings']):
                        results['meetings'].append(meeting)
                        results['total_found'] += 1
                except Exception as e:
                    logger.error(f"Error parsing meeting div: {e}")

            logger.info(f"Found {results['total_found']} meetings")

        except requests.RequestException as e:
            logger.error(f"Error fetching meetings page: {e}")
            results['errors'].append(str(e))

        return results

    def _parse_meeting(self, article) -> Optional[Dict]:
        """Parse meeting data from article element"""
        try:
            # Extract title
            title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
            title = title_elem.get_text(strip=True) if title_elem else 'SAFMC Meeting'

            # Extract date
            date_elem = article.find('time')
            start_date = None
            if date_elem and date_elem.get('datetime'):
                try:
                    start_date = date_parser.parse(date_elem['datetime'])
                except:
                    pass

            # Extract location
            location = self._extract_location(article)

            # Extract links
            links = article.find_all('a', href=True)
            agenda_url = None
            for link in links:
                if 'agenda' in link.get_text().lower():
                    agenda_url = link['href']
                    break

            return {
                'meeting_id': self._generate_meeting_id(title, start_date),
                'title': title,
                'type': self._determine_meeting_type(title),
                'start_date': start_date,
                'end_date': start_date,  # Can be refined later
                'location': location,
                'description': self._extract_description(article),
                'agenda_url': agenda_url,
                'source_url': self.MEETINGS_URL,
                'status': 'Scheduled'
            }

        except Exception as e:
            logger.error(f"Error parsing meeting article: {e}")
            return None

    def _parse_meeting_div(self, div) -> Optional[Dict]:
        """Parse meeting data from div element"""
        try:
            text = div.get_text(strip=True)

            # Extract title (usually the first strong or heading)
            title_elem = div.find(['strong', 'b', 'h3', 'h4'])
            title = title_elem.get_text(strip=True) if title_elem else text[:100]

            # Try to extract date
            date_match = re.search(r'(\w+\s+\d{1,2}(?:-\d{1,2})?,?\s+\d{4})', text)
            start_date = None
            if date_match:
                try:
                    start_date = date_parser.parse(date_match.group(1))
                except:
                    pass

            return {
                'meeting_id': self._generate_meeting_id(title, start_date),
                'title': title,
                'type': self._determine_meeting_type(title),
                'start_date': start_date,
                'end_date': start_date,
                'location': self._extract_location(div),
                'description': text[:500],
                'source_url': self.MEETINGS_URL,
                'status': 'Scheduled'
            }

        except Exception as e:
            logger.error(f"Error parsing meeting div: {e}")
            return None

    def _generate_meeting_id(self, title: str, date: Optional[datetime]) -> str:
        """Generate unique meeting ID"""
        year = date.year if date else datetime.now().year
        title_clean = re.sub(r'[^a-z0-9]+', '-', title.lower())[:30].strip('-')
        return f"safmc-{year}-{title_clean}"

    def _determine_meeting_type(self, title: str) -> str:
        """Determine meeting type from title"""
        title_lower = title.lower()

        if 'committee' in title_lower:
            return 'Committee Meeting'
        elif 'hearing' in title_lower:
            return 'Public Hearing'
        elif 'workshop' in title_lower:
            return 'Workshop'
        elif 'webinar' in title_lower:
            return 'Webinar'
        else:
            return 'Council Meeting'

    def _extract_location(self, element) -> str:
        """Extract location from element"""
        text = element.get_text()

        # Look for common location patterns
        location_patterns = [
            r'Location:\s*([^\n]+)',
            r'Venue:\s*([^\n]+)',
            r'(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})'
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        # Check for virtual meeting
        if 'virtual' in text.lower() or 'webinar' in text.lower():
            return 'Virtual'

        return 'TBD'

    def _extract_description(self, element) -> str:
        """Extract meeting description"""
        # Try to find a paragraph element
        p_elem = element.find('p')
        if p_elem:
            return p_elem.get_text(strip=True)[:500]

        # Fallback to general text
        text = element.get_text(strip=True)
        return text[:500]

    def _is_duplicate(self, meeting: Dict, meetings: List[Dict]) -> bool:
        """Check if meeting is already in list"""
        return any(m['meeting_id'] == meeting['meeting_id'] for m in meetings)
