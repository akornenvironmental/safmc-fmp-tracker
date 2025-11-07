"""
Briefing Books Scraper
Scrapes Council meeting briefing books from SAFMC website
"""

from src.scrapers.base_document_scraper import BaseDocumentScraper
from src.constants.document_types import DocumentType, DocumentStatus, DocumentSource
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class BriefingBooksScraper(BaseDocumentScraper):
    """Scraper for SAFMC briefing books"""

    def __init__(self):
        super().__init__(delay_seconds=2)
        self.base_url = DocumentSource.SAFMC_BASE
        self.briefing_books_url = DocumentSource.BRIEFING_BOOKS

    def scrape_briefing_books(self, limit: int = None):
        """
        Scrape all briefing books from the archive

        Args:
            limit: Maximum number of pages to scrape (None for all)

        Returns:
            Dict with results summary
        """
        results = {
            'success': True,
            'books_found': 0,
            'documents_queued': 0,
            'errors': []
        }

        try:
            logger.info("Starting briefing books scrape...")

            # Fetch the main briefing books page
            soup = self.fetch_page(self.briefing_books_url)
            if not soup:
                results['success'] = False
                results['errors'].append("Failed to fetch briefing books page")
                return results

            # Find all briefing book entries
            # The SAFMC site typically has briefing books in article/post listings
            book_entries = soup.find_all(['article', 'div'], class_=re.compile(r'(post|entry|item|meeting)'))

            logger.info(f"Found {len(book_entries)} potential briefing book entries")

            for idx, entry in enumerate(book_entries):
                if limit and idx >= limit:
                    break

                try:
                    # Extract title
                    title_elem = entry.find(['h2', 'h3', 'h4'], class_=re.compile(r'(title|heading)'))
                    if not title_elem:
                        title_elem = entry.find(['h2', 'h3', 'h4'])

                    if not title_elem:
                        continue

                    title = self.clean_text(title_elem.get_text())
                    if not title or len(title) < 10:
                        continue

                    results['books_found'] += 1

                    # Extract date from title (e.g., "September 2025 Council Meeting")
                    meeting_date = self.extract_date_from_text(title)

                    # Extract link to detail page
                    link_elem = title_elem.find('a') or entry.find('a')
                    detail_url = None
                    if link_elem and link_elem.get('href'):
                        href = link_elem['href']
                        if not href.startswith('http'):
                            detail_url = self.base_url.rstrip('/') + href
                        else:
                            detail_url = href

                    # Determine meeting type from title
                    meeting_type = self._extract_meeting_type(title)

                    # Look for PDF links in this entry
                    pdf_links = self.extract_pdf_links(entry, self.base_url)

                    logger.info(f"Processing: {title} ({len(pdf_links)} PDFs found)")

                    # Queue each PDF for processing
                    for pdf in pdf_links:
                        doc_id = self.generate_document_id(pdf['url'], pdf['text'])

                        # Determine document type from PDF name
                        doc_type = self._classify_pdf_type(pdf['text'])

                        # Queue for processing
                        self.queue_document_for_processing(
                            url=pdf['url'],
                            document_type=doc_type,
                            priority=3,  # Higher priority for recent documents
                            metadata={
                                'title': pdf['text'] or title,
                                'meeting_title': title,
                                'meeting_date': meeting_date,
                                'meeting_type': meeting_type,
                                'source_page': detail_url or self.briefing_books_url,
                                'document_id': doc_id
                            }
                        )
                        results['documents_queued'] += 1

                    # If there's a detail URL, also scrape that page for more PDFs
                    if detail_url:
                        detail_soup = self.fetch_page(detail_url)
                        if detail_soup:
                            detail_pdfs = self.extract_pdf_links(detail_soup, self.base_url)
                            for pdf in detail_pdfs:
                                if pdf not in pdf_links:  # Avoid duplicates
                                    doc_id = self.generate_document_id(pdf['url'], pdf['text'])
                                    doc_type = self._classify_pdf_type(pdf['text'])

                                    self.queue_document_for_processing(
                                        url=pdf['url'],
                                        document_type=doc_type,
                                        priority=3,
                                        metadata={
                                            'title': pdf['text'] or title,
                                            'meeting_title': title,
                                            'meeting_date': meeting_date,
                                            'meeting_type': meeting_type,
                                            'source_page': detail_url,
                                            'document_id': doc_id
                                        }
                                    )
                                    results['documents_queued'] += 1

                except Exception as e:
                    error_msg = f"Error processing entry: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)

            logger.info(f"Briefing books scrape complete: {results['books_found']} books, "
                       f"{results['documents_queued']} documents queued")

        except Exception as e:
            logger.error(f"Error in briefing books scrape: {e}")
            results['success'] = False
            results['errors'].append(str(e))

        return results

    def _extract_meeting_type(self, title: str) -> str:
        """Extract meeting type from title"""
        title_lower = title.lower()

        if 'council meeting' in title_lower:
            return 'Council Meeting'
        elif 'advisory panel' in title_lower or ' ap ' in title_lower:
            return 'Advisory Panel'
        elif 'ssc' in title_lower or 'scientific and statistical' in title_lower:
            return 'Scientific and Statistical Committee'
        elif 'public hearing' in title_lower or 'scoping' in title_lower:
            return 'Public Hearing/Scoping'
        elif 'workgroup' in title_lower or 'work group' in title_lower:
            return 'Workgroup'
        else:
            return 'Meeting'

    def _classify_pdf_type(self, filename: str) -> str:
        """Classify document type based on filename"""
        filename_lower = filename.lower()

        if 'agenda' in filename_lower:
            return DocumentType.MEETING_AGENDA
        elif 'transcript' in filename_lower or 'verbatim' in filename_lower:
            return DocumentType.MEETING_TRANSCRIPT
        elif 'minutes' in filename_lower:
            return DocumentType.MEETING_MINUTES
        elif 'briefing' in filename_lower or 'briefing book' in filename_lower:
            return DocumentType.BRIEFING_BOOK
        elif 'committee' in filename_lower and 'report' in filename_lower:
            return DocumentType.COMMITTEE_REPORT
        elif 'amendment' in filename_lower:
            if 'regulatory' in filename_lower:
                return DocumentType.REGULATORY_AMENDMENT
            elif 'framework' in filename_lower:
                return DocumentType.FRAMEWORK_AMENDMENT
            else:
                return DocumentType.AMENDMENT
        elif 'comment' in filename_lower:
            return DocumentType.PUBLIC_COMMENTS
        else:
            return DocumentType.OTHER


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    scraper = BriefingBooksScraper()
    results = scraper.scrape_briefing_books(limit=5)  # Test with 5 books
    print(f"Results: {results}")
