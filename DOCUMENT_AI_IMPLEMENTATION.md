# SAFMC Document AI Analysis System - Implementation Guide

## Overview

This system enables AI-powered analysis of all SAFMC documents including amendments, environmental impact statements, meeting transcripts, briefing books, and public comments. All PDFs are processed, stored, and made queryable at temperature=0 for accurate information retrieval.

## Architecture

### Data Flow
```
SAFMC Website → Scraper → PDF Download → Text Extraction → Chunking → PostgreSQL → AI Query
```

### Storage Strategy
- **Primary Storage**: PostgreSQL database with full text content
- **Chunking**: Documents split into 3000-character chunks with 200-character overlap
- **Search**: PostgreSQL full-text search with ts_vector indexes
- **AI Access**: Chunks provided as context to Claude API at temperature=0

## Database Schema

### Core Tables Created

1. **`document_chunks`** - Text chunks optimized for AI context windows
   - Stores 3000-char chunks with overlap for context preservation
   - Includes section titles and heading hierarchy
   - Full-text search vectors for fast retrieval
   - Page number tracking

2. **`document_processing`** - Processing status and metadata
   - Tracks PDF extraction quality
   - Chunking progress and strategy
   - Error handling and retry logic

3. **`scrape_queue`** - Document download queue
   - Priority-based processing
   - Retry logic for failed downloads
   - Links to actions/meetings

4. **`document_comments`** - Extracted public comments
   - Parses comments from PDFs
   - Tracks commenter info and sentiment
   - Links to source document and page number

### Enhanced Existing Table
- **`documents`** table already exists and will be used as-is
- New tables link to it via foreign keys

## Components Built

### 1. PDF Processing Service (`src/services/pdf_processor.py`)

**Features:**
- PDF download with retry logic
- Text extraction using pdfplumber (primary) and PyPDF2 (fallback)
- Intelligent chunking that preserves document structure
- Section detection and hierarchy extraction
- Keyword extraction
- Quality scoring for OCR/extraction

**Key Methods:**
```python
processor = PDFProcessor(chunk_size=3000, chunk_overlap=200)

# Download and process
document, error = process_pdf_from_url(url, {
    'title': 'Amendment 49',
    'document_type': 'amendment',
    'fmp': 'Snapper Grouper',
    'action_id': 'sg-am-49'
})

# Manual processing
success, error = processor.process_document(document_id, pdf_path)
```

### 2. Enhanced Document Models (`src/models/document_enhanced.py`)

**Models:**
- `DocumentChunk` - Individual text chunks
- `DocumentProcessing` - Processing metadata
- `ScrapeQueue` - Download queue management
- `DocumentComment` - Extracted comments

**Search Function:**
```python
from src.models.document_enhanced import search_documents

results = search_documents(
    query_text="red snapper rebuilding",
    document_types=['amendment', 'environmental_analysis'],
    fmp='Snapper Grouper',
    limit=20
)
```

## Next Steps to Complete

### Phase 2: SAFMC Website Scraper (Next Priority)

Create `src/scrapers/safmc_document_scraper.py`:

**Targets:**
1. **Amendment Pages** - https://safmc.net/amendments/[fmp-name]
   - Primary amendment PDFs
   - Environmental analyses
   - Regulatory impact reviews
   - Public hearing documents

2. **Meeting Pages** - https://safmc.net/meetings/
   - Meeting transcripts
   - Briefing book PDFs
   - Supplemental materials
   - Public comment summaries

3. **Public Comment Pages**
   - Comment period documents
   - Individual comment letters
   - Comment summaries

**Key Functions Needed:**
```python
def scrape_amendment_documents(amendment_url):
    """Scrape all PDFs from an amendment page"""
    pass

def scrape_meeting_documents(meeting_url):
    """Scrape transcripts and briefing materials"""
    pass

def discover_new_documents():
    """Check SAFMC site for new documents since last scrape"""
    pass

def queue_document_for_processing(url, metadata):
    """Add document to scrape queue"""
    pass
```

### Phase 3: AI Query Endpoint

Create `src/routes/ai_assistant.py`:

**Endpoint:** `POST /api/ai/query`

**Request:**
```json
{
  "query": "What are the rebuilding timelines for red snapper?",
  "context_filters": {
    "document_types": ["amendment", "stock_assessment"],
    "fmp": "Snapper Grouper",
    "date_range": {"start": "2020-01-01", "end": "2024-12-31"}
  },
  "temperature": 0
}
```

