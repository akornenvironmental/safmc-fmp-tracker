"""
SSC Meeting Scraper
Scrapes SSC meetings, agendas, briefing books, and reports from safmc.net
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SSCMeetingScraper:
    """Scraper for SSC meetings from safmc.net"""

    BASE_URL = "https://safmc.net"
    SSC_MEETINGS_URL = f"{BASE_URL}/scientific-and-statistical-committee-meeting/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def scrape_all_meetings(self) -> List[Dict]:
        """
        Scrape all SSC meetings from the main page
        Returns list of meeting dictionaries
        """
        try:
            logger.info(f"Fetching SSC meetings from {self.SSC_MEETINGS_URL}")
            response = self.session.get(self.SSC_MEETINGS_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            meetings = []

            # Find all meeting sections
            # The page has sections for upcoming and past meetings
            meeting_sections = soup.find_all(['h3', 'h4'], class_=lambda x: x and 'meeting' in x.lower() if x else False)

            # Alternative: Find all article or div containers with meeting info
            if not meeting_sections:
                meeting_sections = soup.find_all(['article', 'div'], class_=lambda x: x and 'post' in x.lower() if x else False)

            # If still nothing, try finding by heading pattern
            if not meeting_sections:
                meeting_sections = soup.find_all(['h3', 'h4'])

            for section in meeting_sections:
                meeting_data = self._parse_meeting_section(section)
                if meeting_data:
                    meetings.append(meeting_data)

            logger.info(f"Found {len(meetings)} SSC meetings")
            return meetings

        except Exception as e:
            logger.error(f"Error scraping SSC meetings: {e}")
            return []

    def _parse_meeting_section(self, section) -> Optional[Dict]:
        """
        Parse a meeting section and extract meeting data
        """
        try:
            # Get meeting title from heading
            title = section.get_text(strip=True)

            # Skip if not a meeting title
            if not any(keyword in title.lower() for keyword in ['ssc', 'meeting', 'panel', 'committee']):
                return None

            # Find parent container with meeting details
            parent = section.find_parent(['article', 'div', 'section'])
            if not parent:
                parent = section.find_next_sibling()

            if not parent:
                return None

            # Extract meeting details
            meeting_data = {
                'title': title,
                'meeting_type': self._determine_meeting_type(title),
                'description': None,
                'location': None,
                'is_virtual': False,
                'meeting_date_start': None,
                'meeting_date_end': None,
                'agenda_url': None,
                'briefing_book_url': None,
                'report_url': None,
                'webinar_link': None,
                'topics': [],
                'species_discussed': []
            }

            # Extract date from title
            date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{4})', title)
            if date_match:
                month_str = date_match.group(1)
                year = int(date_match.group(2))
                # Parse month
                month_map = {
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                }
                month = month_map.get(month_str, 1)
                meeting_data['meeting_date_start'] = datetime(year, month, 1)

            # Find all links in the section
            links = parent.find_all('a', href=True)
            for link in links:
                href = link['href']
                link_text = link.get_text(strip=True).lower()

                # Categorize links
                if 'agenda' in link_text or 'agenda' in href.lower():
                    meeting_data['agenda_url'] = self._normalize_url(href)
                elif 'briefing' in link_text or 'briefing' in href.lower():
                    meeting_data['briefing_book_url'] = self._normalize_url(href)
                elif 'report' in link_text or 'report' in href.lower() or 'summary' in link_text:
                    meeting_data['report_url'] = self._normalize_url(href)
                elif 'webinar' in link_text or 'zoom' in link_text:
                    meeting_data['webinar_link'] = href

            # Extract location and date details from text
            text_content = parent.get_text()

            # Check for virtual/webinar
            if 'webinar' in text_content.lower() or 'virtual' in text_content.lower():
                meeting_data['is_virtual'] = True

            # Extract location
            location_match = re.search(r'Location:\s*([^\n]+)', text_content)
            if location_match:
                meeting_data['location'] = location_match.group(1).strip()

            # Extract specific dates
            date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})(?:[-–]\d{1,2})?,?\s+(\d{4})'
            date_match = re.search(date_pattern, text_content)
            if date_match:
                month_str = date_match.group(1)
                day = int(date_match.group(2))
                year = int(date_match.group(3))
                month_map = {
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                }
                month = month_map.get(month_str, 1)
                try:
                    meeting_data['meeting_date_start'] = datetime(year, month, day)
                except ValueError:
                    meeting_data['meeting_date_start'] = datetime(year, month, 1)

            return meeting_data

        except Exception as e:
            logger.error(f"Error parsing meeting section: {e}")
            return None

    def _determine_meeting_type(self, title: str) -> str:
        """Determine meeting type from title"""
        title_lower = title.lower()
        if 'sep' in title_lower or 'social and economic' in title_lower:
            return 'Social and Economic Panel'
        elif 'joint' in title_lower:
            return 'Joint SSC Meeting'
        elif 'special' in title_lower:
            return 'Special SSC Meeting'
        else:
            return 'Regular SSC Meeting'

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to full absolute URL"""
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            return f"{self.BASE_URL}{url}"
        else:
            return f"{self.BASE_URL}/{url}"

    def download_document(self, url: str) -> Optional[bytes]:
        """
        Download a document from URL
        Returns bytes of the document
        """
        try:
            logger.info(f"Downloading document from {url}")
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading document from {url}: {e}")
            return None

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> Optional[str]:
        """
        Extract text from PDF bytes
        """
        try:
            import PyPDF2
            from io import BytesIO

            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None

    def parse_recommendations_from_report(self, report_text: str) -> List[Dict]:
        """
        Parse SSC recommendations from report text
        Returns list of recommendation dictionaries
        """
        recommendations = []

        # Look for recommendation sections
        # SSC reports typically have numbered recommendations
        recommendation_pattern = r'(?:Recommendation|Motion)\s+(\d+):\s*([^\n]+(?:\n(?!\s*(?:Recommendation|Motion)\s+\d+)[^\n]+)*)'

        matches = re.finditer(recommendation_pattern, report_text, re.IGNORECASE | re.MULTILINE)

        for match in matches:
            rec_number = match.group(1)
            rec_text = match.group(2).strip()

            recommendation = {
                'recommendation_number': f"REC-{rec_number}",
                'title': f"SSC Recommendation {rec_number}",
                'recommendation_text': rec_text,
                'recommendation_type': self._classify_recommendation(rec_text),
                'species': self._extract_species(rec_text),
                'status': 'pending'
            }

            # Try to extract ABC values
            abc_match = re.search(r'ABC.*?(\d[\d,]+)\s*(lbs?|pounds?|mt|metric\s+tons?)', rec_text, re.IGNORECASE)
            if abc_match:
                recommendation['abc_value'] = float(abc_match.group(1).replace(',', ''))
                recommendation['abc_units'] = abc_match.group(2)

            recommendations.append(recommendation)

        return recommendations

    def _classify_recommendation(self, text: str) -> str:
        """Classify recommendation type based on content"""
        text_lower = text.lower()
        if 'abc' in text_lower or 'acceptable biological catch' in text_lower:
            return 'ABC Recommendation'
        elif 'assessment' in text_lower or 'stock status' in text_lower:
            return 'Stock Assessment'
        elif 'research' in text_lower:
            return 'Research Recommendation'
        elif 'data' in text_lower:
            return 'Data Collection'
        else:
            return 'General Recommendation'

    def _extract_species(self, text: str) -> List[str]:
        """Extract species names from text"""
        # Common SAFMC species
        species_list = [
            'Red Snapper', 'Gag', 'Red Grouper', 'Black Sea Bass', 'Vermilion Snapper',
            'Greater Amberjack', 'Gray Triggerfish', 'King Mackerel', 'Spanish Mackerel',
            'Cobia', 'Dolphin', 'Wahoo', 'Golden Tilefish', 'Blueline Tilefish',
            'Snowy Grouper', 'Yellowtail Snapper', 'Mutton Snapper', 'Hogfish',
            'Wreckfish', 'Scamp', 'Red Porgy', 'Silk Snapper'
        ]

        found_species = []
        text_lower = text.lower()
        for species in species_list:
            if species.lower() in text_lower:
                found_species.append(species)

        return found_species


def test_scraper():
    """Test the SSC meeting scraper"""
    scraper = SSCMeetingScraper()
    meetings = scraper.scrape_all_meetings()

    print(f"\n=== Found {len(meetings)} SSC Meetings ===\n")

    for i, meeting in enumerate(meetings[:5], 1):  # Show first 5
        print(f"{i}. {meeting['title']}")
        print(f"   Type: {meeting['meeting_type']}")
        print(f"   Date: {meeting['meeting_date_start']}")
        print(f"   Location: {meeting['location']}")
        print(f"   Virtual: {meeting['is_virtual']}")
        print(f"   Agenda: {meeting['agenda_url']}")
        print(f"   Briefing Book: {meeting['briefing_book_url']}")
        print(f"   Report: {meeting['report_url']}")
        print()


if __name__ == '__main__':
    test_scraper()
