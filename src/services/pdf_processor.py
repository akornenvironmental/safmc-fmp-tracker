"""
PDF Processing Service
Handles PDF download, text extraction, and preparation for AI analysis
"""

import os
import re
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pdfplumber
from PyPDF2 import PdfReader
import logging

from src.config.extensions import db
from src.models.document import Document
from src.models.document_enhanced import DocumentChunk, DocumentProcessing

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDFs: download, extract text, create chunks"""

    def __init__(self, chunk_size=3000, chunk_overlap=200):
        """
        Initialize PDF processor

        Args:
            chunk_size: Target size for text chunks (characters)
            chunk_overlap: Overlap between chunks to maintain context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def download_pdf(self, url: str, output_path: str) -> Tuple[bool, Optional[str]]:
        """
        Download PDF from URL

        Returns:
            (success: bool, error_message: Optional[str])
        """
        try:
            headers = {
                'User-Agent': 'SAFMC FMP Tracker Bot/1.0 (Document Archival)'
            }

            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()

            # Verify it's a PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower():
                return False, f"URL does not point to a PDF (Content-Type: {content_type})"

            # Save to file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True, None

        except requests.exceptions.RequestException as e:
            return False, f"Download failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, int, float, bool]:
        """
        Extract text from PDF using pdfplumber (better for tables/layout)

        Returns:
            (full_text, page_count, quality_score, has_images)
        """
        try:
            full_text = []
            page_count = 0
            has_images = False
            char_count = 0

            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text() or ""
                    full_text.append(f"\n--- Page {page_num} ---\n{text}")
                    char_count += len(text)

                    # Check for images
                    if page.images and len(page.images) > 0:
                        has_images = True

            combined_text = "\n".join(full_text)

            # Calculate quality score (chars per page ratio)
            avg_chars_per_page = char_count / page_count if page_count > 0 else 0
            quality_score = min(1.0, avg_chars_per_page / 2000)  # 2000 chars/page is "good"

            return combined_text, page_count, quality_score, has_images

        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}, trying PyPDF2 fallback")
            return self._extract_text_fallback(pdf_path)

    def _extract_text_fallback(self, pdf_path: str) -> Tuple[str, int, float, bool]:
        """Fallback extraction using PyPDF2"""
        try:
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)

            full_text = []
            char_count = 0

            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                full_text.append(f"\n--- Page {page_num} ---\n{text}")
                char_count += len(text)

            combined_text = "\n".join(full_text)
            avg_chars_per_page = char_count / page_count if page_count > 0 else 0
            quality_score = min(1.0, avg_chars_per_page / 2000)

            return combined_text, page_count, quality_score, False

        except Exception as e:
            logger.error(f"PyPDF2 fallback also failed: {e}")
            return "", 0, 0.0, False

    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Remove page headers/footers (common patterns)
        # This is basic - can be enhanced
        text = re.sub(r'Page \d+ of \d+', '', text)

        # Normalize whitespace
        text = re.sub(r'[ \t]+', ' ', text)

        return text.strip()

    def extract_sections(self, text: str) -> List[Dict[str, any]]:
        """
        Extract document sections based on headings
        Returns list of {title, content, level, page_range}
        """
        sections = []

        # Common heading patterns in regulatory documents
        heading_patterns = [
            r'^(\d+\.\d+\.?\d*)\s+([A-Z][^\n]+)$',  # 3.2.1 Section Title
            r'^([A-Z][A-Z\s]{3,}[A-Z])$',  # ALL CAPS HEADINGS
            r'^(Chapter|Section|Appendix)\s+(\d+[A-Z]?):?\s*([^\n]+)$',
        ]

        lines = text.split('\n')
        current_section = {'title': 'Introduction', 'content': [], 'level': 0}

        for line in lines:
            is_heading = False

            for pattern in heading_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    # Save previous section
                    if current_section['content']:
                        sections.append({
                            'title': current_section['title'],
                            'content': '\n'.join(current_section['content']),
                            'level': current_section['level']
                        })

                    # Start new section
                    current_section = {
                        'title': line.strip(),
                        'content': [],
                        'level': len(match.group(1).split('.')) if '.' in match.group(1) else 1
                    }
                    is_heading = True
                    break

            if not is_heading:
                current_section['content'].append(line)

        # Add final section
        if current_section['content']:
            sections.append({
                'title': current_section['title'],
                'content': '\n'.join(current_section['content']),
                'level': current_section['level']
            })

        return sections

    def create_chunks(self, text: str, page_count: int) -> List[Dict[str, any]]:
        """
        Create overlapping chunks optimized for AI context

        Returns list of chunk dictionaries with text and metadata
        """
        # First extract sections for better context
        sections = self.extract_sections(text)

        chunks = []
        chunk_index = 0

        for section in sections:
            section_text = section['content']
            section_title = section['title']

            # If section is small enough, keep it as one chunk
            if len(section_text) <= self.chunk_size:
                chunks.append({
                    'chunk_index': chunk_index,
                    'chunk_text': section_text,
                    'chunk_size': len(section_text),
                    'section_title': section_title,
                    'heading_hierarchy': [section_title],
                    'page_numbers': self._extract_page_numbers(section_text)
                })
                chunk_index += 1
            else:
                # Split large sections
                section_chunks = self._split_text_smart(section_text, section_title)
                for sc in section_chunks:
                    chunks.append({
                        'chunk_index': chunk_index,
                        'chunk_text': sc,
                        'chunk_size': len(sc),
                        'section_title': section_title,
                        'heading_hierarchy': [section_title],
                        'page_numbers': self._extract_page_numbers(sc)
                    })
                    chunk_index += 1

        return chunks

    def _split_text_smart(self, text: str, section_title: str) -> List[str]:
        """
        Smart text splitting: tries to break on paragraph/sentence boundaries
        """
        chunks = []
        current_chunk = ""

        # Split into paragraphs
        paragraphs = text.split('\n\n')

        for para in paragraphs:
            # If adding this paragraph exceeds chunk_size
            if len(current_chunk) + len(para) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    # Add overlap from previous chunk
                    words = current_chunk.split()
                    overlap_text = ' '.join(words[-50:]) if len(words) > 50 else current_chunk
                    current_chunk = overlap_text + "\n\n" + para
                else:
                    # Paragraph itself is too long, split by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sent in sentences:
                        if len(current_chunk) + len(sent) > self.chunk_size:
                            if current_chunk:
                                chunks.append(current_chunk)
                                current_chunk = sent
                            else:
                                # Sentence is too long, just add it
                                chunks.append(sent)
                        else:
                            current_chunk += " " + sent
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _extract_page_numbers(self, text: str) -> List[int]:
        """Extract page numbers mentioned in text"""
        page_markers = re.findall(r'--- Page (\d+) ---', text)
        return [int(p) for p in page_markers] if page_markers else []

    def extract_keywords(self, text: str, top_n=10) -> List[str]:
        """
        Extract keywords from text (simple frequency-based)
        For production, could use NLP libraries like spaCy
        """
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                      'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                      'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}

        # Tokenize and count
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        word_freq = {}

        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Get top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]

    def process_document(self, document_id: int, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        Complete processing pipeline for a document

        1. Extract text from PDF
        2. Create chunks
        3. Update database

        Returns (success, error_message)
        """
        try:
            document = Document.query.get(document_id)
            if not document:
                return False, "Document not found"

            # Create or get processing record
            processing = DocumentProcessing.query.filter_by(document_id=document_id).first()
            if not processing:
                processing = DocumentProcessing(document_id=document_id)
                db.session.add(processing)

            processing.status = 'processing'
            processing.started_at = datetime.utcnow()
            db.session.commit()

            # Extract text
            logger.info(f"Extracting text from {pdf_path}")
            full_text, page_count, quality_score, has_images = self.extract_text_from_pdf(pdf_path)

            if not full_text:
                processing.status = 'failed'
                processing.error_message = "No text could be extracted from PDF"
                db.session.commit()
                return False, "Text extraction failed"

            # Clean text
            full_text = self.clean_text(full_text)

            # Update document
            document.full_text = full_text
            document.page_count = page_count
            document.has_images = has_images

            processing.pdf_extracted = True
            processing.text_quality_score = quality_score
            db.session.commit()

            # Create chunks
            logger.info(f"Creating chunks for document {document_id}")
            chunks = self.create_chunks(full_text, page_count)

            # Save chunks to database
            for chunk_data in chunks:
                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk_data['chunk_index'],
                    chunk_text=chunk_data['chunk_text'],
                    chunk_size=chunk_data['chunk_size'],
                    token_count=len(chunk_data['chunk_text']) // 4,  # Rough estimate
                    page_numbers=chunk_data['page_numbers'],
                    section_title=chunk_data['section_title'],
                    heading_hierarchy=chunk_data['heading_hierarchy'],
                    keywords=self.extract_keywords(chunk_data['chunk_text'])
                )
                db.session.add(chunk)

            processing.chunks_created = True
            processing.chunk_count = len(chunks)
            processing.chunking_strategy = 'semantic_overlap'
            processing.status = 'completed'
            processing.completed_at = datetime.utcnow()

            db.session.commit()

            logger.info(f"Successfully processed document {document_id}: {len(chunks)} chunks created")
            return True, None

        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            if processing:
                processing.status = 'failed'
                processing.error_message = str(e)
                db.session.commit()
            return False, str(e)


# Helper function for routes
def process_pdf_from_url(url: str, document_data: Dict) -> Tuple[Optional[Document], Optional[str]]:
    """
    Download and process a PDF from URL, create Document record

    Args:
        url: PDF download URL
        document_data: Dict with document metadata (title, type, etc.)

    Returns:
        (Document object, error_message)
    """
    processor = PDFProcessor()

    # Create temp directory
    temp_dir = '/tmp/safmc_pdfs'
    os.makedirs(temp_dir, exist_ok=True)

    # Generate filename
    filename = hashlib.md5(url.encode()).hexdigest() + '.pdf'
    pdf_path = os.path.join(temp_dir, filename)

    try:
        # Download
        success, error = processor.download_pdf(url, pdf_path)
        if not success:
            return None, error

        # Calculate hash
        file_hash = processor.calculate_file_hash(pdf_path)
        file_size = os.path.getsize(pdf_path)

        # Check if already exists
        existing = Document.query.filter_by(file_hash=file_hash).first()
        if existing:
            logger.info(f"Document already exists: {existing.id}")
            return existing, None

        # Create document record
        document = Document(
            title=document_data.get('title', 'Untitled'),
            document_type=document_data.get('document_type'),
            fmp=document_data.get('fmp'),
            file_url=url,
            file_size_kb=file_size // 1024,
            file_type='PDF',
            document_date=document_data.get('document_date'),
            related_action_id=document_data.get('action_id'),
            related_meeting_id=document_data.get('meeting_id')
        )
        db.session.add(document)
        db.session.flush()  # Get document ID

        # Process PDF
        success, error = processor.process_document(document.id, pdf_path)

        if not success:
            db.session.rollback()
            return None, error

        db.session.commit()

        # Cleanup
        try:
            os.remove(pdf_path)
        except:
            pass

        return document, None

    except Exception as e:
        logger.error(f"Error in process_pdf_from_url: {e}")
        db.session.rollback()
        return None, str(e)
