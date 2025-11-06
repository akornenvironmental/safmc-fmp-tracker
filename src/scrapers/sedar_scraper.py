"""
SEDAR Scraper for Stock Assessment Data
Scrapes https://sedarweb.org/ for stock assessment information
"""

import requests
from bs4 import BeautifulSoup
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)


class SEDARScraper:
    """Scraper for SEDAR (SouthEast Data, Assessment, and Review) website"""

    def __init__(self):
        self.base_url = 'https://sedarweb.org'
        self.assessments_url = f'{self.base_url}/sedar-assessments/'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SAFMC FMP Tracker (aaron.kornbluth@gmail.com)'
        })

    def scrape_assessments(self) -> Dict:
        """
        Scrape all SEDAR assessments from the main assessments page

        Returns:
            Dict with results: {'success': bool, 'assessments': List, 'count': int}
        """
        try:
            logger.info("Starting SEDAR assessment scrape...")

            assessments = []
            page = 1
            max_pages = 20  # Safety limit

            # SEDAR typically lists assessments on paginated pages
            # We'll need to scrape the main page and follow links

            response = self.session.get(self.assessments_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all assessment links (typically in format /sedar-XX/)
            assessment_links = soup.find_all('a', href=re.compile(r'/sedar-\d+/?'))

            logger.info(f"Found {len(assessment_links)} assessment links")

            # Extract unique SEDAR numbers
            seen_numbers = set()
            for link in assessment_links:
                href = link.get('href')
                match = re.search(r'/sedar-(\d+)/?', href)
                if match:
                    sedar_number = match.group(1)
                    if sedar_number not in seen_numbers:
                        seen_numbers.add(sedar_number)

                        # Scrape individual assessment page
                        assessment_data = self.scrape_single_assessment(sedar_number)
                        if assessment_data:
                            assessments.append(assessment_data)

                        # Be polite - rate limit
                        time.sleep(0.5)

            # Save to database
            saved_count = self._save_assessments(assessments)

            logger.info(f"SEDAR scrape complete. Found {len(assessments)}, saved {saved_count}")

            return {
                'success': True,
                'assessments': assessments,
                'count': len(assessments),
                'saved': saved_count
            }

        except Exception as e:
            logger.error(f"Error scraping SEDAR: {e}")
            return {
                'success': False,
                'error': str(e),
                'assessments': [],
                'count': 0
            }

    def scrape_single_assessment(self, sedar_number: str) -> Optional[Dict]:
        """
        Scrape a single SEDAR assessment page

        Args:
            sedar_number: SEDAR number (e.g., '73' for SEDAR-73)

        Returns:
            Dict with assessment data or None if failed
        """
        try:
            url = f'{self.base_url}/sedar-{sedar_number}/'
            logger.info(f"Scraping SEDAR-{sedar_number}...")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract data from the page
            # NOTE: This is a template - actual selectors will need to be
            # adjusted based on SEDAR's actual HTML structure

            assessment = {
                'sedar_number': f'SEDAR-{sedar_number}',
                'source_url': url,
                'scraped_at': datetime.utcnow().isoformat()
            }

            # Try to extract species name (common patterns)
            title = soup.find('h1', class_='entry-title')
            if title:
                assessment['title'] = title.text.strip()
                # Species is often in the title
                assessment['species'] = self._extract_species_from_title(title.text)

            # Look for assessment type
            content = soup.find('div', class_='entry-content')
            if content:
                text = content.get_text()

                # Extract assessment type
                if 'Benchmark' in text or 'benchmark' in text:
                    assessment['assessment_type'] = 'Benchmark'
                elif 'Update' in text or 'update' in text:
                    assessment['assessment_type'] = 'Update'
                elif 'Standard' in text or 'standard' in text:
                    assessment['assessment_type'] = 'Standard'
                elif 'Research Track' in text or 'research track' in text:
                    assessment['assessment_type'] = 'Research Track'
                else:
                    assessment['assessment_type'] = 'Unknown'

                # Extract status
                if 'Completed' in text or 'completed' in text:
                    assessment['status'] = 'Completed'
                elif 'In Progress' in text or 'in progress' in text:
                    assessment['status'] = 'In Progress'
                elif 'Planning' in text or 'planning' in text:
                    assessment['status'] = 'Planning'
                else:
                    assessment['status'] = 'Unknown'

                # Look for dates
                date_patterns = [
                    r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
                    r'(\d{4}-\d{2}-\d{2})',      # YYYY-MM-DD
                    r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
                ]

                dates_found = []
                for pattern in date_patterns:
                    matches = re.findall(pattern, text)
                    dates_found.extend(matches)

                if dates_found:
                    # First date is often start date, last is completion
                    assessment['start_date'] = dates_found[0] if len(dates_found) > 0 else None
                    assessment['completion_date'] = dates_found[-1] if len(dates_found) > 1 else None

            # Extract documents
            documents = []
            doc_links = soup.find_all('a', href=re.compile(r'\.(pdf|PDF)$'))
            for link in doc_links:
                doc_url = link.get('href')
                if not doc_url.startswith('http'):
                    doc_url = self.base_url + doc_url
                documents.append({
                    'title': link.text.strip(),
                    'url': doc_url
                })

            if documents:
                assessment['documents'] = documents
                assessment['document_url'] = documents[0]['url']  # Primary document

            # Determine FMPs affected (SAFMC specific)
            fmps = self._determine_fmps(assessment.get('species', ''))
            if fmps:
                assessment['fmps_affected'] = fmps

            logger.info(f"Successfully scraped SEDAR-{sedar_number}: {assessment.get('species', 'Unknown')}")

            return assessment

        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping SEDAR-{sedar_number}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error scraping SEDAR-{sedar_number}: {e}")
            return None

    def scrape_calendar_events(self) -> List[Dict]:
        """
        Scrape SEDAR calendar for upcoming events (workshops, webinars, meetings)

        Returns:
            List of calendar events
        """
        try:
            # SEDAR calendar URL may vary - adjust as needed
            calendar_url = f'{self.base_url}/events/'

            response = self.session.get(calendar_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            events = []

            # Parse event listings (structure will vary)
            # This is a template - adjust selectors based on actual HTML

            event_items = soup.find_all('article', class_='event')
            for item in event_items:
                event = {}

                # Extract event title
                title = item.find('h2')
                if title:
                    event['title'] = title.text.strip()

                # Extract date
                date_elem = item.find('time')
                if date_elem:
                    event['date'] = date_elem.get('datetime')

                # Extract location
                location = item.find('span', class_='location')
                if location:
                    event['location'] = location.text.strip()

                # Extract SEDAR number if mentioned
                sedar_match = re.search(r'SEDAR[- ](\d+)', event.get('title', ''))
                if sedar_match:
                    event['sedar_number'] = f"SEDAR-{sedar_match.group(1)}"

                # Event type
                title_lower = event.get('title', '').lower()
                if 'data workshop' in title_lower:
                    event['event_type'] = 'Data Workshop'
                elif 'assessment workshop' in title_lower:
                    event['event_type'] = 'Assessment Workshop'
                elif 'review workshop' in title_lower:
                    event['event_type'] = 'Review Workshop'
                elif 'webinar' in title_lower:
                    event['event_type'] = 'Webinar'
                elif 'steering' in title_lower:
                    event['event_type'] = 'Steering Committee'
                else:
                    event['event_type'] = 'Meeting'

                event['source'] = 'SEDAR'
                event['source_url'] = calendar_url

                events.append(event)

            logger.info(f"Scraped {len(events)} SEDAR calendar events")
            return events

        except Exception as e:
            logger.error(f"Error scraping SEDAR calendar: {e}")
            return []

    def scrape_public_comments_google_sheet(self, sheet_url: str) -> List[Dict]:
        """
        Scrape public comments from a Google Sheets published HTML page

        Args:
            sheet_url: Published Google Sheets URL (e.g., /pubhtml?gid=...)

        Returns:
            List of comment dictionaries
        """
        try:
            logger.info(f"Scraping Google Sheets comments: {sheet_url}")

            response = self.session.get(sheet_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            comments = []

            # Google Sheets published as HTML uses table structure
            table = soup.find('table')
            if not table:
                logger.warning("No table found in Google Sheets HTML")
                return []

            rows = table.find_all('tr')

            # First row is usually headers
            if len(rows) < 2:
                return []

            headers_row = rows[0]
            headers = [th.text.strip().lower() for th in headers_row.find_all(['th', 'td'])]

            # Map common column names
            name_col = next((i for i, h in enumerate(headers) if 'name' in h), None)
            org_col = next((i for i, h in enumerate(headers) if 'org' in h or 'affiliation' in h), None)
            date_col = next((i for i, h in enumerate(headers) if 'date' in h or 'timestamp' in h), None)
            comment_col = next((i for i, h in enumerate(headers) if 'comment' in h or 'question' in h or 'feedback' in h), None)

            # Parse data rows
            for row in rows[1:]:
                cells = row.find_all('td')
                if len(cells) < 2:
                    continue

                comment = {
                    'source_url': sheet_url,
                    'created_at': datetime.utcnow().isoformat()
                }

                if name_col is not None and name_col < len(cells):
                    comment['commenter_name'] = cells[name_col].text.strip()

                if org_col is not None and org_col < len(cells):
                    comment['organization'] = cells[org_col].text.strip()

                if date_col is not None and date_col < len(cells):
                    comment['comment_date'] = cells[date_col].text.strip()

                if comment_col is not None and comment_col < len(cells):
                    comment['comment_text'] = cells[comment_col].text.strip()

                # Extract SEDAR number from URL parameters
                sedar_match = re.search(r'gid=(\d+)', sheet_url)
                if sedar_match:
                    # Try to find corresponding SEDAR number
                    # This mapping would need to be maintained
                    comment['comment_type'] = 'Public Comment'

                comments.append(comment)

            logger.info(f"Scraped {len(comments)} comments from Google Sheet")
            return comments

        except Exception as e:
            logger.error(f"Error scraping Google Sheets comments: {e}")
            return []

    def _extract_species_from_title(self, title: str) -> str:
        """Extract species name from assessment title"""
        # Common patterns: "SEDAR 73: Red Snapper", "Red Snapper Assessment", etc.
        # Remove SEDAR number
        title = re.sub(r'SEDAR[- ]?\d+:?\s*', '', title, flags=re.IGNORECASE)

        # Remove common words
        title = re.sub(r'(assessment|update|benchmark|stock|evaluation)', '', title, flags=re.IGNORECASE)

        return title.strip()

    def _determine_fmps(self, species: str) -> List[str]:
        """
        Determine which SAFMC FMPs a species belongs to

        Args:
            species: Species common name

        Returns:
            List of FMP names
        """
        species_lower = species.lower()

        fmps = []

        # Snapper Grouper
        snapper_grouper_species = [
            'snapper', 'grouper', 'hogfish', 'tilefish', 'triggerfish',
            'grunt', 'porgy', 'sea bass', 'jack', 'amberjack'
        ]
        if any(sp in species_lower for sp in snapper_grouper_species):
            fmps.append('Snapper Grouper')

        # Coastal Migratory Pelagics
        cmp_species = ['mackerel', 'cobia', 'king mackerel', 'spanish mackerel']
        if any(sp in species_lower for sp in cmp_species):
            fmps.append('Coastal Migratory Pelagics')

        # Dolphin Wahoo
        if 'dolphin' in species_lower or 'wahoo' in species_lower or 'mahi' in species_lower:
            fmps.append('Dolphin Wahoo')

        # Shrimp
        if 'shrimp' in species_lower:
            fmps.append('Shrimp')

        # Spiny Lobster
        if 'lobster' in species_lower and 'spiny' in species_lower:
            fmps.append('Spiny Lobster')

        # Golden Crab
        if 'golden crab' in species_lower:
            fmps.append('Golden Crab')

        return fmps if fmps else ['Unknown']

    def _save_assessments(self, assessments: List[Dict]) -> int:
        """
        Save assessments to database

        Args:
            assessments: List of assessment dictionaries

        Returns:
            Number of assessments saved
        """
        try:
            from src.database import get_db_connection

            conn = get_db_connection()
            cur = conn.cursor()

            saved_count = 0

            for assessment in assessments:
                try:
                    # Check if assessment already exists
                    cur.execute(
                        "SELECT id FROM stock_assessments WHERE sedar_number = %s",
                        (assessment.get('sedar_number'),)
                    )

                    existing = cur.fetchone()

                    if existing:
                        # Update existing
                        cur.execute("""
                            UPDATE stock_assessments
                            SET species = %s, assessment_type = %s, status = %s,
                                source_url = %s, updated_at = CURRENT_TIMESTAMP
                            WHERE sedar_number = %s
                        """, (
                            assessment.get('species'),
                            assessment.get('assessment_type'),
                            assessment.get('status'),
                            assessment.get('source_url'),
                            assessment.get('sedar_number')
                        ))
                    else:
                        # Insert new
                        cur.execute("""
                            INSERT INTO stock_assessments
                            (sedar_number, species, assessment_type, status,
                             fmps_affected, source_url, document_url)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            assessment.get('sedar_number'),
                            assessment.get('species'),
                            assessment.get('assessment_type'),
                            assessment.get('status'),
                            assessment.get('fmps_affected'),
                            assessment.get('source_url'),
                            assessment.get('document_url')
                        ))

                    saved_count += 1

                except Exception as e:
                    logger.error(f"Error saving assessment {assessment.get('sedar_number')}: {e}")
                    continue

            conn.commit()
            cur.close()
            conn.close()

            return saved_count

        except Exception as e:
            logger.error(f"Error saving assessments to database: {e}")
            return 0