**Response:**
```json
{
  "answer": "Based on Amendment 49...",
  "sources": [
    {
      "document_id": 123,
      "document_title": "Snapper Grouper Amendment 49",
      "chunk_index": 5,
      "page_numbers": [12, 13],
      "excerpt": "...relevant text...",
      "url": "https://safmc.net/..."
    }
  ],
  "tokens_used": 1543
}
```

**Implementation:**
1. Parse user query
2. Search document_chunks table with full-text search
3. Retrieve top 10 most relevant chunks
4. Build Claude API prompt with chunks as context
5. Query Claude API at temperature=0
6. Return answer with source citations

### Phase 4: Weekly Automated Scraping

Create `src/services/scheduled_scraper.py`:

**Using APScheduler (already in requirements.txt):**
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', day_of_week='mon', hour=2)
def weekly_document_scan():
    """Run every Monday at 2 AM"""
    discover_and_queue_new_documents()
    process_queue()

scheduler.start()
```

## Database Migration

### Step 1: Create Tables

```bash
# Run the SQL migration
psql $DATABASE_URL < migrations/create_documents_tables.sql
```

### Step 2: Update Models Import

Edit `src/models/__init__.py` to include new models:
```python
from src.models.document_enhanced import (
    DocumentChunk,
    DocumentProcessing,
    ScrapeQueue,
    DocumentComment
)
```

### Step 3: Test Setup

```python
# In Python shell
from app import app
from src.config.extensions import db
from src.models.document_enhanced import *

with app.app_context():
    db.create_all()
```

## API Endpoints to Create

### Document Management

```
GET  /api/documents - List all documents with pagination
GET  /api/documents/:id - Get document details
POST /api/documents/upload - Manual document upload
GET  /api/documents/:id/chunks - Get document chunks
GET  /api/documents/search - Full-text search

POST /api/scrape/queue - Add URL to scrape queue
GET  /api/scrape/status - Get scraping status
POST /api/scrape/trigger - Manually trigger scraping

POST /api/ai/query - AI-powered document query
POST /api/ai/summarize - Summarize a specific document
POST /api/ai/compare - Compare multiple documents
```

## Configuration

### Environment Variables Needed

```bash
# .env additions
CLAUDE_API_KEY=sk-ant-...  # Already exists
SCRAPING_ENABLED=true
SCRAPING_USER_AGENT=SAFMC-FMP-Tracker/1.0
SCRAPING_DELAY_SECONDS=2  # Politeness delay between requests
MAX_CONCURRENT_SCRAPES=3
PDF_STORAGE_PATH=/tmp/safmc_pdfs  # Temporary PDF storage
```

## Testing Strategy

### Unit Tests

```python
# tests/test_pdf_processor.py
def test_pdf_download():
    processor = PDFProcessor()
    success, error = processor.download_pdf(TEST_PDF_URL, '/tmp/test.pdf')
    assert success

def test_text_extraction():
    processor = PDFProcessor()
    text, pages, quality, has_images = processor.extract_text_from_pdf('test.pdf')
    assert len(text) > 0
    assert pages > 0

def test_chunking():
    processor = PDFProcessor()
    chunks = processor.create_chunks(SAMPLE_TEXT, 10)
    assert len(chunks) > 0
    assert all(c['chunk_size'] <= 3200 for c in chunks)  # With overlap
```

### Integration Tests

```python
# tests/test_document_pipeline.py
def test_full_pipeline():
    # Download, process, chunk, store
    doc, error = process_pdf_from_url(TEST_URL, TEST_METADATA)
    assert doc is not None
    assert doc.chunks.count() > 0
