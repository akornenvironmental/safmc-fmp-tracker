"""
Multi-Council Calendar Scraper
Scrapes meeting calendars from multiple Regional Fishery Management Councils,
Interstate Commissions, and State Agencies using RSS feeds
Based on FisheryPulse patterns
"""

import re
import logging
import feedparser
from datetime import datetime
from typing import List, Dict, Optional
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class MultiCouncilScraper:
    """Scraper for multiple fishery management councils and agencies"""

    # Council and agency RSS feed configurations
    FEED_SOURCES = [
        # Regional Fishery Management Councils
        {
            'council': 'SAFMC',
            'name': 'South Atlantic Fishery Management Council',
            'organization_type': 'Regional Council',
            'rss_url': 'https://safmc.net/feed/',
            'filter_keywords': ['meeting', 'hearing', 'workshop', 'webinar']
        },
        {
            'council': 'NEFMC',
            'name': 'New England Fishery Management Council',
            'organization_type': 'Regional Council',
            'rss_url': 'https://www.nefmc.org/calendar/feed',
            'filter_keywords': ['meeting', 'hearing', 'workshop']
        },
        {
            'council': 'MAFMC',
            'name': 'Mid-Atlantic Fishery Management Council',
            'organization_type': 'Regional Council',
            'rss_url': 'https://www.mafmc.org/events/feed',
            'filter_keywords': ['meeting', 'hearing', 'workshop']
        },
        {
            'council': 'GFMC',
            'name': 'Gulf of Mexico Fishery Management Council',
            'organization_type': 'Regional Council',
            'rss_url': 'https://gulfcouncil.org/feed/',
            'filter_keywords': ['meeting', 'hearing', 'workshop']
        },
        # Interstate Fishery Commissions
        {
            'council': 'ASMFC',
            'name': 'Atlantic States Marine Fisheries Commission',
            'organization_type': 'Interstate Commission',
            'rss_url': 'http://www.asmfc.org/home/calendar-rss',
            'filter_keywords': ['meeting', 'hearing', 'workshop']
        },
        {
            'council': 'GSMFC',
            'name': 'Gulf States Marine Fisheries Commission',
            'organization_type': 'Interstate Commission',
            'rss_url': 'http://www.gsmfc.org/events/feed',
            'filter_keywords': ['meeting', 'hearing']
        },
        # Caribbean Fishery Management Council
        {
            'council': 'CCC',
            'name': 'Caribbean Fishery Management Council',
            'organization_type': 'Regional Council',
            'rss_url': 'https://caribbeanfmc.com/feed/',
            'filter_keywords': ['meeting', 'hearing', 'workshop']
        },
        # State Agencies (NC through FL)
        {
            'council': 'NCDMF',
            'name': 'North Carolina Division of Marine Fisheries',
            'organization_type': 'State Agency',
            'rss_url': 'https://deq.nc.gov/news/feed',
            'filter_keywords': ['fisheries', 'meeting', 'hearing', 'mfc', 'marine']
        },
        {
            'council': 'SCDNR',
            'name': 'South Carolina Department of Natural Resources',
            'organization_type': 'State Agency',
            'rss_url': 'https://www.dnr.sc.gov/news/feed',
            'filter_keywords': ['fisheries', 'meeting', 'hearing', 'marine']
        },
        {
            'council': 'GADNR',
            'name': 'Georgia Department of Natural Resources',
            'organization_type': 'State Agency',
            'rss_url': 'https://gadnr.org/feed',
            'filter_keywords': ['fisheries', 'meeting', 'hearing', 'marine']
        },
        {
            'council': 'FWC',
            'name': 'Florida Fish and Wildlife Conservation Commission',
            'organization_type': 'State Agency',
            'rss_url': 'https://myfwc.com/news/feed/',
            'filter_keywords': ['fisheries', 'meeting', 'hearing', 'commission']
        }
    ]

    def __init__(self, timeout=30):
        self.timeout = timeout

    def scrape_all_councils(self) -> Dict:
        """Scrape meetings from all configured councils and agencies"""
        results = {
            'meetings': [],
            'total_found': 0,
            'by_source': {},
            'errors': []
        }

        logger.info(f"Starting to scrape {len(self.FEED_SOURCES)} councils/agencies")

        for source in self.FEED_SOURCES:
            try:
                logger.info(f"Scraping: {source['name']}")
                meetings = self.scrape_council_feed(source)

                results['meetings'].extend(meetings)
                results['by_source'][source['council']] = len(meetings)
                results['total_found'] += len(meetings)

                logger.info(f"  Found {len(meetings)} meetings from {source['council']}")

            except Exception as e:
                logger.error(f"Error scraping {source['council']}: {e}")
                results['errors'].append({
                    'source': source['council'],
                    'error': str(e)
                })

        logger.info(f"Total meetings found: {results['total_found']}")
        return results

    def scrape_council_feed(self, source: Dict) -> List[Dict]:
        """Scrape a single council/agency RSS feed"""
        meetings = []

        try:
            # Parse RSS feed
            feed = feedparser.parse(source['rss_url'])

            if not feed.entries:
                logger.warning(f"No entries found in {source['council']} feed")
                return meetings

            # Process each entry
            for entry in feed.entries:
                # Check if entry is meeting-related
                if not self._is_meeting_entry(entry, source.get('filter_keywords', [])):
                    continue

                # Parse meeting data
                meeting = self._parse_feed_entry(entry, source)
                if meeting:
                    meetings.append(meeting)

        except Exception as e:
            logger.error(f"Error parsing feed for {source['council']}: {e}")

        return meetings

    def _is_meeting_entry(self, entry, keywords: List[str]) -> bool:
        """Check if RSS entry is meeting-related"""
        # Combine title and summary for checking
        text = (entry.get('title', '') + ' ' + entry.get('summary', '')).lower()

        # Check for any matching keywords
        return any(keyword.lower() in text for keyword in keywords)

    def _parse_feed_entry(self, entry, source: Dict) -> Optional[Dict]:
        """Parse a single RSS feed entry into meeting data"""
        try:
            title = entry.get('title', 'Untitled Meeting')

            # Extract dates
            start_date = None
            end_date = None

            # Try published date first
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                start_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                start_date = datetime(*entry.updated_parsed[:6])

            # Try to extract better dates from title or content
            better_dates = self._extract_dates_from_text(title + ' ' + entry.get('summary', ''))
            if better_dates:
                start_date = better_dates[0]
                end_date = better_dates[1] if len(better_dates) > 1 else better_dates[0]

            # Extract location
            location = self._extract_location(entry.get('summary', ''))

            # Get description
            description = self._clean_html(entry.get('summary', ''))[:500]

            # Extract link
            source_url = entry.get('link', source['rss_url'])

            # Generate unique ID
            meeting_id = self._generate_meeting_id(
                source['council'],
                title,
                start_date
            )

            return {
                'meeting_id': meeting_id,
                'title': title,
                'type': self._determine_meeting_type(title),
                'council': source['council'],
                'organization_type': source['organization_type'],
                'start_date': start_date,
                'end_date': end_date or start_date,
                'location': location,
                'description': description,
                'source_url': source_url,
                'rss_feed_url': source['rss_url'],
                'status': self._determine_status(start_date)
            }

        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None

    def _extract_dates_from_text(self, text: str) -> List[datetime]:
        """Extract date(s) from text using various patterns"""
        dates = []

        # Common date patterns
        patterns = [
            # December 8-12, 2025
            r'(\w+\s+\d{1,2})\s*[-–—]\s*(\d{1,2}),?\s+(\d{4})',
            # Dec 8-12, 2025
            r'(\w{3})\s+(\d{1,2})\s*[-–—]\s*(\d{1,2}),?\s+(\d{4})',
            # December 8, 2025
            r'(\w+\s+\d{1,2},?\s+\d{4})',
            # 12/8/2025
            r'(\d{1,2}/\d{1,2}/\d{4})',
            # 2025-12-08
            r'(\d{4}-\d{2}-\d{2})'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Handle date ranges (first pattern)
                    if len(match.groups()) >= 3 and '-' in match.group(0):
                        month_day = match.group(1)
                        end_day = match.group(2)
                        year = match.group(3)

                        # Parse start date
                        start_str = f"{month_day}, {year}"
                        start = date_parser.parse(start_str, fuzzy=True)
                        dates.append(start)

                        # Parse end date
                        month = month_day.split()[0]
                        end_str = f"{month} {end_day}, {year}"
                        end = date_parser.parse(end_str, fuzzy=True)
                        dates.append(end)
                        return dates
                    else:
                        # Single date
                        date_str = match.group(1) if match.groups() else match.group(0)
                        parsed = date_parser.parse(date_str, fuzzy=True)
                        dates.append(parsed)
                        return dates
                except:
                    continue

        return dates

    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
        # Remove HTML tags
        text = self._clean_html(text)

        # Common location patterns
        patterns = [
            r'Location:\s*([^\n]+)',
            r'Where:\s*([^\n]+)',
            r'Venue:\s*([^\n]+)',
            r'(?:at|in)\s+([A-Z][a-zA-Z\s]+(?:Hotel|Center|Building|Room)[^\n]*)',
            r'([A-Z][a-zA-Z\s]+,\s*[A-Z]{2})'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        # Check for virtual
        if re.search(r'\b(virtual|webinar|online|zoom|teams)\b', text, re.IGNORECASE):
            return 'Virtual'

        return 'TBD'

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        return re.sub(r'<[^>]+>', '', text)

    def _determine_meeting_type(self, title: str) -> str:
        """Determine meeting type from title"""
        title_lower = title.lower()

        if 'committee' in title_lower:
            return 'Committee Meeting'
        elif 'hearing' in title_lower or 'public comment' in title_lower:
            return 'Public Hearing'
        elif 'workshop' in title_lower:
            return 'Workshop'
        elif 'webinar' in title_lower:
            return 'Webinar'
        elif 'scoping' in title_lower:
            return 'Scoping Meeting'
        else:
            return 'Council Meeting'

    def _determine_status(self, start_date: Optional[datetime]) -> str:
        """Determine meeting status based on date"""
        if not start_date:
            return 'Scheduled'

        now = datetime.now()
        if start_date > now:
            return 'Scheduled'
        else:
            return 'Completed'

    def _generate_meeting_id(self, council: str, title: str, date: Optional[datetime]) -> str:
        """Generate unique meeting ID"""
        year = date.year if date else datetime.now().year
        title_clean = re.sub(r'[^a-z0-9]+', '-', title.lower())[:30].strip('-')
        return f"{council.lower()}-{year}-{title_clean}"
