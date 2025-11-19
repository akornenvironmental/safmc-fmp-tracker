"""
Enhanced Document models for AI-powered document analysis
Extends the existing document.py with chunking and search capabilities
"""

from datetime import datetime
from src.config.extensions import db
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlalchemy import Index, func, text


class DocumentChunk(db.Model):
    """Text chunks for AI context windows - optimized for Claude API"""
    __tablename__ = 'document_chunks'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    chunk_index = db.Column(db.Integer, nullable=False)

    # Content
    chunk_text = db.Column(db.Text, nullable=False)
    chunk_size = db.Column(db.Integer)  # Character count
    token_count = db.Column(db.Integer)  # Estimated tokens for AI
    page_numbers = db.Column(ARRAY(db.Integer))

    # Context
    section_title = db.Column(db.String(500))
    heading_hierarchy = db.Column(ARRAY(db.Text))  # ['Chapter 3', 'Section 3.2', 'Environmental Impact']

    # Metadata for relevance
    keywords = db.Column(ARRAY(db.Text))
    entities = db.Column(ARRAY(db.Text))  # Organizations, species, locations

    # Full-text search
    search_vector = db.Column(TSVECTOR)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    document = db.relationship('Document', backref=db.backref('chunks', lazy='dynamic', cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('document_id', 'chunk_index', name='uq_document_chunk'),
        Index('idx_chunks_document', 'document_id'),
        Index('idx_chunks_search', 'search_vector', postgresql_using='gin'),
    )

    def to_dict(self, include_full_text=False):
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'document_id': self.document_id,
            'chunk_index': self.chunk_index,
            'chunk_size': self.chunk_size,
            'token_count': self.token_count,
            'page_numbers': self.page_numbers,
            'section_title': self.section_title,
            'heading_hierarchy': self.heading_hierarchy,
            'keywords': self.keywords,
            'entities': self.entities,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_full_text:
            result['chunk_text'] = self.chunk_text
        else:
            # Include preview
            result['chunk_preview'] = self.chunk_text[:200] + '...' if len(self.chunk_text) > 200 else self.chunk_text

        return result

    def __repr__(self):
        return f'<DocumentChunk {self.id}: Doc {self.document_id} Chunk {self.chunk_index}>'


class DocumentProcessing(db.Model):
    """Track document processing status and metadata"""
    __tablename__ = 'document_processing'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)

    # Processing status
    status = db.Column(db.String(50), default='pending', index=True)  # pending, processing, completed, failed
    error_message = db.Column(db.Text)

    # PDF extraction
    pdf_extracted = db.Column(db.Boolean, default=False)
    text_quality_score = db.Column(db.Float)  # 0.0-1.0, quality of OCR/extraction

    # Chunking
    chunks_created = db.Column(db.Boolean, default=False)
    chunk_count = db.Column(db.Integer, default=0)
    chunking_strategy = db.Column(db.String(50))  # 'fixed_size', 'semantic', 'paragraph'

    # AI Analysis (for future enhancement)
    ai_summary_generated = db.Column(db.Boolean, default=False)
    key_points_extracted = db.Column(db.Boolean, default=False)

    # Timestamps
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = db.relationship('Document', backref=db.backref('processing', uselist=False, cascade='all, delete-orphan'))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'status': self.status,
            'error_message': self.error_message,
            'pdf_extracted': self.pdf_extracted,
            'text_quality_score': self.text_quality_score,
            'chunks_created': self.chunks_created,
            'chunk_count': self.chunk_count,
            'chunking_strategy': self.chunking_strategy,
            'ai_summary_generated': self.ai_summary_generated,
            'key_points_extracted': self.key_points_extracted,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ScrapeQueue(db.Model):
    """Queue for managing document downloads and processing"""
    __tablename__ = 'scrape_queue'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    document_type = db.Column(db.String(50), nullable=False, index=True)
    action_id = db.Column(db.String(100))  # Link to action if applicable
    meeting_id = db.Column(db.Integer)  # Link to meeting if applicable

    priority = db.Column(db.Integer, default=5, index=True)  # 1=high, 10=low

    # Processing
    status = db.Column(db.String(50), default='pending', index=True)  # pending, in_progress, completed, failed
    attempts = db.Column(db.Integer, default=0)
    max_attempts = db.Column(db.Integer, default=3)

    error_message = db.Column(db.Text)
    result_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))  # Created document

    # Scheduling
    scheduled_for = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_scrape_queue_status_priority', 'status', 'priority'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'url': self.url,
            'document_type': self.document_type,
            'action_id': self.action_id,
            'meeting_id': self.meeting_id,
            'priority': self.priority,
            'status': self.status,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'error_message': self.error_message,
            'result_document_id': self.result_document_id,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<ScrapeQueue {self.id}: {self.url[:50]} ({self.status})>'


class DocumentComment(db.Model):
    """Public comments extracted from PDF documents"""
    __tablename__ = 'document_comments'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)

    # Comment content
    commenter_name = db.Column(db.String(255))
    commenter_organization = db.Column(db.String(255))
    commenter_email = db.Column(db.String(255))
    comment_text = db.Column(db.Text)
    comment_date = db.Column(db.Date, index=True)

    # Location in document
    page_number = db.Column(db.Integer)
    section_reference = db.Column(db.String(255))

    # Categorization (can be done by AI later)
    topics = db.Column(ARRAY(db.Text))
    sentiment = db.Column(db.String(20))  # positive, negative, neutral, mixed
    key_concerns = db.Column(ARRAY(db.Text))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    document = db.relationship('Document', backref=db.backref('extracted_comments', lazy='dynamic', cascade='all, delete-orphan'))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'commenter_name': self.commenter_name,
            'commenter_organization': self.commenter_organization,
            'commenter_email': self.commenter_email,
            'comment_text': self.comment_text,
            'comment_date': self.comment_date.isoformat() if self.comment_date else None,
            'page_number': self.page_number,
            'section_reference': self.section_reference,
            'topics': self.topics,
            'sentiment': self.sentiment,
            'key_concerns': self.key_concerns,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Add search helper functions
def search_documents(query_text, document_types=None, fmp=None, limit=20):
    """
    Full-text search across documents and chunks
    Returns list of dicts with document and relevant chunks
    """
    from src.models.document import Document

    # Build query
    query = db.session.query(Document, DocumentChunk)\
        .join(DocumentChunk, Document.id == DocumentChunk.document_id)\
        .filter(
            DocumentChunk.search_vector.match(query_text, postgresql_regconfig='english')
        )

    if document_types:
        query = query.filter(Document.document_type.in_(document_types))

    if fmp:
        query = query.filter(Document.fmp == fmp)

    # Order by relevance (ts_rank)
    query = query.order_by(
        func.ts_rank(DocumentChunk.search_vector, func.to_tsquery('english', query_text)).desc()
    )

    results = query.limit(limit).all()

    # Format results
    formatted = []
    for doc, chunk in results:
        formatted.append({
            'document': doc.to_dict(),
            'relevant_chunk': chunk.to_dict(include_full_text=True),
            'relevance_score': db.session.query(
                func.ts_rank(chunk.search_vector, func.to_tsquery('english', query_text))
            ).scalar()
        })

    return formatted