```

## Performance Considerations

### Database Indexes
- Full-text search indexes on `search_vector` columns
- Indexes on foreign keys (document_id, action_id, etc.)
- Composite index on (status, priority) for scrape_queue

### Optimization
- **Batch Processing**: Process multiple PDFs in parallel
- **Caching**: Cache frequently accessed chunks
- **Compression**: Consider compressing full_text if needed
- **Pagination**: Always paginate large result sets

### Estimated Storage

**Per Document:**
- Original PDF: Not stored (only URL)
- Full text: ~2-5 MB for 200-page doc
- Chunks: ~50-100 chunks per doc
- Total per doc: ~3-8 MB

**For 1000 Documents:**
- Approximately 3-8 GB in database
- PostgreSQL handles this easily

## Security Considerations

1. **Rate Limiting**: Implement rate limits on AI query endpoint
2. **Authentication**: Require auth for scraping triggers
3. **Input Validation**: Sanitize all URLs and user queries
4. **API Key Protection**: Never expose Claude API key to frontend
5. **SQL Injection**: Use parameterized queries (already done with SQLAlchemy)

## Monitoring & Logging

### Metrics to Track
- Documents processed per day
- Processing success/failure rate
- Average processing time per document
- AI query response times
- Token usage for Claude API

### Logging Points
```python
logger.info(f"Processing document {doc_id}")
logger.error(f"PDF extraction failed: {error}")
logger.warning(f"Low quality extraction (score: {quality_score})")
```

## Cost Estimation

### Claude API Usage
- **Input tokens**: ~10K tokens per query (context + question)
- **Output tokens**: ~500-1000 tokens per answer
- **Cost per query**: ~$0.10-0.15 with Claude Sonnet
- **Monthly (1000 queries)**: ~$100-150

### Optimization
- Cache common queries
- Use smaller context windows when possible
- Implement query deduplication

## Timeline

### Week 1: Foundation ✅ COMPLETE
- [x] Database schema design
- [x] Enhanced models
- [x] PDF processor service

### Week 2: Scraping
- [ ] SAFMC website scraper
- [ ] Amendment page parser
- [ ] Meeting page parser
- [ ] Queue management

### Week 3: AI Integration
- [ ] AI query endpoint
- [ ] Context retrieval logic
- [ ] Claude API integration
- [ ] Source citation system

### Week 4: Automation & Polish
- [ ] Weekly scheduled scraping
- [ ] Admin dashboard for monitoring
- [ ] Testing and refinement
- [ ] Documentation

## Usage Examples

### Example 1: Process a Single Document

```python
from src.services.pdf_processor import process_pdf_from_url

document, error = process_pdf_from_url(
    url='https://safmc.net/wp-content/uploads/2024/SG-Am-49.pdf',
    document_data={
        'title': 'Snapper Grouper Amendment 49',
        'document_type': 'amendment',
        'fmp': 'Snapper Grouper',
        'action_id': 'sg-am-49',
        'document_date': '2024-03-15'
    }
)

if document:
    print(f"Processed: {document.id}")
    print(f"Pages: {document.page_count}")
    print(f"Chunks: {document.chunks.count()}")
```

### Example 2: Search Documents

```python
from src.models.document_enhanced import search_documents

results = search_documents(
    query_text="commercial fishing allocation",
    document_types=['amendment'],
    fmp='Snapper Grouper',
    limit=10
)

for result in results:
    print(f"{result['document']['title']}")
    print(f"Relevance: {result['relevance_score']}")
    print(f"Excerpt: {result['relevant_chunk']['chunk_preview']}")
```

### Example 3: AI Query (Future)

```python
# Frontend usage
const response = await fetch('/api/ai/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "What are the latest red snapper management measures?",
    context_filters: {
      fmp: "Snapper Grouper",
      document_types: ["amendment", "regulatory_action"]
    }
  })
});

const data = await response.json();
console.log(data.answer);
console.log(data.sources);
```

## Support & Maintenance

### Common Issues

**Issue: Low extraction quality**
- Solution: PDFs may be scanned images - implement OCR fallback

**Issue: Chunking breaks mid-sentence**
- Solution: Adjust chunk_overlap or improve sentence boundary detection

**Issue: Slow search performance**
- Solution: Ensure search_vector indexes are created, consider materialized views

### Future Enhancements

1. **OCR Support**: Add tesseract for scanned PDFs
2. **Image Analysis**: Extract and analyze charts/tables with vision AI
3. **Embeddings**: Add vector embeddings for semantic search
4. **Multilingual**: Support Spanish documents
5. **Document Comparison**: Side-by-side amendment comparison
6. **Citation Network**: Build graph of document citations

---

## Ready to Deploy

All core components for Phase 1 are complete:
- ✅ Database schema designed
- ✅ Models created
- ✅ PDF processor implemented
- ✅ Chunking strategy implemented

**Next Priority**: Build the SAFMC website scraper to start ingesting documents!
