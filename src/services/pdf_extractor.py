"""
PDF Text Extraction Service
Extracts text content from PDF documents for indexing and search
"""

import logging
import os
import tempfile
from typing import Dict, Optional, List
import requests

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Service for extracting text from PDF files"""

    def __init__(self):
        """Initialize PDF extractor"""
        self.temp_dir = tempfile.gettempdir()

    def download_pdf(self, url: str, timeout: int = 60) -> Optional[str]:
        """
        Download PDF from URL to temp file

        Args:
            url: PDF URL
            timeout: Request timeout in seconds

        Returns:
            Path to downloaded file or None
        """
        try:
            logger.info(f"Downloading PDF: {url}")

            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()

            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.pdf',
                dir=self.temp_dir
            )

            # Write content
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)

            temp_file.close()

            logger.info(f"Downloaded to: {temp_file.name}")
            return temp_file.name

        except Exception as e:
            logger.error(f"Error downloading PDF {url}: {e}")
            return None

    def extract_text_pypdf2(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text using PyPDF2 (faster, basic extraction)

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dict with text, metadata, and page count
        """
        try:
            import PyPDF2

            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Extract metadata
                metadata = {}
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', '')
                    }

                # Extract text from all pages
                text_parts = []
                page_count = len(pdf_reader.pages)

                for page_num in range(page_count):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

                full_text = '\n\n'.join(text_parts)

                return {
                    'text': full_text,
                    'page_count': page_count,
                    'metadata': metadata,
                    'method': 'pypdf2',
                    'success': True
                }

        except Exception as e:
            logger.error(f"PyPDF2 extraction failed for {pdf_path}: {e}")
            return {
                'text': '',
                'success': False,
                'error': str(e),
                'method': 'pypdf2'
            }

    def extract_text_pdfplumber(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text using pdfplumber (more accurate, slower)

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dict with text, tables, metadata, and page count
        """
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                # Extract metadata
                metadata = {
                    'title': pdf.metadata.get('Title', ''),
                    'author': pdf.metadata.get('Author', ''),
                    'subject': pdf.metadata.get('Subject', ''),
                    'creator': pdf.metadata.get('Creator', ''),
                    'producer': pdf.metadata.get('Producer', ''),
                    'creation_date': pdf.metadata.get('CreationDate', '')
                }

                # Extract text and tables from all pages
                text_parts = []
                tables = []
                page_count = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

                    # Extract tables
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table in page_tables:
                            tables.append({
                                'page': page_num + 1,
                                'data': table
                            })

                full_text = '\n\n'.join(text_parts)

                return {
                    'text': full_text,
                    'page_count': page_count,
                    'metadata': metadata,
                    'tables': tables,
                    'table_count': len(tables),
                    'method': 'pdfplumber',
                    'success': True
                }

        except Exception as e:
            logger.error(f"pdfplumber extraction failed for {pdf_path}: {e}")
            return {
                'text': '',
                'success': False,
                'error': str(e),
                'method': 'pdfplumber'
            }

    def extract_text(self, pdf_path: str, method: str = 'auto') -> Dict[str, any]:
        """
        Extract text from PDF using best available method

        Args:
            pdf_path: Path to PDF file
            method: 'pypdf2', 'pdfplumber', or 'auto'

        Returns:
            Dict with extraction results
        """
        if method == 'pypdf2':
            return self.extract_text_pypdf2(pdf_path)
        elif method == 'pdfplumber':
            return self.extract_text_pdfplumber(pdf_path)
        else:  # auto
            # Try pdfplumber first for better quality
            result = self.extract_text_pdfplumber(pdf_path)
            if result['success'] and result.get('text', '').strip():
                return result

            # Fallback to PyPDF2
            logger.info("Falling back to PyPDF2...")
            return self.extract_text_pypdf2(pdf_path)

    def extract_from_url(self, url: str, method: str = 'auto') -> Dict[str, any]:
        """
        Download and extract text from PDF URL

        Args:
            url: PDF URL
            method: Extraction method

        Returns:
            Dict with extraction results including file_size
        """
        pdf_path = None
        try:
            # Download PDF
            pdf_path = self.download_pdf(url)
            if not pdf_path:
                return {
                    'success': False,
                    'error': 'Failed to download PDF',
                    'url': url
                }

            # Get file size
            file_size = os.path.getsize(pdf_path)

            # Extract text
            result = self.extract_text(pdf_path, method=method)
            result['url'] = url
            result['file_size_bytes'] = file_size

            return result

        except Exception as e:
            logger.error(f"Error processing PDF from {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }

        finally:
            # Clean up temp file
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                    logger.debug(f"Cleaned up temp file: {pdf_path}")
                except:
                    pass

    def extract_summary(self, text: str, max_length: int = 1000) -> str:
        """
        Extract a summary from the beginning of the text

        Args:
            text: Full text
            max_length: Maximum summary length

        Returns:
            Summary text
        """
        if not text:
            return ""

        # Clean up text
        text = ' '.join(text.split())

        # Try to find executive summary section
        text_lower = text.lower()
        summary_markers = [
            'executive summary',
            'summary',
            'purpose and need',
            'introduction'
        ]

        for marker in summary_markers:
            idx = text_lower.find(marker)
            if idx >= 0:
                # Extract from marker position
                start = idx
                # Try to find next section
                end_markers = ['table of contents', 'contents', 'chapter', 'section']
                end = len(text)
                for end_marker in end_markers:
                    end_idx = text_lower.find(end_marker, start + 100)
                    if end_idx > start:
                        end = end_idx
                        break

                summary_text = text[start:end]
                if len(summary_text) > max_length:
                    return summary_text[:max_length] + '...'
                return summary_text

        # Fallback: use first N characters
        if len(text) > max_length:
            return text[:max_length] + '...'
        return text


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    extractor = PDFExtractor()

    # Test with a sample PDF URL
    test_url = "https://safmc.net/wp-content/uploads/2023/09/Att05_DW_Reg3_PH_Doc.pdf"

    result = extractor.extract_from_url(test_url)

    if result['success']:
        print(f"✓ Extracted {len(result['text'])} characters")
        print(f"  Pages: {result.get('page_count', 0)}")
        print(f"  File size: {result.get('file_size_bytes', 0)} bytes")
        if result.get('tables'):
            print(f"  Tables: {result.get('table_count', 0)}")

        # Print first 500 characters
        print(f"\nFirst 500 chars:\n{result['text'][:500]}...")
    else:
        print(f"✗ Extraction failed: {result.get('error')}")
