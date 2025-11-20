"""
Enhanced SEDAR Assessments Scraper
Scrapes stock assessments from sedarweb.org for new SAFE/SEDAR integration
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import re
import time
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class SEDARScraperEnhanced:
    """Enhanced scraper for SEDAR stock assessments"""

    BASE_URL = 'https://sedarweb.org'
    ASSESSMENTS_URL = f'{BASE_URL}/assessments/'
    API_URL = f'{BASE_URL}/wp-json/sedar/v1/filter-projects'

    # Council abbreviations mapping
    COUNCIL_MAP = {
        'SAFMC': 'South Atlantic Fishery Management Council',
        'GMFMC': 'Gulf of Mexico Fishery Management Council',
        'ASMFC': 'Atlantic States Marine Fisheries Commission',
        'CFMC': 'Caribbean Fishery Management Council',
        'HMS': 'Highly Migratory Species',
        'NMFS': 'National Marine Fisheries Service',
        'GSMFC': 'Gulf States Marine Fisheries Commission'
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SAFMC FMP Tracker (aaron.kornbluth@gmail.com)'
        })

    def scrape_all_assessments(self, delay_between_requests: float = 0.5) -> List[Dict]:
        """
        Scrape all SEDAR assessments from sedarweb.org

        Args:
            delay_between_requests: Seconds to wait between requests (be polite)

        Returns:
            List of assessment metadata dictionaries
        """
        logger.info("Starting comprehensive SEDAR assessments scrape...")

        assessments = []

        try:
            # Step 1: Get list of all assessments from main page
            logger.info("Fetching assessments list...")
            assessment_links = self._get_assessment_links()
            logger.info(f"Found {len(assessment_links)} assessment pages")

            # Step 2: Scrape each assessment's detail page
            for idx, (sedar_number, url) in enumerate(assessment_links.items(), 1):
                logger.info(f"[{idx}/{len(assessment_links)}] Scraping {sedar_number}...")

                try:
                    details = self.scrape_assessment_details(url)
                    if details:
                        details['sedar_number'] = sedar_number
                        assessments.append(details)

                    # Be polite - rate limit
                    time.sleep(delay_between_requests)

                except Exception as e:
                    logger.error(f"Error scraping {sedar_number}: {e}")
                    continue

            logger.info(f"Successfully scraped {len(assessments)} SEDAR assessments")
            return assessments

        except Exception as e:
            logger.error(f"Error in scrape_all_assessments: {e}")
            return assessments

    def _get_assessment_links(self) -> Dict[str, str]:
        """
        Get dictionary of SEDAR number -> URL from main assessments page

        Returns:
            Dict mapping SEDAR numbers to URLs
        """
        assessment_links = {}

        try:
            # Try API endpoint first
            try:
                response = self.session.get(self.API_URL, timeout=30)
                if response.ok:
                    data = response.json()
                    if isinstance(data, list):
                        for item in data:
                            sedar_num = self._extract_sedar_number(
                                item.get('title', '') or item.get('name', '')
                            )
                            url = item.get('url') or item.get('link')
                            if sedar_num and url:
                                assessment_links[sedar_num] = url

                        if assessment_links:
                            logger.info(f"Got {len(assessment_links)} assessments from API")
                            return assessment_links
            except Exception as e:
                logger.warning(f"API request failed: {e}, falling back to HTML scraping")

            # Fallback to HTML scraping
            response = self.session.get(self.ASSESSMENTS_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all assessment links
            # Pattern 1: Direct links with "sedar-" in href
            links = soup.find_all('a', href=re.compile(r'/assessments/sedar-', re.IGNORECASE))

            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)

                sedar_num = self._extract_sedar_number(href + ' ' + text)
                if sedar_num:
                    full_url = urljoin(self.BASE_URL, href)
                    if sedar_num not in assessment_links:
                        assessment_links[sedar_num] = full_url

            # Pattern 2: Quick links (just numbers)
            quick_links = soup.find_all('a', string=re.compile(r'^\d+$'))
            for link in quick_links:
                number = link.get_text(strip=True).zfill(2)  # Pad with zero
                href = link.get('href')

                if href and 'sedar' in href.lower():
                    sedar_num = f"SEDAR {number}"
                    full_url = urljoin(self.BASE_URL, href)

                    if sedar_num not in assessment_links:
                        assessment_links[sedar_num] = full_url

            logger.info(f"Got {len(assessment_links)} assessments from HTML")
            return assessment_links

        except Exception as e:
            logger.error(f"Error getting assessment links: {e}")
            return assessment_links

    def scrape_assessment_details(self, sedar_url: str) -> Dict:
        """
        Scrape detailed information from individual SEDAR assessment page

        Args:
            sedar_url: URL to specific SEDAR assessment page

        Returns:
            Dictionary with detailed assessment information
        """
        try:
            response = self.session.get(sedar_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            details = {
                'sedar_url': sedar_url,
                'last_scraped': datetime.now().isoformat()
            }

            # Extract full title
            title_elem = soup.find('h1', class_='entry-title') or soup.find('h1') or soup.find('title')
            if title_elem:
                details['full_title'] = title_elem.get_text(strip=True)

            # Extract species name
            species = self._extract_species(soup, details.get('full_title', ''))
            if species:
                details['species_name'] = species['common_name']
                if species.get('scientific_name'):
                    details['scientific_name'] = species['scientific_name']

            # Extract council/cooperator
            council = self._extract_council(soup, details.get('full_title', ''))
            if council:
                details['council'] = council

            # Extract stock area
            stock_area = self._extract_stock_area(soup, details.get('full_title', ''))
            if stock_area:
                details['stock_area'] = stock_area

            # Extract assessment type
            assessment_type = self._extract_assessment_type(soup, details.get('full_title', ''))
            if assessment_type:
                details['assessment_type'] = assessment_type

            # Extract dates
            dates = self._extract_dates(soup)
            details.update(dates)

            # Extract status
            status = self._extract_status(soup, details)
            if status:
                details['assessment_status'] = status

            # Extract document links
            documents = self._extract_document_links(soup)
            details.update(documents)

            # Extract text content for AI analysis
            content = self._extract_content(soup)
            details.update(content)

            # Determine FMP
            fmp = self._determine_fmp(species.get('common_name', ''))
            if fmp:
                details['fmp'] = fmp

            return details

        except Exception as e:
            logger.error(f"Error scraping assessment details from {sedar_url}: {e}")
            return {'sedar_url': sedar_url, 'error': str(e)}

    def _extract_sedar_number(self, text: str) -> Optional[str]:
        """Extract SEDAR number from text"""
        # Patterns: "SEDAR 80", "SEDAR-80", "sedar80"
        match = re.search(r'SEDAR[- ]?(\d+)', text, re.IGNORECASE)
        if match:
            num = match.group(1).zfill(2)  # Pad with zero if needed
            return f"SEDAR {num}"
        return None

    def _extract_species(self, soup: BeautifulSoup, title: str) -> Dict:
        """Extract species name (common and scientific) from page"""
        species = {}

        # Pattern 1: From title - "SEDAR XX Species Name"
        # Remove SEDAR number first
        clean_title = re.sub(r'SEDAR[- ]?\d+:?\s*', '', title, flags=re.IGNORECASE)
        clean_title = re.sub(r'(SAFMC|GMFMC|ASMFC|CFMC|HMS)\s*', '', clean_title, flags=re.IGNORECASE)

        # Extract common name (usually first part before parenthesis or " Stock")
        common_match = re.search(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', clean_title)
        if common_match:
            common_name = common_match.group(1).strip()
            # Clean up
            common_name = re.sub(r'\s+(Stock|Assessment|Update|Benchmark|and).*', '', common_name)
            species['common_name'] = common_name

        # Extract scientific name (usually in parentheses or italics)
        scientific_match = re.search(r'\(([A-Z][a-z]+\s+[a-z]+)\)', title)
        if scientific_match:
            species['scientific_name'] = scientific_match.group(1)

        # Pattern 2: Look in page content
        if not species.get('common_name'):
            species_text = soup.find(string=re.compile(r'Species:', re.IGNORECASE))
            if species_text:
                parent = species_text.parent
                if parent:
                    species_str = parent.get_text(strip=True).replace('Species:', '').strip()
                    if species_str:
                        species['common_name'] = species_str

        return species

    def _extract_council(self, soup: BeautifulSoup, title: str) -> Optional[str]:
        """Extract cooperating council/organization"""
        page_text = soup.get_text() + ' ' + title

        for abbrev in self.COUNCIL_MAP.keys():
            if abbrev in page_text:
                return abbrev

        return None

    def _extract_stock_area(self, soup: BeautifulSoup, title: str) -> Optional[str]:
        """Extract stock geographic area"""
        areas = {
            'South Atlantic': ['South Atlantic', 'SA ', 'SAFMC'],
            'Gulf of Mexico': ['Gulf of Mexico', 'GOM', 'GMFMC'],
            'Atlantic-wide': ['Atlantic-wide', 'Atlantic Coast', 'ASMFC'],
            'Caribbean': ['Caribbean', 'CFMC']
        }

        page_text = (soup.get_text() + ' ' + title).lower()

        for area_name, keywords in areas.items():
            if any(keyword.lower() in page_text for keyword in keywords):
                return area_name

        return None

    def _extract_assessment_type(self, soup: BeautifulSoup, title: str) -> str:
        """Extract assessment type"""
        page_text = soup.get_text() + ' ' + title

        type_keywords = [
            ('Benchmark', ['Benchmark']),
            ('Update', ['Update', 'Updated']),
            ('Operational', ['Operational']),
            ('Research Track', ['Research Track']),
        ]

        for type_name, keywords in type_keywords:
            if any(keyword in page_text for keyword in keywords):
                return type_name

        return 'Standard'

    def _extract_dates(self, soup: BeautifulSoup) -> Dict:
        """Extract key dates from assessment page"""
        dates = {}
        page_text = soup.get_text()

        # Date patterns
        date_patterns = {
            'kickoff_date': r'(?:Kickoff|Start|Initiated)[:\s]+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
            'data_workshop_date': r'(?:Data Workshop)[:\s]+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
            'assessment_workshop_date': r'(?:Assessment Workshop)[:\s]+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
            'review_workshop_date': r'(?:Review Workshop)[:\s]+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
            'completion_date': r'(?:Complet|Finish)[ed:\s]+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
        }

        for field, pattern in date_patterns.items():
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                parsed = self._parse_date(date_str)
                if parsed:
                    dates[field] = parsed

        return dates

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        formats = ['%B %d, %Y', '%B %d %Y', '%b %d, %Y', '%b %d %Y']

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt).date()
                return parsed.isoformat()
            except:
                continue

        return None

    def _extract_status(self, soup: BeautifulSoup, details: Dict) -> str:
        """Determine assessment status"""
        page_text = soup.get_text().lower()

        # Completed if final report exists or completion date set
        if details.get('completion_date') or details.get('final_report_url'):
            return 'Completed'

        # Check for status keywords
        if any(word in page_text for word in ['completed', 'final', 'finished']):
            return 'Completed'

        if any(word in page_text for word in ['in progress', 'ongoing', 'underway']):
            return 'In Progress'

        if any(word in page_text for word in ['scheduled', 'upcoming', 'planned']):
            return 'Scheduled'

        if any(word in page_text for word in ['on hold', 'suspended', 'postponed']):
            return 'On Hold'

        return 'Unknown'

    def _extract_document_links(self, soup: BeautifulSoup) -> Dict:
        """Extract links to assessment documents"""
        documents = {}

        links = soup.find_all('a', href=True)

        doc_patterns = {
            'final_report_url': ['Final Report', 'Stock Assessment Report', 'SAR'],
            'executive_summary_url': ['Executive Summary', 'Summary Report', 'Summary'],
            'data_report_url': ['Data Report', 'Data Workshop Report'],
        }

        for field, keywords in doc_patterns.items():
            for link in links:
                link_text = link.get_text(strip=True)
                if any(keyword.lower() in link_text.lower() for keyword in keywords):
                    href = link.get('href')
                    # Prefer PDF links
                    if '.pdf' in href.lower():
                        documents[field] = urljoin(self.BASE_URL, href)
                        break
                    elif not documents.get(field):  # Fallback to non-PDF
                        documents[field] = urljoin(self.BASE_URL, href)

        return documents

    def _extract_content(self, soup: BeautifulSoup) -> Dict:
        """Extract text content for AI analysis"""
        content = {}

        # Find main content area
        main_content = soup.find('div', class_='entry-content') or \
                      soup.find('main') or \
                      soup.find('article')

        if main_content:
            # Get all paragraphs
            paragraphs = main_content.find_all('p')
            full_text = ' '.join(p.get_text(strip=True) for p in paragraphs)

            # Store first 3000 characters for AI analysis
            if full_text:
                content['page_content'] = full_text[:3000]

        return content

    def _determine_fmp(self, species_name: str) -> Optional[str]:
        """Determine which FMP a species belongs to"""
        if not species_name:
            return None

        species_lower = species_name.lower()

        # FMP species mappings
        fmp_species = {
            'Snapper Grouper': [
                'snapper', 'grouper', 'hogfish', 'tilefish', 'triggerfish',
                'grunt', 'porgy', 'sea bass', 'bass', 'jack', 'amberjack',
                'blueline', 'vermilion', 'red porgy', 'golden tilefish'
            ],
            'Coastal Migratory Pelagics': [
                'mackerel', 'cobia', 'king mackerel', 'spanish mackerel'
            ],
            'Dolphin Wahoo': [
                'dolphin', 'wahoo', 'mahi', 'dorado'
            ],
            'Shrimp': [
                'shrimp', 'penaeid'
            ],
            'Spiny Lobster': [
                'lobster', 'spiny lobster'
            ],
            'Golden Crab': [
                'golden crab', 'crab'
            ]
        }

        for fmp, keywords in fmp_species.items():
            if any(keyword in species_lower for keyword in keywords):
                return fmp

        return None

    def get_safmc_assessments_only(self) -> List[Dict]:
        """Get only SAFMC-related assessments"""
        all_assessments = self.scrape_all_assessments()
        safmc_assessments = [
            a for a in all_assessments
            if a.get('council') == 'SAFMC' or a.get('stock_area') == 'South Atlantic'
        ]
        logger.info(f"Filtered to {len(safmc_assessments)} SAFMC assessments")
        return safmc_assessments


def main():
    """Test the enhanced SEDAR scraper"""
    logging.basicConfig(level=logging.INFO)

    scraper = SEDARScraperEnhanced()

    print("Testing Enhanced SEDAR Scraper...")
    print("=" * 60)

    # Test 1: Get assessment links
    print("\n1. Getting assessment links...")
    links = scraper._get_assessment_links()
    print(f"   Found {len(links)} assessments")
    if links:
        print(f"   Sample: {list(links.keys())[:5]}")

    # Test 2: Scrape details for one assessment
    if links:
        test_sedar, test_url = list(links.items())[0]
        print(f"\n2. Scraping details for {test_sedar}...")
        details = scraper.scrape_assessment_details(test_url)
        print(f"   Species: {details.get('species_name')}")
        print(f"   Status: {details.get('assessment_status')}")
        print(f"   Council: {details.get('council')}")
        print(f"   FMP: {details.get('fmp')}")

    # Test 3: Get SAFMC assessments only
    print("\n3. Testing SAFMC filter...")
    print("   (This will take a while - scraping all assessments)")
    print("   Skipping in test mode. Use scraper.get_safmc_assessments_only() in production.")


if __name__ == '__main__':
    main()
