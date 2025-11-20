"""
SAFE Reports Scraper
Scrapes Stock Assessment and Fishery Evaluation (SAFE) reports from SAFMC
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin, urlparse
import PyPDF2
import io

logger = logging.getLogger(__name__)


class SAFEReportScraper:
    """Scraper for SAFE (Stock Assessment and Fishery Evaluation) reports"""

    BASE_URL = 'https://safmc.net'
    SAFE_REPORTS_URL = f'{BASE_URL}/documents/13a_south-atlantic-stock-assessment-and-fishery-evaluation-reports/'

    # Known SAFE report URLs by FMP
    KNOWN_REPORTS = {
        'Snapper Grouper': {
            'html': 'https://safmc.net/wp-content/uploads/2025/01/SG-FMP-SAFE-Report-for-html.html',
            'pdf': 'https://safmc.net/wp-content/uploads/2024/01/SG-FMP-SAFE-Report-Jan-2024.pdf'
        },
        'Dolphin Wahoo': {
            'rpubs': 'https://rpubs.com/chipcollier/954965',
            'pdf': None  # May need to find
        },
        'Shrimp': {
            'url': 'https://safmc.net/documents/shrimp-safe-report/',
            'pdf': None
        }
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SAFMC FMP Tracker (aaron.kornbluth@gmail.com)'
        })

    def discover_all_safe_reports(self) -> List[Dict]:
        """
        Discover all SAFE reports from main landing page

        Returns:
            List of report metadata dictionaries
        """
        logger.info("Discovering SAFE reports from landing page...")

        reports = []

        try:
            # Start with known reports
            for fmp, urls in self.KNOWN_REPORTS.items():
                for format_type, url in urls.items():
                    if url:
                        reports.append({
                            'fmp': fmp,
                            'source_format': format_type,
                            'source_url': url,
                            'report_year': datetime.now().year,  # Will refine later
                            'is_current': True
                        })

            # Try to discover additional reports from landing page
            try:
                response = self.session.get(self.SAFE_REPORTS_URL, timeout=30)
                if response.ok:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Look for additional report links
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link.get('href')
                        text = link.get_text(strip=True).lower()

                        # Check if it's a SAFE report link
                        if any(keyword in text for keyword in ['safe', 'stock assessment', 'fishery evaluation']):
                            full_url = urljoin(self.BASE_URL, href)

                            # Determine FMP
                            fmp = None
                            for fmp_name in ['Snapper Grouper', 'Dolphin Wahoo', 'Shrimp']:
                                if fmp_name.lower() in text:
                                    fmp = fmp_name
                                    break

                            if fmp:
                                # Determine format
                                source_format = 'html'
                                if '.pdf' in href.lower():
                                    source_format = 'pdf'
                                elif 'rpubs.com' in href:
                                    source_format = 'rpubs'

                                # Check if not already in reports
                                if not any(r['source_url'] == full_url for r in reports):
                                    reports.append({
                                        'fmp': fmp,
                                        'source_format': source_format,
                                        'source_url': full_url,
                                        'report_year': datetime.now().year,
                                        'is_current': True
                                    })

            except Exception as e:
                logger.warning(f"Could not discover additional reports: {e}")

            logger.info(f"Discovered {len(reports)} SAFE reports")
            return reports

        except Exception as e:
            logger.error(f"Error discovering SAFE reports: {e}")
            return reports

    def scrape_html_report(self, url: str) -> Dict:
        """
        Scrape SAFE report from HTML page

        Args:
            url: URL to HTML SAFE report

        Returns:
            Dictionary with report content and metadata
        """
        logger.info(f"Scraping HTML SAFE report from {url}")

        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            report_data = {
                'source_url': url,
                'source_format': 'html',
                'scraped_at': datetime.now().isoformat()
            }

            # Extract title
            title = soup.find('title') or soup.find('h1')
            if title:
                report_data['report_title'] = title.get_text(strip=True)
                # Try to extract year from title
                year_match = re.search(r'20\d{2}', report_data['report_title'])
                if year_match:
                    report_data['report_year'] = int(year_match.group())

            # Extract main content
            main_content = soup.find('body') or soup

            # Store full HTML for later processing
            report_data['html_content'] = str(main_content)[:50000]  # Limit to 50KB

            # Extract sections
            sections = self._extract_sections_from_html(soup)
            report_data['sections'] = sections

            # Extract tables (for stock data)
            tables = self._extract_tables_from_html(soup)
            report_data['tables'] = tables

            return report_data

        except Exception as e:
            logger.error(f"Error scraping HTML report from {url}: {e}")
            return {'source_url': url, 'error': str(e)}

    def scrape_pdf_report(self, url: str) -> Dict:
        """
        Scrape SAFE report from PDF file

        Args:
            url: URL to PDF SAFE report

        Returns:
            Dictionary with report content and metadata
        """
        logger.info(f"Scraping PDF SAFE report from {url}")

        try:
            # Download PDF
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            # Parse PDF
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            report_data = {
                'source_url': url,
                'source_format': 'pdf',
                'pdf_file_path': url,  # Store URL as path
                'scraped_at': datetime.now().isoformat(),
                'page_count': len(pdf_reader.pages)
            }

            # Extract text from all pages
            full_text = []
            for page in pdf_reader.pages:
                try:
                    text = page.extract_text()
                    if text:
                        full_text.append(text)
                except:
                    continue

            report_data['pdf_text'] = '\n\n'.join(full_text)[:100000]  # Limit to 100KB

            # Try to extract title and year from first page
            if full_text:
                first_page = full_text[0]

                # Extract title (usually first few lines)
                title_match = re.search(r'^(.+?)\n', first_page)
                if title_match:
                    report_data['report_title'] = title_match.group(1).strip()

                # Extract year
                year_match = re.search(r'20\d{2}', first_page[:500])
                if year_match:
                    report_data['report_year'] = int(year_match.group())

            return report_data

        except Exception as e:
            logger.error(f"Error scraping PDF report from {url}: {e}")
            return {'source_url': url, 'error': str(e)}

    def scrape_rpubs_report(self, url: str) -> Dict:
        """
        Scrape SAFE report from RPubs page

        Args:
            url: URL to RPubs SAFE report

        Returns:
            Dictionary with report content and metadata
        """
        logger.info(f"Scraping RPubs SAFE report from {url}")

        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            report_data = {
                'source_url': url,
                'source_format': 'rpubs',
                'scraped_at': datetime.now().isoformat()
            }

            # Extract title
            title = soup.find('h1', class_='title') or soup.find('title')
            if title:
                report_data['report_title'] = title.get_text(strip=True)

            # Extract main content (RPubs typically has content in specific divs)
            content_div = soup.find('div', {'id': 'content'}) or \
                         soup.find('div', {'class': 'container-fluid'}) or \
                         soup.find('body')

            if content_div:
                report_data['html_content'] = str(content_div)[:50000]

                # Extract sections
                sections = self._extract_sections_from_html(content_div)
                report_data['sections'] = sections

                # Extract tables
                tables = self._extract_tables_from_html(content_div)
                report_data['tables'] = tables

            return report_data

        except Exception as e:
            logger.error(f"Error scraping RPubs report from {url}: {e}")
            return {'source_url': url, 'error': str(e)}

    def _extract_sections_from_html(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract sections from HTML content"""
        sections = []

        # Find all headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])

        for heading in headings:
            section = {
                'section_title': heading.get_text(strip=True),
                'heading_level': heading.name
            }

            # Get content until next heading
            content_parts = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h1', 'h2', 'h3', 'h4']:
                    break
                if sibling.name == 'p':
                    content_parts.append(sibling.get_text(strip=True))

            if content_parts:
                section['content'] = ' '.join(content_parts)
                section['word_count'] = len(section['content'].split())

                # Classify section type
                title_lower = section['section_title'].lower()
                if any(kw in title_lower for kw in ['stock status', 'overfished', 'overfishing']):
                    section['section_type'] = 'stock_status'
                elif any(kw in title_lower for kw in ['economic', 'revenue', 'value', 'price']):
                    section['section_type'] = 'economics'
                elif any(kw in title_lower for kw in ['social', 'community', 'employment']):
                    section['section_type'] = 'social'
                elif any(kw in title_lower for kw in ['ecosystem', 'habitat', 'environment']):
                    section['section_type'] = 'ecosystem'
                elif any(kw in title_lower for kw in ['method', 'data', 'assessment']):
                    section['section_type'] = 'methodology'
                elif any(kw in title_lower for kw in ['summary', 'executive', 'overview']):
                    section['section_type'] = 'executive_summary'
                else:
                    section['section_type'] = 'other'

                sections.append(section)

        return sections

    def _extract_tables_from_html(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract tables from HTML content"""
        tables = []

        html_tables = soup.find_all('table')

        for idx, table in enumerate(html_tables):
            table_data = {
                'table_index': idx,
                'rows': []
            }

            # Extract caption if exists
            caption = table.find('caption')
            if caption:
                table_data['caption'] = caption.get_text(strip=True)

            # Extract rows
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    table_data['rows'].append(row_data)

            if table_data['rows']:
                tables.append(table_data)

        return tables

    def scrape_report(self, report_metadata: Dict) -> Dict:
        """
        Scrape a SAFE report based on its format

        Args:
            report_metadata: Dictionary with 'source_url' and 'source_format'

        Returns:
            Complete report data dictionary
        """
        url = report_metadata.get('source_url')
        format_type = report_metadata.get('source_format', 'html')

        if not url:
            raise ValueError("source_url required")

        # Dispatch to appropriate scraper
        if format_type == 'pdf':
            data = self.scrape_pdf_report(url)
        elif format_type == 'rpubs':
            data = self.scrape_rpubs_report(url)
        else:  # html or unknown
            data = self.scrape_html_report(url)

        # Merge with metadata
        data.update(report_metadata)

        return data

    def identify_fmp_from_content(self, content: str) -> Optional[str]:
        """Identify FMP from report content"""
        content_lower = content.lower()

        if any(kw in content_lower for kw in ['snapper', 'grouper', 'hogfish', 'tilefish']):
            return 'Snapper Grouper'
        elif any(kw in content_lower for kw in ['dolphin', 'wahoo', 'mahi']):
            return 'Dolphin Wahoo'
        elif 'shrimp' in content_lower:
            return 'Shrimp'
        elif 'spiny lobster' in content_lower or 'lobster' in content_lower:
            return 'Spiny Lobster'
        elif 'golden crab' in content_lower or 'crab' in content_lower:
            return 'Golden Crab'

        return None


def main():
    """Test the SAFE report scraper"""
    logging.basicConfig(level=logging.INFO)

    scraper = SAFEReportScraper()

    print("Testing SAFE Report Scraper...")
    print("=" * 60)

    # Test 1: Discover reports
    print("\n1. Discovering SAFE reports...")
    reports = scraper.discover_all_safe_reports()
    print(f"   Found {len(reports)} reports")
    for report in reports:
        print(f"   - {report['fmp']}: {report['source_format']} ({report['source_url'][:60]}...)")

    # Test 2: Scrape one HTML report
    if reports:
        html_report = next((r for r in reports if r['source_format'] == 'html'), None)
        if html_report:
            print(f"\n2. Scraping HTML report...")
            data = scraper.scrape_report(html_report)
            print(f"   Title: {data.get('report_title', 'N/A')[:80]}")
            print(f"   Sections: {len(data.get('sections', []))}")
            print(f"   Tables: {len(data.get('tables', []))}")


if __name__ == '__main__':
    main()
