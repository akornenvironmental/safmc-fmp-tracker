"""
SAFMC Amendments Scraper
Scrapes amendment data from SAFMC website
"""

import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class AmendmentsScraper:
    """Scraper for SAFMC amendments and regulatory actions"""

    AMENDMENTS_URL = 'https://safmc.net/fishery-management/amendments-under-development/'

    FMP_PAGES = {
        'Snapper Grouper': 'https://safmc.net/fishery-management-plans/snapper-grouper/',
        'Coastal Migratory Pelagics': 'https://safmc.net/fishery-management-plans/coastal-migratory-pelagics/',
        'Dolphin Wahoo': 'https://safmc.net/fishery-management-plans/dolphin-wahoo/',
        'Golden Crab': 'https://safmc.net/fishery-management-plans/golden-crab/',
        'Sargassum': 'https://safmc.net/fishery-management-plans/sargassum/',
        'Shrimp': 'https://safmc.net/fishery-management-plans/shrimp/',
        'Spiny Lobster': 'https://safmc.net/fishery-management-plans/spiny-lobster/',
        'Coral': 'https://safmc.net/fishery-management-plans/coral/'
    }

    PROGRESS_STAGES = {
        'pre-scoping': 10,
        'scoping': 25,
        'public hearing': 45,
        'final approval': 65,
        'secretarial review': 75,
        'rule making': 85,
        'implementation': 95,
        'implemented': 100
    }

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SAFMC-FMP-Tracker/1.0'
        })

    def scrape_all(self) -> Dict:
        """Scrape all amendment data"""
        results = {
            'amendments': [],
            'total_found': 0,
            'errors': []
        }

        try:
            # Scrape main amendments page
            amendments = self.scrape_amendments_page()
            results['amendments'].extend(amendments)
            results['total_found'] += len(amendments)

            # Scrape individual FMP pages
            for fmp_name, url in self.FMP_PAGES.items():
                try:
                    fmp_amendments = self.scrape_fmp_page(fmp_name, url)
                    results['amendments'].extend(fmp_amendments)
                    results['total_found'] += len(fmp_amendments)
                except Exception as e:
                    logger.error(f"Error scraping {fmp_name}: {e}")
                    results['errors'].append(f"{fmp_name}: {str(e)}")

        except Exception as e:
            logger.error(f"Error in scrape_all: {e}")
            results['errors'].append(str(e))

        return results

    def scrape_amendments_page(self) -> List[Dict]:
        """Scrape the main amendments under development page"""
        amendments = []

        try:
            response = self.session.get(self.AMENDMENTS_URL, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Strategy 1: Find headings with amendment text
            for heading in soup.find_all(['h2', 'h3', 'h4']):
                amendment = self._parse_amendment_from_heading(heading)
                if amendment and not self._is_duplicate(amendment, amendments):
                    amendments.append(amendment)

            # Strategy 2: Find list items with amendment text
            for li in soup.find_all('li'):
                text = li.get_text(strip=True)
                if self._is_amendment_text(text):
                    amendment = self._parse_amendment_from_text(text, li)
                    if amendment and not self._is_duplicate(amendment, amendments):
                        amendments.append(amendment)

            logger.info(f"Found {len(amendments)} amendments from main page")

        except requests.RequestException as e:
            logger.error(f"Error fetching amendments page: {e}")
            raise

        return amendments

    def scrape_fmp_page(self, fmp_name: str, url: str) -> List[Dict]:
        """Scrape an individual FMP page"""
        amendments = []

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Look for amendment patterns
            pattern = re.compile(r'(?:Amendment|Framework|Regulatory\s+Amendment)\s+\d+', re.IGNORECASE)

            for element in soup.find_all(text=pattern):
                amendment = self._parse_amendment_from_text(element.strip(), element.parent, fmp_name)
                if amendment and not self._is_duplicate(amendment, amendments):
                    amendments.append(amendment)

            logger.info(f"Found {len(amendments)} amendments from {fmp_name} page")

        except requests.RequestException as e:
            logger.error(f"Error fetching {fmp_name} page: {e}")

        return amendments

    def _parse_amendment_from_heading(self, heading) -> Optional[Dict]:
        """Parse amendment data from a heading element"""
        text = heading.get_text(strip=True)

        if not self._is_amendment_text(text):
            return None

        # Get surrounding content for additional details
        content = self._get_surrounding_content(heading)

        # Try to find source URL from links in or near the heading
        source_url = self._extract_source_url(heading)

        return self._create_amendment_object(text, content, source_url)

    def _parse_amendment_from_text(self, text: str, element, fmp_override: str = None) -> Optional[Dict]:
        """Parse amendment data from text"""
        if not self._is_amendment_text(text):
            return None

        content = self._get_surrounding_content(element)

        # Try to find source URL from links in or near the element
        source_url = self._extract_source_url(element)

        amendment = self._create_amendment_object(text, content, source_url)
        if fmp_override:
            amendment['fmp'] = fmp_override

        return amendment

    def _create_amendment_object(self, title: str, content: str, source_url: str = None) -> Dict:
        """Create amendment object from title and content"""
        progress_stage = self._extract_progress_stage(content, title)
        progress_percentage = self._calculate_progress_percentage(progress_stage)

        # Extract dates from the amendment page if we have a source URL
        dates = {'published': None, 'modified': None}
        if source_url and source_url != self.AMENDMENTS_URL:
            dates = self._extract_dates_from_page(source_url)

        # Use dateModified as completion_date for implemented amendments
        # For in-progress amendments, completion_date will be None
        completion_date = None
        if progress_percentage >= 100 and dates['modified']:
            # Convert to date (not datetime)
            completion_date = dates['modified'].date()

        return {
            'action_id': self._generate_action_id(title),
            'title': title,
            'type': self._determine_action_type(title),
            'fmp': self._extract_fmp(title, content),
            'progress_stage': progress_stage,
            'progress_percentage': progress_percentage,
            'phase': self._determine_phase(progress_stage),
            'description': self._extract_description(content),
            'lead_staff': self._extract_staff(content),
            'committee': '',  # Will be determined from FMP
            'source_url': source_url or self.AMENDMENTS_URL,
            'documents_found': 0,
            'completion_date': completion_date,
            'start_date': dates['published'].date() if dates['published'] else None,
        }

    def _is_amendment_text(self, text: str) -> bool:
        """Check if text appears to be an amendment title"""
        pattern = r'(?:Amendment|Framework|Regulatory)\s+\d+'
        return bool(re.search(pattern, text, re.IGNORECASE))

    def _is_duplicate(self, amendment: Dict, amendments: List[Dict]) -> bool:
        """Check if amendment is already in list"""
        return any(a['action_id'] == amendment['action_id'] for a in amendments)

    def _get_surrounding_content(self, element, max_length: int = 2000) -> str:
        """Get surrounding content for context"""
        content = []

        # Get next siblings
        for sibling in element.find_next_siblings(limit=5):
            content.append(sibling.get_text(strip=True))

        return ' '.join(content)[:max_length]

    def _generate_action_id(self, title: str) -> str:
        """Generate unique action ID from title"""
        # Extract amendment number
        match = re.search(r'(Amendment|Framework|Regulatory\s+Amendment)\s+(\d+)', title, re.IGNORECASE)

        if match:
            action_type = match.group(1).lower()
            number = match.group(2)

            type_code = 'fw' if 'framework' in action_type else \
                       'reg' if 'regulatory' in action_type else 'am'

            fmp_code = self._extract_fmp_code(title)

            return f"{fmp_code}-{type_code}-{number}".lower()

        # Fallback: use cleaned title
        return re.sub(r'[^a-z0-9]+', '-', title.lower())[:50].strip('-')

    def _extract_fmp_code(self, title: str) -> str:
        """Extract FMP code from title"""
        title_lower = title.lower()

        if 'snapper' in title_lower:
            return 'sg'
        elif 'dolphin' in title_lower:
            return 'dw'
        elif 'coastal' in title_lower or 'migratory' in title_lower:
            return 'cmp'
        elif 'golden' in title_lower:
            return 'gc'
        elif 'coral' in title_lower:
            return 'cor'
        elif 'shrimp' in title_lower:
            return 'shr'
        elif 'spiny' in title_lower or 'lobster' in title_lower:
            return 'sl'
        elif 'sargassum' in title_lower:
            return 'sar'

        return 'unk'

    def _determine_action_type(self, title: str) -> str:
        """Determine action type from title"""
        title_lower = title.lower()

        if 'comprehensive' in title_lower or 'omnibus' in title_lower:
            return 'Comprehensive Amendment'
        elif 'framework' in title_lower:
            return 'Framework'
        elif 'regulatory' in title_lower:
            return 'Regulatory Amendment'
        elif 'emergency' in title_lower:
            return 'Emergency Action'
        else:
            return 'Amendment'

    def _extract_fmp(self, title: str, content: str) -> str:
        """Extract FMP name from title and content - returns first match or Multiple FMPs for comprehensive"""
        combined = (title + ' ' + content).lower()

        fmp_patterns = {
            'Snapper Grouper': r'snapper[\s-]?grouper',
            'Coastal Migratory Pelagics': r'coastal\s+migratory|cmp\s|mackerel',
            'Dolphin Wahoo': r'dolphin[\s-]?wahoo',
            'Golden Crab': r'golden[\s-]?crab',
            'Sargassum': r'sargassum',
            'Shrimp': r'shrimp',
            'Spiny Lobster': r'spiny[\s-]?lobster|lobster',
            'Coral': r'coral'
        }

        # Check if this is a comprehensive/omnibus amendment
        if 'comprehensive' in combined or 'omnibus' in combined:
            # Count how many FMPs are mentioned
            matched_fmps = []
            for fmp, pattern in fmp_patterns.items():
                if re.search(pattern, combined):
                    matched_fmps.append(fmp)

            # If multiple FMPs mentioned, return "Multiple FMPs"
            if len(matched_fmps) > 1:
                return 'Multiple FMPs'
            elif len(matched_fmps) == 1:
                return matched_fmps[0]

        # For non-comprehensive amendments, return first match
        for fmp, pattern in fmp_patterns.items():
            if re.search(pattern, combined):
                return fmp

        return 'Unknown FMP'

    def _extract_progress_stage(self, content: str, title: str) -> str:
        """Extract current progress stage"""
        content_lower = content.lower()

        # Check for specific stage mentions
        if 'implementation' in content_lower or 'implemented' in content_lower:
            return 'Implementation'
        if 'rule making' in content_lower or 'rulemaking' in content_lower:
            return 'Rule Making'
        if 'secretarial review' in content_lower or 'nmfs review' in content_lower:
            return 'Secretarial Review'
        if 'final approval' in content_lower or 'final action' in content_lower:
            return 'Final Approval'
        if 'public hearing' in content_lower:
            return 'Public Hearing'
        if 'scoping' in content_lower and 'pre' not in content_lower:
            return 'Scoping'
        if 'pre-scoping' in content_lower:
            return 'Pre-Scoping'

        return 'Scoping'  # Default

    def _extract_description(self, content: str) -> str:
        """Extract description from content"""
        # Get first few sentences
        sentences = re.split(r'[.!?]+', content)
        descriptive = [s.strip() for s in sentences if len(s.strip()) > 50]

        return '. '.join(descriptive[:2])[:500] if descriptive else content[:500]

    def _extract_staff(self, content: str) -> str:
        """Extract lead staff name from content"""
        # Common SAFMC staff names
        staff_names = [
            'John Hadley', 'Mike Schmidtke', 'Chip Collier',
            'Christina Wiegand', 'Roger Pugliese', 'Allie Iberle',
            'Myra Brouwer', 'Julia Byrd', 'Cindy Chaya', 'Cameron Rhodes'
        ]

        for name in staff_names:
            if name in content:
                return name

        # Look for "Staff:" pattern
        match = re.search(r'(?:Staff|Contact|Lead):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)', content)
        if match:
            return match.group(1)

        return ''

    def _extract_source_url(self, element) -> Optional[str]:
        """Extract source URL from element or nearby links"""
        # Check if element itself is a link
        if element.name == 'a' and element.get('href'):
            return element.get('href')

        # Check for links within element
        link = element.find('a', href=True)
        if link:
            return link.get('href')

        # Check parent elements
        parent = element.parent
        if parent:
            link = parent.find('a', href=True)
            if link:
                return link.get('href')

        # Check next siblings for links
        for sibling in element.find_next_siblings(limit=3):
            link = sibling.find('a', href=True) if hasattr(sibling, 'find') else None
            if link:
                return link.get('href')

        return None

    def _extract_dates_from_page(self, url: str) -> Dict[str, Optional[datetime]]:
        """
        Extract dates from amendment page JSON-LD metadata

        Returns dict with 'published', 'modified' keys (datetime objects or None)
        """
        dates = {'published': None, 'modified': None}

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')

            # Find JSON-LD structured data
            json_scripts = soup.find_all('script', type='application/ld+json')

            for script in json_scripts:
                try:
                    data = json.loads(script.string)

                    # Navigate through the JSON structure to find dates
                    if isinstance(data, dict) and '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict) and item.get('@type') == 'WebPage':
                                # Extract datePublished
                                if 'datePublished' in item:
                                    dates['published'] = date_parser.parse(item['datePublished'])

                                # Extract dateModified
                                if 'dateModified' in item:
                                    dates['modified'] = date_parser.parse(item['dateModified'])

                                # We found the WebPage, can break
                                if dates['published'] or dates['modified']:
                                    break

                except json.JSONDecodeError:
                    continue

        except Exception as e:
            logger.debug(f"Could not extract dates from {url}: {e}")

        return dates

    def _calculate_progress_percentage(self, stage: str) -> int:
        """
        Calculate progress percentage from stage

        Note: 'Implementation' stage means the rule has been finalized and is being
        implemented (or already implemented), so we consider it 100% complete.
        """
        if not stage:
            return 0

        stage_lower = stage.lower()

        # Check for completion indicators first (100%)
        if any(keyword in stage_lower for keyword in ['implemented', 'completed', 'implementation']):
            return 100

        # Check against known stages (these are for in-progress stages)
        for stage_key, percentage in self.PROGRESS_STAGES.items():
            if stage_key == 'implementation' or stage_key == 'implemented':
                continue  # Skip these, already handled above
            if stage_key in stage_lower:
                return percentage

        # Default based on common patterns (fallback if not in PROGRESS_STAGES)
        if 'rule making' in stage_lower or 'rulemaking' in stage_lower:
            return 85
        if 'review' in stage_lower:
            return 75
        if 'approval' in stage_lower:
            return 65
        if 'hearing' in stage_lower:
            return 45
        if 'scoping' in stage_lower:
            return 25

        return 0

    def _determine_phase(self, stage: str) -> str:
        """Determine phase from progress stage"""
        if not stage:
            return 'Development'

        stage_lower = stage.lower()

        if 'implement' in stage_lower:
            return 'Implementation'
        if 'rule' in stage_lower or 'secretarial' in stage_lower:
            return 'Federal Review'
        if 'approval' in stage_lower or 'hearing' in stage_lower:
            return 'Review'

        return 'Development'
