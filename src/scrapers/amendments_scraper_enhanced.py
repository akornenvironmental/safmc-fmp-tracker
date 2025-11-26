"""
Enhanced SAFMC Amendments Scraper
Comprehensive scraping with historical data, timelines, documents, and metadata extraction
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import time

logger = logging.getLogger(__name__)

class EnhancedAmendmentsScraper:
    """
    Enhanced scraper for comprehensive SAFMC amendment data
    Features:
    - Historical amendment scraping (2018-present)
    - Individual amendment page scraping for detailed metadata
    - Timeline/milestone extraction
    - Document discovery and cataloging
    - Federal Register number extraction (when available)
    - Staff/contact information extraction
    """

    BASE_URL = 'https://safmc.net'
    AMENDMENTS_URL = f'{BASE_URL}/fishery-management/amendments-under-development/'

    # Amendment detail page URL pattern
    AMENDMENT_PAGE_PATTERN = f'{BASE_URL}/amendments/{{amendment_slug}}/'

    FMP_PAGES = {
        'Snapper Grouper': f'{BASE_URL}/fishery-management-plans/snapper-grouper/',
        'Coastal Migratory Pelagics': f'{BASE_URL}/fishery-management-plans/coastal-migratory-pelagics/',
        'Dolphin Wahoo': f'{BASE_URL}/fishery-management-plans/dolphin-wahoo/',
        'Golden Crab': f'{BASE_URL}/fishery-management-plans/golden-crab/',
        'Sargassum': f'{BASE_URL}/fishery-management-plans/sargassum/',
        'Shrimp': f'{BASE_URL}/fishery-management-plans/shrimp/',
        'Spiny Lobster': f'{BASE_URL}/fishery-management-plans/spiny-lobster/',
        'Coral': f'{BASE_URL}/fishery-management-plans/coral/'
    }

    PROGRESS_STAGES = {
        'pre-scoping': 5,
        'scoping': 20,
        'public hearing': 45,
        'council review': 55,
        'final approval': 65,
        'secretarial review': 75,
        'federal register': 80,
        'rule making': 85,
        'final rule': 90,
        'implementation': 95,
        'implemented': 100
    }

    def __init__(self, timeout=30, rate_limit=1.0):
        """
        Initialize scraper
        Args:
            timeout: Request timeout in seconds
            rate_limit: Minimum seconds between requests (respectful scraping)
        """
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SAFMC-FMP-Tracker/2.0 (Enhanced Amendment Scraper)'
        })

    def _rate_limit_wait(self):
        """Ensure respectful scraping with rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def scrape_all_comprehensive(self) -> Dict:
        """
        Comprehensive scrape of all amendment data including historical
        Returns: Dict with amendments, documents, milestones, errors
        """
        results = {
            'amendments': [],
            'documents': [],
            'milestones': [],
            'total_found': 0,
            'errors': [],
            'metadata': {
                'scrape_date': datetime.utcnow().isoformat(),
                'sources_scraped': []
            }
        }

        try:
            # 1. Scrape main amendments page (under development)
            logger.info("Scraping main amendments page...")
            amendments_under_dev = self.scrape_amendments_page()
            # Mark these with appropriate status based on their stage
            for amend in amendments_under_dev:
                amend['status'] = self._determine_status(amend.get('progress_stage', ''))
            results['amendments'].extend(amendments_under_dev)
            results['metadata']['sources_scraped'].append('amendments-under-development')

            # Track titles of amendments under development for matching
            under_dev_titles = {self._normalize_title(a.get('title', '')) for a in amendments_under_dev if a.get('title')}

            # 2. Scrape each FMP page for current and completed amendments
            for fmp_name, url in self.FMP_PAGES.items():
                try:
                    logger.info(f"Scraping {fmp_name} FMP page...")
                    self._rate_limit_wait()
                    fmp_data = self.scrape_fmp_page_comprehensive(fmp_name, url)
                    # Mark amendments from FMP pages with appropriate status
                    for amend in fmp_data['amendments']:
                        normalized_title = self._normalize_title(amend.get('title', ''))
                        if normalized_title in under_dev_titles:
                            amend['status'] = self._determine_status(amend.get('progress_stage', ''))
                        else:
                            amend['status'] = None  # Completed/historical amendments
                    results['amendments'].extend(fmp_data['amendments'])
                    results['documents'].extend(fmp_data['documents'])
                    results['metadata']['sources_scraped'].append(fmp_name)
                except Exception as e:
                    logger.error(f"Error scraping {fmp_name}: {e}")
                    results['errors'].append(f"{fmp_name}: {str(e)}")

            # 3. For each amendment, scrape individual detail page
            logger.info("Scraping individual amendment detail pages...")
            for amendment in results['amendments']:
                try:
                    detail_url = self._construct_amendment_url(amendment)
                    if detail_url:
                        self._rate_limit_wait()
                        details = self.scrape_amendment_detail_page(detail_url)
                        if details:
                            # Merge details into amendment
                            amendment.update(details)
                            if details.get('milestones'):
                                results['milestones'].extend(details['milestones'])
                            if details.get('documents'):
                                results['documents'].extend(details['documents'])
                except Exception as e:
                    logger.error(f"Error scraping detail page for {amendment.get('title')}: {e}")

            # 4. Deduplicate
            results['amendments'] = self._deduplicate_amendments(results['amendments'])
            results['total_found'] = len(results['amendments'])

            logger.info(f"Comprehensive scrape complete: {results['total_found']} amendments, "
                       f"{len(results['documents'])} documents, {len(results['milestones'])} milestones")

        except Exception as e:
            logger.error(f"Error in comprehensive scrape: {e}")
            results['errors'].append(str(e))

        return results

    def scrape_amendments_page(self) -> List[Dict]:
        """Scrape the main amendments under development page"""
        amendments = []

        try:
            self._rate_limit_wait()
            response = self.session.get(self.AMENDMENTS_URL, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Find amendment listings
            for element in soup.find_all(['h2', 'h3', 'h4', 'li']):
                text = element.get_text(strip=True)
                if self._is_amendment_text(text):
                    amendment = self._parse_amendment_basic(text, element)
                    if amendment and not self._is_duplicate_in_list(amendment, amendments):
                        amendments.append(amendment)

            logger.info(f"Found {len(amendments)} amendments from main page")

        except requests.RequestException as e:
            logger.error(f"Error fetching amendments page: {e}")
            raise

        return amendments

    def scrape_fmp_page_comprehensive(self, fmp_name: str, url: str) -> Dict:
        """
        Comprehensive scrape of individual FMP page
        Extracts both under development AND completed amendments
        """
        result = {
            'amendments': [],
            'documents': []
        }

        try:
            self._rate_limit_wait()
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Strategy 1: Find section headings for "Amendments Under Development" and "Completed Amendments"
            sections = soup.find_all(['h2', 'h3'], string=re.compile(r'amendments?\s+under\s+development|completed\s+amendments?', re.IGNORECASE))

            for section_header in sections:
                section_type = 'Under Development' if 'under development' in section_header.get_text().lower() else 'Completed'

                # Get all content until next major heading
                amendments_in_section = self._extract_amendments_from_section(section_header, fmp_name, section_type)
                result['amendments'].extend(amendments_in_section)

            # Strategy 2: General amendment pattern matching across entire page
            pattern = re.compile(r'(?:Amendment|Framework|Regulatory\s+Amendment)\s+\d+', re.IGNORECASE)
            for element in soup.find_all(text=pattern):
                amendment = self._parse_amendment_basic(element.strip(), element.parent, fmp_name)
                if amendment and not self._is_duplicate_in_list(amendment, result['amendments']):
                    result['amendments'].append(amendment)

            # Extract documents
            result['documents'] = self._extract_documents_from_page(soup, fmp_name)

            logger.info(f"Found {len(result['amendments'])} amendments and {len(result['documents'])} documents from {fmp_name} page")

        except requests.RequestException as e:
            logger.error(f"Error fetching {fmp_name} page: {e}")
            raise

        return result

    def scrape_amendment_detail_page(self, url: str) -> Optional[Dict]:
        """
        Scrape individual amendment detail page for comprehensive metadata
        Returns: Dict with timeline, documents, staff, status, dates
        """
        try:
            self._rate_limit_wait()
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            details = {
                'detail_url': url,
                'milestones': [],
                'documents': [],
                'staff_contact': {},
                'dates': {},
                'federal_register': None,
                'detailed_description': ''
            }

            # Extract timeline/milestones
            details['milestones'] = self._extract_timeline(soup)

            # Extract documents
            details['documents'] = self._extract_documents_from_page(soup)

            # Extract staff information
            details['staff_contact'] = self._extract_staff_info(soup)

            # Extract key dates
            details['dates'] = self._extract_dates(soup)

            # Extract detailed description
            details['detailed_description'] = self._extract_detailed_description(soup)

            # Look for Federal Register numbers
            details['federal_register'] = self._extract_federal_register(soup)

            # Extract current status
            details['current_status'] = self._extract_status(soup)

            return details

        except requests.RequestException as e:
            logger.error(f"Error fetching detail page {url}: {e}")
            return None

    def _extract_amendments_from_section(self, section_header, fmp_name: str, section_type: str) -> List[Dict]:
        """Extract amendments from a specific section (Under Development or Completed)"""
        amendments = []

        # Get next siblings until we hit another major heading
        current = section_header.find_next_sibling()
        while current and current.name not in ['h2', 'h3']:
            text = current.get_text(strip=True)
            if self._is_amendment_text(text):
                amendment = self._parse_amendment_basic(text, current, fmp_name)
                if amendment:
                    amendment['section_type'] = section_type
                    if section_type == 'Completed':
                        amendment['progress_stage'] = 'Implemented'
                        amendment['progress_percentage'] = 100
                    amendments.append(amendment)
            current = current.find_next_sibling()

        return amendments

    def _extract_timeline(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract timeline/milestone information from amendment page"""
        milestones = []

        # Look for timeline sections
        timeline_sections = soup.find_all(text=re.compile(r'timeline|milestone|schedule|history', re.IGNORECASE))

        for section in timeline_sections:
            parent = section.parent if hasattr(section, 'parent') else None
            if not parent:
                continue

            # Look for dates and descriptions in nearby content
            content = parent.find_next_siblings(limit=10)
            for element in content:
                # Parse date patterns
                text = element.get_text()
                date_matches = re.finditer(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', text)

                for match in date_matches:
                    date_str = match.group()
                    # Get surrounding context
                    context = text[max(0, match.start()-50):min(len(text), match.end()+100)]

                    milestones.append({
                        'date_text': date_str,
                        'description': context.strip(),
                        'parsed_date': self._parse_date(date_str)
                    })

        return milestones

    def _extract_documents_from_page(self, soup: BeautifulSoup, fmp_name: str = None) -> List[Dict]:
        """Extract document links from page"""
        documents = []

        # Find all PDF links
        for link in soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE)):
            href = link.get('href')
            title = link.get_text(strip=True) or link.get('title', '')

            # Make URL absolute
            if href.startswith('/'):
                href = self.BASE_URL + href
            elif not href.startswith('http'):
                href = self.BASE_URL + '/' + href

            doc_type = self._classify_document_type(title)

            documents.append({
                'title': title,
                'url': href,
                'type': doc_type,
                'fmp': fmp_name
            })

        return documents

    def _extract_staff_info(self, soup: BeautifulSoup) -> Dict:
        """Extract staff contact information"""
        staff_info = {
            'name': '',
            'title': '',
            'email': '',
            'phone': ''
        }

        # Look for staff/contact sections
        staff_patterns = [
            r'staff\s+contact',
            r'lead\s+staff',
            r'fishery\s+(?:social\s+)?scientist',
            r'contact\s+(?:person|information)'
        ]

        for pattern in staff_patterns:
            section = soup.find(text=re.compile(pattern, re.IGNORECASE))
            if section:
                parent = section.parent if hasattr(section, 'parent') else None
                if parent:
                    # Extract name
                    name_match = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)', parent.get_text())
                    if name_match:
                        staff_info['name'] = name_match.group(1)

                    # Extract email
                    email_link = parent.find('a', href=re.compile(r'mailto:'))
                    if email_link:
                        staff_info['email'] = email_link.get('href').replace('mailto:', '')

                    break

        return staff_info

    def _extract_dates(self, soup: BeautifulSoup) -> Dict:
        """Extract key dates from amendment page"""
        dates = {}

        date_types = {
            'scoping': r'scoping.*?(\w+\s+\d{4})',
            'public_hearing': r'public\s+hearing.*?(\w+\s+\d{4})',
            'submission': r'submitted?.*?(\w+\s+\d{4})',
            'approval': r'approved?.*?(\w+\s+\d{4})',
            'implementation': r'implemented?.*?(\w+\s+\d{4})'
        }

        page_text = soup.get_text()
        for date_type, pattern in date_types.items():
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                dates[date_type] = self._parse_date(match.group(1))

        return dates

    def _extract_detailed_description(self, soup: BeautifulSoup) -> str:
        """Extract detailed amendment description"""
        # Look for main content area
        content_div = soup.find('div', class_=re.compile(r'entry-content|post-content|content'))
        if content_div:
            paragraphs = content_div.find_all('p', limit=5)
            text = ' '.join([p.get_text(strip=True) for p in paragraphs])
            return text[:1000]  # Limit to 1000 chars
        return ''

    def _extract_federal_register(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract Federal Register number or citation"""
        page_text = soup.get_text()

        # Pattern for Federal Register citations
        fr_patterns = [
            r'(\d+\s+FR\s+\d+)',  # e.g., "88 FR 12345"
            r'Federal\s+Register.*?(\d+\s+FR\s+\d+)',
            r'Docket\s+(?:No\.|Number):\s+([A-Z]+-[A-Z]+-\d{4}-\d{4})'
        ]

        for pattern in fr_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_status(self, soup: BeautifulSoup) -> str:
        """Extract current status from page"""
        page_text = soup.get_text().lower()

        # Check for status indicators
        if 'implemented' in page_text:
            return 'Implemented'
        if 'submitted' in page_text or 'secretarial review' in page_text:
            return 'Secretarial Review'
        if 'public hearing' in page_text:
            return 'Public Hearing'
        if 'scoping' in page_text:
            return 'Scoping'

        return 'Under Development'

    def _classify_document_type(self, title: str) -> str:
        """Classify document type based on title"""
        title_lower = title.lower()

        if 'scoping' in title_lower:
            return 'Scoping Document'
        elif 'draft' in title_lower:
            return 'Draft Amendment'
        elif 'final' in title_lower:
            return 'Final Amendment'
        elif 'environmental' in title_lower or 'ea' in title_lower:
            return 'Environmental Assessment'
        elif 'decision' in title_lower:
            return 'Decision Document'
        elif 'regulatory' in title_lower:
            return 'Regulatory Document'
        else:
            return 'Amendment Document'

    def _parse_amendment_basic(self, text: str, element, fmp_override: str = None) -> Optional[Dict]:
        """Parse basic amendment information from text and element"""
        if not self._is_amendment_text(text):
            return None

        # Extract content for context
        content = self._get_element_content(element)

        amendment = {
            'action_id': self._generate_action_id(text),
            'title': text.strip(),
            'type': self._determine_action_type(text),
            'fmp': fmp_override or self._extract_fmp(text, content),
            'progress_stage': self._extract_progress_stage(content, text),
            'description': self._extract_brief_description(content),
            'lead_staff': self._extract_staff_name(content),
            'source_url': self._extract_element_url(element),
            'scraped_date': datetime.utcnow().isoformat()
        }

        # Calculate progress percentage
        amendment['progress_percentage'] = self._calculate_progress_percentage(amendment['progress_stage'])

        return amendment

    def _construct_amendment_url(self, amendment: Dict) -> Optional[str]:
        """Construct URL for amendment detail page"""
        title = amendment.get('title', '')

        # Convert title to slug
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

        # Common patterns for amendment pages
        possible_urls = [
            f"{self.BASE_URL}/amendments/{slug}/",
            f"{self.BASE_URL}/{slug}/",
        ]

        return possible_urls[0]  # Return first pattern (most common)

    def _get_element_content(self, element, max_length: int = 1000) -> str:
        """Get surrounding content from element"""
        content = []

        # Get element's own text
        if hasattr(element, 'get_text'):
            content.append(element.get_text(strip=True))

        # Get following siblings
        if hasattr(element, 'find_next_siblings'):
            for sibling in element.find_next_siblings(limit=5):
                content.append(sibling.get_text(strip=True))

        return ' '.join(content)[:max_length]

    def _extract_brief_description(self, content: str) -> str:
        """Extract brief description from content"""
        sentences = re.split(r'[.!?]+', content)
        descriptive = [s.strip() for s in sentences if len(s.strip()) > 50]
        return descriptive[0][:500] if descriptive else content[:300]

    def _extract_staff_name(self, content: str) -> str:
        """Extract staff name from content"""
        # Updated staff list (as of 2024)
        staff_names = [
            'Christina Wiegand', 'John Hadley', 'Mike Schmidtke', 'Chip Collier',
            'Roger Pugliese', 'Allie Iberle', 'Myra Brouwer', 'Julia Byrd',
            'Cindy Chaya', 'Cameron Rhodes', 'Kathleen Howington'
        ]

        for name in staff_names:
            if name in content:
                return name

        # Pattern matching
        match = re.search(r'(?:Staff|Contact|Lead):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)', content)
        if match:
            return match.group(1)

        return ''

    def _extract_element_url(self, element) -> Optional[str]:
        """Extract URL from element"""
        if not element:
            return None

        if hasattr(element, 'get') and element.name == 'a':
            return element.get('href')

        if hasattr(element, 'find'):
            link = element.find('a', href=True)
            if link:
                href = link.get('href')
                if href.startswith('/'):
                    return self.BASE_URL + href
                return href

        return None

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        try:
            parsed = date_parser.parse(date_str, fuzzy=True)
            return parsed.isoformat()
        except:
            return None

    def _is_amendment_text(self, text: str) -> bool:
        """Check if text is an amendment title"""
        pattern = r'(?:Amendment|Framework|Regulatory)\s+\d+'
        return bool(re.search(pattern, text, re.IGNORECASE))

    def _is_duplicate_in_list(self, amendment: Dict, amendments: List[Dict]) -> bool:
        """Check if amendment already in list"""
        return any(a['action_id'] == amendment['action_id'] for a in amendments)

    def _deduplicate_amendments(self, amendments: List[Dict]) -> List[Dict]:
        """Remove duplicates, keeping most complete version"""
        seen = {}
        for amendment in amendments:
            action_id = amendment['action_id']
            if action_id not in seen or len(str(amendment)) > len(str(seen[action_id])):
                seen[action_id] = amendment

        return list(seen.values())

    def _normalize_title(self, title: str) -> str:
        """Normalize title for matching (remove extra whitespace, lowercase, etc.)"""
        if not title:
            return ""
        # Remove extra whitespace and convert to lowercase for comparison
        return ' '.join(title.lower().split())

    def _determine_status(self, progress_stage: str) -> Optional[str]:
        """
        Determine amendment status based on progress stage.

        Returns:
            'PLANNED' - Pre-scoping or Scoping stage
            'UNDERWAY' - Public Hearing, Secretarial Review, Final Approval, or Public Comment stages
            'Public Comment' - If explicitly in public comment/hearing
            None - Completed/Implemented amendments
        """
        if not progress_stage:
            return None

        stage_lower = progress_stage.lower()

        # Pre-development stages
        if any(x in stage_lower for x in ['pre-scoping', 'prescoping']):
            return 'PLANNED'

        # Scoping phase
        if 'scoping' in stage_lower and 'pre' not in stage_lower:
            return 'PLANNED'

        # Active development/review stages
        if any(x in stage_lower for x in ['public hearing', 'public comment', 'hearing']):
            return 'Public Comment'

        if any(x in stage_lower for x in ['secretarial review', 'final approval', 'council review', 'rule making', 'federal register']):
            return 'UNDERWAY'

        # Completed
        if any(x in stage_lower for x in ['implement', 'complete']):
            return None

        # Default for amendments under development but unclear stage
        return 'UNDERWAY'

    def _generate_action_id(self, title: str) -> str:
        """Generate action ID from title"""
        match = re.search(r'(Amendment|Framework|Regulatory\s+Amendment)\s+(\d+[A-Z]*)', title, re.IGNORECASE)

        if match:
            action_type = match.group(1).lower()
            number = match.group(2)

            type_code = 'fw' if 'framework' in action_type else \
                       'reg' if 'regulatory' in action_type else 'am'

            fmp_code = self._extract_fmp_code(title)

            return f"{fmp_code}-{type_code}-{number}".lower()

        return re.sub(r'[^a-z0-9]+', '-', title.lower())[:50].strip('-')

    def _extract_fmp_code(self, title: str) -> str:
        """Extract FMP code from title"""
        title_lower = title.lower()

        if 'snapper' in title_lower or 'grouper' in title_lower:
            return 'sg'
        elif 'dolphin' in title_lower or 'wahoo' in title_lower:
            return 'dw'
        elif 'coastal' in title_lower or 'migratory' in title_lower or 'cmp' in title_lower:
            return 'cmp'
        elif 'golden' in title_lower and 'crab' in title_lower:
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

        if 'framework' in title_lower:
            return 'Framework'
        elif 'regulatory' in title_lower:
            return 'Regulatory Amendment'
        elif 'emergency' in title_lower:
            return 'Emergency Action'
        else:
            return 'Amendment'

    def _extract_fmp(self, title: str, content: str) -> str:
        """Extract FMP name"""
        combined = (title + ' ' + content).lower()

        fmp_patterns = {
            'Snapper Grouper': r'snapper[\s-]?grouper|sg\s',
            'Coastal Migratory Pelagics': r'coastal\s+migratory|cmp\s|mackerel|cobia',
            'Dolphin Wahoo': r'dolphin[\s-]?wahoo',
            'Golden Crab': r'golden[\s-]?crab',
            'Sargassum': r'sargassum',
            'Shrimp': r'shrimp',
            'Spiny Lobster': r'spiny[\s-]?lobster|lobster',
            'Coral': r'coral'
        }

        for fmp, pattern in fmp_patterns.items():
            if re.search(pattern, combined):
                return fmp

        return 'Unknown FMP'

    def _extract_progress_stage(self, content: str, title: str) -> str:
        """Extract current progress stage"""
        content_lower = content.lower()

        # Check for status keywords in order of completion
        if 'implemented' in content_lower:
            return 'Implemented'
        if 'final rule' in content_lower:
            return 'Final Rule'
        if 'rule making' in content_lower or 'rulemaking' in content_lower:
            return 'Rule Making'
        if 'federal register' in content_lower:
            return 'Federal Register'
        if 'secretarial review' in content_lower or 'nmfs review' in content_lower or 'submitted' in content_lower:
            return 'Secretarial Review'
        if 'final approval' in content_lower or 'final action' in content_lower:
            return 'Final Approval'
        if 'council review' in content_lower:
            return 'Council Review'
        if 'public hearing' in content_lower:
            return 'Public Hearing'
        if 'scoping' in content_lower and 'pre' not in content_lower:
            return 'Scoping'
        if 'pre-scoping' in content_lower:
            return 'Pre-Scoping'

        return 'Scoping'

    def _calculate_progress_percentage(self, stage: str) -> int:
        """Calculate progress percentage"""
        if not stage:
            return 0

        stage_lower = stage.lower()

        for stage_key, percentage in self.PROGRESS_STAGES.items():
            if stage_key in stage_lower:
                return percentage

        # Fallback patterns
        if 'implement' in stage_lower:
            return 95
        if 'rule' in stage_lower:
            return 85
        if 'review' in stage_lower:
            return 75
        if 'approval' in stage_lower:
            return 65
        if 'hearing' in stage_lower:
            return 45

        return 10
