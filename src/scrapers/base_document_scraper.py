"""
Base Document Scraper
Provides common functionality for all document scrapers
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
import logging
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)


class BaseDocumentScraper:
    """Base class for document scrapers"""

    def __init__(self, delay_seconds=1):
        """
        Initialize scraper

        Args:
            delay_seconds: Delay between requests to be respectful
        """
        self.delay_seconds = delay_seconds
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SAFMC FMP Tracker Bot/1.0 (Fishery Management Research)'
        })

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if error
        """
        try:
            logger.info(f"Fetching: {url}")
            time.sleep(self.delay_seconds)

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            return BeautifulSoup(response.content, 'html.parser')

        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def generate_document_id(self, url: str, title: str) -> str:
        """
        Generate unique document ID from URL and title

        Args:
            url: Source URL
            title: Document title

        Returns:
            MD5 hash as document ID
        """
        content = f"{url}|{title}"
        return hashlib.md5(content.encode()).hexdigest()

    def extract_pdf_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
        Extract all PDF links from a page

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for relative links

        Returns:
            List of dicts with 'url' and 'text' keys
        """
        pdf_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                # Make absolute URL
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = base_url.rstrip('/') + href
                    else:
                        href = base_url.rstrip('/') + '/' + href

                pdf_links.append({
                    'url': href,
                    'text': link.get_text(strip=True)
                })

        return pdf_links

    def extract_date_from_text(self, text: str) -> Optional[str]:
        """
        Extract date from text using common patterns

        Args:
            text: Text to parse

        Returns:
            Date string in YYYY-MM-DD format or None
        """
        import re
        from dateutil import parser

        # Common date patterns
        patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # MM/DD/YYYY or similar
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',    # YYYY-MM-DD
            r'[A-Za-z]+\s+\d{1,2},?\s+\d{4}',  # Month DD, YYYY
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_obj = parser.parse(match.group())
                    return date_obj.strftime('%Y-%m-%d')
                except:
                    continue

        return None

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Remove common artifacts
        text = text.replace('\xa0', ' ')
        text = text.replace('\u200b', '')

        return text.strip()

    def extract_keywords(self, text: str, soup: BeautifulSoup = None) -> List[str]:
        """
        Extract keywords from text and metadata

        Args:
            text: Document text
            soup: BeautifulSoup object for metadata

        Returns:
            List of keywords
        """
        keywords = []

        # Extract from meta tags if available
        if soup:
            meta_keywords = soup.find('meta', {'name': 'keywords'})
            if meta_keywords and meta_keywords.get('content'):
                keywords.extend([k.strip() for k in meta_keywords['content'].split(',')])

        # Common fishery management terms
        fishery_terms = [
            'catch limit', 'quota', 'season', 'closure', 'permit',
            'overfishing', 'overfished', 'rebuilding', 'allocation',
            'size limit', 'bag limit', 'gear', 'habitat', 'bycatch'
        ]

        text_lower = text.lower()
        for term in fishery_terms:
            if term in text_lower:
                keywords.append(term)

        return list(set(keywords))

    def extract_fmp_from_text(self, text: str) -> Optional[str]:
        """
        Identify which FMP a document belongs to

        Args:
            text: Document text

        Returns:
            FMP name or None
        """
        from src.constants.document_types import FMP

        text_lower = text.lower()

        # Check for FMP keywords
        fmp_keywords = {
            FMP.SNAPPER_GROUPER: ['snapper', 'grouper', 'snapper-grouper', 'snapper grouper'],
            FMP.DOLPHIN_WAHOO: ['dolphin', 'wahoo', 'dolphin-wahoo', 'dolphin wahoo', 'mahi'],
            FMP.COASTAL_MIGRATORY_PELAGICS: ['mackerel', 'cobia', 'pelagic', 'king mackerel', 'spanish mackerel'],
            FMP.GOLDEN_CRAB: ['golden crab', 'crab'],
            FMP.SHRIMP: ['shrimp', 'penaeid'],
            FMP.SPINY_LOBSTER: ['lobster', 'spiny lobster'],
            FMP.CORAL: ['coral', 'coral reef'],
            FMP.SARGASSUM: ['sargassum', 'seaweed']
        }

        for fmp, keywords in fmp_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return fmp

        return None

    def create_document_record(self, **kwargs) -> Dict:
        """
        Create standardized document record

        Returns:
            Dictionary with document fields
        """
        return {
            'document_id': kwargs.get('document_id'),
            'title': self.clean_text(kwargs.get('title', '')),
            'document_type': kwargs.get('document_type'),
            'fmp': kwargs.get('fmp'),
            'amendment_number': kwargs.get('amendment_number'),
            'document_date': kwargs.get('document_date'),
            'status': kwargs.get('status'),
            'source_url': kwargs.get('source_url'),
            'download_url': kwargs.get('download_url'),
            'description': self.clean_text(kwargs.get('description', '')),
            'keywords': kwargs.get('keywords', []),
            'last_scraped': datetime.utcnow()
        }

    def queue_document_for_processing(self, url: str, document_type: str,
                                      fmp: Optional[str] = None,
                                      priority: int = 5,
                                      metadata: Optional[Dict] = None):
        """
        Add document to processing queue

        Args:
            url: Document URL
            document_type: Type of document
            fmp: FMP category
            priority: Priority (1-10, lower is higher priority)
            metadata: Additional metadata
        """
        from src.config.extensions import db
        from sqlalchemy import text

        try:
            db.session.execute(text("""
                INSERT INTO document_scrape_queue
                (url, document_type, fmp, priority, metadata, status)
                VALUES (:url, :doc_type, :fmp, :priority, :metadata::jsonb, 'pending')
                ON CONFLICT DO NOTHING
            """), {
                'url': url,
                'doc_type': document_type,
                'fmp': fmp,
                'priority': priority,
                'metadata': metadata or {}
            })
            db.session.commit()
            logger.info(f"Queued document: {url}")
        except Exception as e:
            logger.error(f"Error queuing document {url}: {e}")
            db.session.rollback()
