"""
FisheryPulse Meeting Scraper
Aggregates meetings from Federal Register, NOAA, and all regional fishery management councils/commissions
"""

import requests
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import feedparser
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Data source configuration
SOURCES = {
    'nefmc': {
        'name': 'New England Fishery Management Council',
        'short': 'NEFMC',
        'url': 'https://www.nefmc.org/calendar',
        'feed_url': 'https://www.nefmc.org/events/feed',
        'region': 'Northeast',
        'color': '#1e40af'
    },
    'mafmc': {
        'name': 'Mid-Atlantic Fishery Management Council',
        'short': 'MAFMC',
        'url': 'https://www.mafmc.org/council-events',
        'feed_url': 'https://www.mafmc.org/events/feed',
        'region': 'Mid-Atlantic',
        'color': '#0891b2'
    },
    'safmc': {
        'name': 'South Atlantic Fishery Management Council',
        'short': 'SAFMC',
        'url': 'https://safmc.net/events/',
        'feed_url': 'https://safmc.net/events/feed',
        'region': 'Southeast',
        'color': '#0d9488'
    },
    'gmfmc': {
        'name': 'Gulf of Mexico Fishery Management Council',
        'short': 'GMFMC',
        'url': 'https://gulfcouncil.org/meetings/',
        'feed_url': None,
        'region': 'Gulf of Mexico',
        'color': '#059669'
    },
    'cfmc': {
        'name': 'Caribbean Fishery Management Council',
        'short': 'CFMC',
        'url': 'https://www.caribbeanfmc.com/meetings',
        'feed_url': None,
        'region': 'Caribbean',
        'color': '#84cc16'
    },
    'pfmc': {
        'name': 'Pacific Fishery Management Council',
        'short': 'PFMC',
        'url': 'https://www.pcouncil.org/events/',
        'feed_url': 'https://www.pcouncil.org/events/feed',
        'region': 'West Coast',
        'color': '#eab308'
    },
    'npfmc': {
        'name': 'North Pacific Fishery Management Council',
        'short': 'NPFMC',
        'url': 'https://www.npfmc.org/meetings/',
        'feed_url': None,
        'region': 'Alaska',
        'color': '#f97316'
    },
    'wpfmc': {
        'name': 'Western Pacific Fishery Management Council',
        'short': 'WPFMC',
        'url': 'https://www.wpcouncil.org/meetings-calendars/',
        'feed_url': None,
        'region': 'Pacific Islands',
        'color': '#ef4444'
    },
    'asmfc': {
        'name': 'Atlantic States Marine Fisheries Commission',
        'short': 'ASMFC',
        'url': 'http://www.asmfc.org/calendar',
        'feed_url': None,
        'region': 'Atlantic Coast',
        'color': '#dc2626'
    },
    'gsmfc': {
        'name': 'Gulf States Marine Fisheries Commission',
        'short': 'GSMFC',
        'url': 'https://www.gsmfc.org/meetings.php',
        'feed_url': None,
        'region': 'Gulf States',
        'color': '#c026d3'
    },
    'psmfc': {
        'name': 'Pacific States Marine Fisheries Commission',
        'short': 'PSMFC',
        'url': 'https://www.psmfc.org/events',
        'feed_url': None,
        'region': 'Pacific States',
        'color': '#9333ea'
    },
    'ncdmf': {
        'name': 'North Carolina Division of Marine Fisheries',
        'short': 'NCDMF',
        'url': 'https://deq.nc.gov/about/divisions/marine-fisheries/calendar',
        'feed_url': None,
        'region': 'North Carolina',
        'color': '#7c3aed'
    },
    'scdnr': {
        'name': 'South Carolina Department of Natural Resources',
        'short': 'SCDNR',
        'url': 'https://www.dnr.sc.gov/news/calendar.html',
        'feed_url': None,
        'region': 'South Carolina',
        'color': '#db2777'
    },
    'gadnr': {
        'name': 'Georgia Department of Natural Resources',
        'short': 'GADNR',
        'url': 'https://coastalgadnr.org/Calendar',
        'feed_url': None,
        'region': 'Georgia',
        'color': '#ea580c'
    },
    'fwc': {
        'name': 'Florida Fish and Wildlife Conservation Commission',
        'short': 'FWC',
        'url': 'https://myfwc.com/about/events/',
        'feed_url': 'https://myfwc.com/about/events/rss/',
        'region': 'Florida',
        'color': '#f59e0b'
    }
}

class FisheryPulseScraper:
    """Comprehensive scraper for all fishery management meetings"""

    def __init__(self):
        self.meetings = []

    def scrape_all(self) -> List[Dict]:
        """Scrape meetings from all sources"""
        logger.info("Starting FisheryPulse comprehensive scrape...")

        # 1. Federal Register
        try:
            fed_meetings = self.scrape_federal_register()
            self.meetings.extend(fed_meetings)
            logger.info(f"Fetched {len(fed_meetings)} meetings from Federal Register")
        except Exception as e:
            logger.error(f"Error scraping Federal Register: {e}")

        # 2. NOAA Events
        try:
            noaa_meetings = self.scrape_noaa_events()
            self.meetings.extend(noaa_meetings)
            logger.info(f"Fetched {len(noaa_meetings)} meetings from NOAA Events")
        except Exception as e:
            logger.error(f"Error scraping NOAA Events: {e}")

        # 3. Regional Councils RSS Feeds and HTML Scraping
        for source_key, source in SOURCES.items():
            try:
                if source['feed_url']:
                    source_meetings = self.scrape_rss_feed(source_key, source)
                    self.meetings.extend(source_meetings)
                    logger.info(f"Fetched {len(source_meetings)} meetings from {source['short']} (RSS)")
                else:
                    # HTML scraping for sources without RSS feeds
                    source_meetings = self.scrape_html_calendar(source_key, source)
                    self.meetings.extend(source_meetings)
                    logger.info(f"Fetched {len(source_meetings)} meetings from {source['short']} (HTML)")
            except Exception as e:
                logger.error(f"Error scraping {source['short']}: {e}")

        # Deduplicate and sort
        unique_meetings = self.deduplicate_meetings(self.meetings)
        unique_meetings.sort(key=lambda x: x.get('date', datetime.now()))

        logger.info(f"Total unique meetings: {len(unique_meetings)}")
        return unique_meetings

    def scrape_federal_register(self) -> List[Dict]:
        """Scrape Federal Register API for fisheries meetings"""
        meetings = []
        base_url = 'https://www.federalregister.gov/api/v1/documents.json'

        params = {
            'conditions[agencies][]': 'national-oceanic-and-atmospheric-administration',
            'conditions[term]': 'fisheries meeting OR fisheries hearing OR fisheries council',
            'conditions[type][]': ['notice', 'proposed_rule'],
            'per_page': 100,
            'fields[]': ['title', 'abstract', 'html_url', 'publication_date', 'document_number']
        }

        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            for doc in data.get('results', []):
                meeting = self.parse_federal_register_doc(doc)
                if meeting:
                    meetings.append(meeting)

        except Exception as e:
            logger.error(f"Federal Register API error: {e}")

        return meetings

    def parse_federal_register_doc(self, doc: Dict) -> Optional[Dict]:
        """Parse a Federal Register document into a meeting"""
        title = doc.get('title', '')
        abstract = doc.get('abstract', '')
        text = f"{title} {abstract}"

        # Check if this is actually a meeting notice
        if not re.search(r'meeting|hearing|session|workshop|webinar|conference', text, re.I):
            return None

        # Extract date from abstract
        meeting_date = self.extract_date_from_text(abstract)
        if not meeting_date:
            pub_date = datetime.strptime(doc.get('publication_date'), '%Y-%m-%d')
            meeting_date = pub_date + timedelta(days=30)

        # Determine organization
        organization = 'NOAA Fisheries'
        for source_key, source in SOURCES.items():
            if source['name'].lower() in text.lower():
                organization = source['name']
                break

        is_virtual = bool(re.search(r'webinar|virtual|online|remote|zoom|teams|webex', text, re.I))

        return {
            'source': 'Federal Register',
            'organization': organization,
            'title': title,
            'description': abstract,
            'date': meeting_date,
            'location': '' if is_virtual else 'See Notice',
            'is_virtual': is_virtual,
            'url': doc.get('html_url', ''),
            'meeting_type': self.determine_meeting_type(text)
        }

    def scrape_noaa_events(self) -> List[Dict]:
        """Scrape NOAA Fisheries events page"""
        meetings = []
        url = 'https://www.fisheries.noaa.gov/events'

        try:
            headers = {'User-Agent': 'FisheryPulse/1.0 (Fisheries Meeting Calendar)'}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            events = soup.find_all('article', class_=re.compile('event'))

            for event in events:
                meeting = self.parse_noaa_event(event)
                if meeting:
                    meetings.append(meeting)

        except Exception as e:
            logger.error(f"NOAA Events scraping error: {e}")

        return meetings

    def parse_noaa_event(self, event) -> Optional[Dict]:
        """Parse a NOAA event HTML element"""
        try:
            title_elem = event.find(['h2', 'h3'], class_=re.compile('title|heading'))
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)

            date_elem = event.find('time')
            meeting_date = datetime.now()
            if date_elem and date_elem.get('datetime'):
                meeting_date = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))

            url_elem = event.find('a', href=True)
            url = 'https://www.fisheries.noaa.gov' + url_elem['href'] if url_elem else 'https://www.fisheries.noaa.gov/events'

            return {
                'source': 'NOAA Events',
                'organization': 'NOAA Fisheries',
                'title': title,
                'date': meeting_date,
                'location': '',
                'is_virtual': bool(re.search(r'virtual|webinar|online', title, re.I)),
                'url': url,
                'meeting_type': self.determine_meeting_type(title)
            }
        except Exception as e:
            logger.error(f"Error parsing NOAA event: {e}")
            return None

    def scrape_rss_feed(self, source_key: str, source: Dict) -> List[Dict]:
        """Scrape RSS feed from a fishery council"""
        meetings = []

        try:
            feed = feedparser.parse(source['feed_url'])

            for entry in feed.entries:
                meeting = self.parse_rss_entry(entry, source_key, source)
                if meeting:
                    meetings.append(meeting)

        except Exception as e:
            logger.error(f"Error parsing RSS feed from {source['short']}: {e}")

        return meetings

    def parse_rss_entry(self, entry, source_key: str, source: Dict) -> Optional[Dict]:
        """Parse an RSS feed entry into a meeting"""
        title = entry.get('title', '')
        description = entry.get('description', entry.get('summary', ''))
        link = entry.get('link', source['url'])

        # For SAFMC, construct proper event URL from title
        if source_key == 'safmc' and (not link or link == 'https://safmc.net/events/'):
            slug = re.sub(r'[^a-z0-9\s-]', '', title.lower())
            slug = re.sub(r'\s+', '-', slug).strip('-')
            link = f"https://safmc.net/events/{slug}/"

        # Extract meeting date from title or description
        meeting_date = self.extract_meeting_date_from_title(title, description)

        # Fall back to published date
        if not meeting_date and entry.get('published_parsed'):
            meeting_date = datetime(*entry.published_parsed[:6])

        if not meeting_date:
            meeting_date = datetime.now()

        is_virtual = bool(re.search(r'virtual|webinar|online|zoom|teams', f"{title} {description}", re.I))

        return {
            'source': source['short'],
            'organization': source['name'],
            'title': title,
            'description': description,
            'date': meeting_date,
            'location': '' if is_virtual else 'TBD',
            'is_virtual': is_virtual,
            'url': link,
            'meeting_type': self.determine_meeting_type(f"{title} {description}"),
            'region': source['region']
        }

    def scrape_html_calendar(self, source_key: str, source: Dict) -> List[Dict]:
        """Scrape HTML calendar pages for councils without RSS feeds"""
        meetings = []

        try:
            headers = {'User-Agent': 'FisheryPulse/1.0 (Fisheries Meeting Calendar)'}
            response = requests.get(source['url'], headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try different calendar HTML patterns
            # Pattern 1: Table-based calendars
            calendar_tables = soup.find_all('table', class_=re.compile('calendar|event|meeting', re.I))
            for table in calendar_tables:
                rows = table.find_all('tr')
                for row in rows:
                    meeting = self.parse_calendar_row(row, source_key, source)
                    if meeting:
                        meetings.append(meeting)

            # Pattern 2: List/div-based calendars
            event_containers = soup.find_all(['div', 'article', 'li'], class_=re.compile('event|meeting|calendar|item', re.I))
            for container in event_containers[:50]:  # Limit to first 50 to avoid noise
                meeting = self.parse_calendar_container(container, source_key, source)
                if meeting:
                    meetings.append(meeting)

            # Pattern 3: Links with date patterns in text
            links = soup.find_all('a', href=True)
            for link in links:
                link_text = link.get_text(strip=True)
                if re.search(r'(meeting|council|hearing|workshop|webinar)', link_text, re.I):
                    meeting_date = self.extract_date_from_text(link_text)
                    if meeting_date and meeting_date > datetime.now() - timedelta(days=365):
                        meetings.append({
                            'source': source['short'],
                            'organization': source['name'],
                            'title': link_text,
                            'description': '',
                            'date': meeting_date,
                            'location': 'TBD',
                            'is_virtual': bool(re.search(r'virtual|webinar|online', link_text, re.I)),
                            'url': link['href'] if link['href'].startswith('http') else source['url'] + link['href'],
                            'meeting_type': self.determine_meeting_type(link_text),
                            'region': source['region']
                        })

        except Exception as e:
            logger.error(f"Error scraping HTML calendar from {source['short']}: {e}")

        return meetings

    def parse_calendar_row(self, row, source_key: str, source: Dict) -> Optional[Dict]:
        """Parse a table row that might contain meeting info"""
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                return None

            # Try to extract date and title from cells
            text = ' '.join([cell.get_text(strip=True) for cell in cells])

            if not re.search(r'(meeting|council|hearing|workshop|session)', text, re.I):
                return None

            meeting_date = self.extract_date_from_text(text)
            if not meeting_date or meeting_date < datetime.now() - timedelta(days=365):
                return None

            link = row.find('a', href=True)
            url = link['href'] if link else source['url']
            if not url.startswith('http'):
                url = source['url'] + url

            return {
                'source': source['short'],
                'organization': source['name'],
                'title': text[:200],  # Limit title length
                'description': '',
                'date': meeting_date,
                'location': 'TBD',
                'is_virtual': bool(re.search(r'virtual|webinar|online', text, re.I)),
                'url': url,
                'meeting_type': self.determine_meeting_type(text),
                'region': source['region']
            }
        except Exception:
            return None

    def parse_calendar_container(self, container, source_key: str, source: Dict) -> Optional[Dict]:
        """Parse a div/article container that might contain meeting info"""
        try:
            text = container.get_text(strip=True)

            # Must contain meeting-related keywords
            if not re.search(r'(meeting|council|hearing|workshop|webinar|session)', text, re.I):
                return None

            # Must have a date
            meeting_date = self.extract_date_from_text(text)
            if not meeting_date or meeting_date < datetime.now() - timedelta(days=365):
                return None

            # Try to extract title from heading
            title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'])
            title = title_elem.get_text(strip=True) if title_elem else text[:200]

            link = container.find('a', href=True)
            url = link['href'] if link else source['url']
            if not url.startswith('http'):
                url = source['url'] + url

            return {
                'source': source['short'],
                'organization': source['name'],
                'title': title,
                'description': text[:500] if len(text) > 200 else '',
                'date': meeting_date,
                'location': 'TBD',
                'is_virtual': bool(re.search(r'virtual|webinar|online', text, re.I)),
                'url': url,
                'meeting_type': self.determine_meeting_type(text),
                'region': source['region']
            }
        except Exception:
            return None

    def extract_meeting_date_from_title(self, title: str, description: str = '') -> Optional[datetime]:
        """Extract meeting date from title (e.g., 'December 2025 Council Meeting')"""
        text = f"{title} {description}"

        # Month Year pattern
        match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})', text, re.I)
        if match:
            month_name, year = match.groups()
            month = datetime.strptime(month_name, '%B').month

            # Look for specific day
            day_match = re.search(rf'{month_name}\s+(\d{{1,2}})(?:[-–]\d{{1,2}})?[\s,]+{year}', text, re.I)
            day = int(day_match.group(1)) if day_match else 1

            return datetime(int(year), month, day)

        return self.extract_date_from_text(text)

    def extract_date_from_text(self, text: str) -> Optional[datetime]:
        """Extract date from text using various patterns"""
        patterns = [
            r'(\w+)\s+(\d{1,2})(?:[-–](\d{1,2}))?,?\s+(\d{4})',  # Month DD-DD, YYYY
            r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',  # MM/DD/YYYY
            r'(\d{4})-(\d{2})-(\d{2})',  # ISO format
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    groups = match.groups()
                    if groups[0].isalpha():
                        # Month name format
                        month = datetime.strptime(groups[0], '%B').month if len(groups[0]) > 3 else datetime.strptime(groups[0], '%b').month
                        day = int(groups[1])
                        year = int(groups[3] if len(groups) > 3 else groups[2])
                        return datetime(year, month, day)
                    elif '-' in match.group(0) and len(groups[0]) == 4:
                        # ISO format
                        return datetime.strptime(match.group(0), '%Y-%m-%d')
                    else:
                        # MM/DD/YYYY
                        return datetime(int(groups[2]), int(groups[0]), int(groups[1]))
                except (ValueError, AttributeError):
                    continue

        return None

    def determine_meeting_type(self, text: str) -> str:
        """Determine meeting type from text"""
        text_lower = text.lower()

        types = {
            'stock assessment': 'Stock Assessment',
            'public hearing': 'Public Hearing',
            'advisory panel': 'Advisory Panel',
            'webinar': 'Webinar',
            'workshop': 'Workshop',
            'scoping': 'Scoping Meeting',
            'council meeting': 'Council Meeting',
            'executive committee': 'Executive Committee',
            'scientific committee': 'Scientific Committee'
        }

        for keyword, meeting_type in types.items():
            if keyword in text_lower:
                return meeting_type

        return 'Meeting'

    def deduplicate_meetings(self, meetings: List[Dict]) -> List[Dict]:
        """Remove duplicate meetings based on title, date, and organization"""
        seen = {}
        unique = []

        for meeting in meetings:
            if not meeting.get('date'):
                continue

            date_str = meeting['date'].strftime('%Y-%m-%d')
            title_snippet = meeting.get('title', '')[:50].lower()
            org = meeting.get('organization', '')

            key = f"{title_snippet}_{date_str}_{org}"

            if key not in seen:
                seen[key] = meeting
                unique.append(meeting)
            else:
                # Keep the one with better description
                existing = seen[key]
                if len(meeting.get('description', '')) > len(existing.get('description', '')):
                    unique.remove(existing)
                    unique.append(meeting)
                    seen[key] = meeting

        return unique

    def save_to_database(self, meetings: List[Dict], db) -> int:
        """Save scraped meetings to database using SQLAlchemy"""
        from src.models.meeting import Meeting

        saved_count = 0

        for meeting_data in meetings:
            try:
                # Generate unique meeting_id
                meeting_id = f"{meeting_data.get('source', 'fp')}_{meeting_data['date'].strftime('%Y%m%d')}_{meeting_data['title'][:50]}"
                meeting_id = meeting_id.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').lower()
                meeting_id = re.sub(r'[^a-z0-9_-]', '', meeting_id)

                # Check if meeting already exists
                existing = Meeting.query.filter_by(
                    meeting_id=meeting_id
                ).first()

                if existing:
                    continue  # Skip duplicate

                # Create new meeting using SQLAlchemy ORM
                new_meeting = Meeting(
                    meeting_id=meeting_id,
                    title=meeting_data['title'],
                    description=meeting_data.get('description', ''),
                    start_date=meeting_data['date'],
                    location=meeting_data.get('location', ''),
                    type=meeting_data.get('meeting_type', 'Meeting'),
                    council=meeting_data.get('organization', ''),
                    region=meeting_data.get('region', ''),
                    is_virtual=meeting_data.get('is_virtual', False),
                    source_url=meeting_data.get('url', ''),
                    source=meeting_data.get('source', ''),
                    status='Scheduled'
                )

                db.session.add(new_meeting)
                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving meeting '{meeting_data.get('title')}': {e}")
                db.session.rollback()
                continue

        try:
            db.session.commit()
            logger.info(f"Saved {saved_count} new meetings to database")
        except Exception as e:
            logger.error(f"Error committing meetings: {e}")
            db.session.rollback()

        return saved_count
