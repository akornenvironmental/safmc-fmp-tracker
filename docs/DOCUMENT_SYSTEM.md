# SAFMC FMP Document Management System

## Overview

Comprehensive system for scraping, indexing, and querying ALL SAFMC Fishery Management Plan documents. This system enables advanced search capabilities and AI-powered document analysis.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SAFMC Website                          │
│  (Briefing Books, Amendments, Meetings, Public Comments)   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Document Scrapers                         │
│  • Briefing Books Scraper                                   │
│  • Amendments Scraper                                       │
│  • Meetings Scraper                                         │
│  • Public Comments Scraper                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Scrape Queue (PostgreSQL)                  │
│  Prioritized queue with retry logic                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               Document Processor Worker                     │
│  • Downloads PDFs                                           │
│  • Extracts text (PyPDF2 + pdfplumber)                     │
│  • Parses metadata                                          │
│  • Classifies document type                                 │
│  • Extracts keywords and entities                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Documents Database (PostgreSQL)                │
│  • fmp_documents: Full document metadata + text             │
│  • document_chunks: Segmented text for semantic search      │
│  • Full-text search with PostgreSQL tsvector                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Document Search API                         │
│  • Full-text search                                         │
│  • Filter by type, FMP, date, status                        │
│  • Retrieve document chunks for context                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              AI Assistant Integration                       │
│  • Semantic search across document chunks                   │
│  • Answer questions using document context                  │
│  • Cite specific documents in responses                     │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### fmp_documents Table

Stores complete document metadata and full text content.

**Key Fields:**
- `document_id` - Unique identifier (MD5 hash)
- `title` - Document title
- `document_type` - Type from DocumentType constants
- `fmp` - Associated Fishery Management Plan
- `amendment_number` - Amendment number if applicable
- `document_date`, `publication_date`, `effective_date` - Key dates
- `status` - Document status (draft, final, approved, etc.)
- `source_url`, `download_url` - URLs
- `full_text` - Complete extracted text
- `summary` - Auto-generated summary
- `keywords[]` - Extracted keywords array
- `species[]` - Relevant species array
- `topics[]` - Topic categorization array
- `search_vector` - PostgreSQL tsvector for full-text search
- `processed`, `indexed` - Processing status flags

### document_chunks Table

Stores document segments for semantic search and AI context.

**Key Fields:**
- `document_id` - Foreign key to fmp_documents
- `chunk_index` - Sequential chunk number
- `chunk_text` - Text segment (typically 500-1000 words)
- `chunk_type` - Type from ChunkType constants
- `section_title` - Section heading if available
- `page_number` - Page reference
- `embedding_vector[]` - Embedding for semantic search (future)
- `metadata` - JSONB for additional context

### document_scrape_queue Table

Manages document scraping queue with retry logic.

**Key Fields:**
- `url` - Document URL to scrape
- `document_type` - Expected document type
- `fmp` - Associated FMP
- `priority` - Priority (1-10, lower is higher)
- `status` - pending/processing/completed/failed
- `attempts` - Number of retry attempts
- `metadata` - JSONB for additional context

## Document Types

### Primary Categories

- **Amendments**: Full FMP amendments
- **Regulatory Amendments**: Faster regulatory updates
- **Framework Amendments**: Streamlined amendments
- **Secretarial Amendments**: NMFS-proposed changes

### Meeting Documents

- **Briefing Books**: Complete meeting materials
- **Meeting Agendas**: Meeting schedules
- **Meeting Transcripts**: Verbatim transcripts
- **Meeting Minutes**: Summary minutes
- **Committee Reports**: Committee findings

### Public Engagement

- **Scoping Documents**: Initial proposal documents
- **Public Hearing Documents**: Public hearing materials
- **Public Comments**: Stakeholder comments
- **Comment Summaries**: Compiled comment summaries

### Environmental Review

- **Environmental Assessments**: EA documents
- **Environmental Impact Statements**: EIS documents

### Regulations

- **Final Rules**: Published final regulations
- **Proposed Rules**: Proposed regulatory changes
- **Regulatory Guides**: Compliance guides

### Scientific

- **Stock Assessment Reports**: SEDAR reports
- **Scientific Reports**: Research findings

## Scrapers

### BaseDocumentScraper

Base class providing common scraping functionality:
- HTTP requests with proper headers
- BeautifulSoup HTML parsing
- PDF link extraction
- Date extraction from text
- Keyword extraction
- FMP classification
- Document ID generation
- Queue management

### BriefingBooksScraper

Scrapes Council meeting briefing books:
- Discovers all briefing book listings
- Extracts meeting metadata (date, type, location)
- Identifies all PDF attachments
- Classifies document types from filenames
- Queues documents for processing

### AmendmentsScraper (TODO)

Scrapes FMP amendments:
- All amendment statuses (scoping → final)
- Amendment numbers and titles
- Associated environmental documents
- Public comment periods

### MeetingsDocumentScraper (TODO)

Scrapes meeting documents beyond briefing books:
- Meeting agendas
- Transcripts
- Minutes
- Motions and votes

## PDF Text Extraction

### PDFExtractor Service

Extracts text content from PDF documents using multiple methods:

**Primary Method: pdfplumber**
- More accurate text extraction
- Table extraction capability
- Layout-aware text ordering
- Better handling of complex PDFs

**Fallback Method: PyPDF2**
- Faster extraction
- Lower resource usage
- Works when pdfplumber fails

**Features:**
- Automatic method selection
- Metadata extraction (title, author, dates)
- Table detection and extraction
- Summary generation
- File size tracking
- Temporary file management

## Document Processing Workflow

1. **Discovery**: Scraper identifies documents on SAFMC website
2. **Queueing**: Documents added to `document_scrape_queue`
3. **Download**: Worker downloads PDF from URL
4. **Extraction**: Text extracted using PDFExtractor
5. **Classification**: Document type, FMP, topics identified
6. **Chunking**: Large documents split into searchable chunks
7. **Indexing**: Full-text search vector generated
8. **Storage**: Saved to `fmp_documents` and `document_chunks`

## Search Capabilities

### Full-Text Search

PostgreSQL tsvector with weighted fields:
- Title: Weight A (highest)
- Description: Weight B
- Summary: Weight C
- Full text: Weight D (lowest)

### Filtered Search

Filter documents by:
- Document type
- FMP category
- Date range
- Status
- Keywords
- Species
- Topics

### Semantic Search (Future)

Using embeddings in `document_chunks`:
- Find similar document sections
- Answer questions with relevant context
- Cite specific passages

## AI Assistant Integration

### Query Processing

1. User asks question via AI Assistant
2. System performs semantic search on document chunks
3. Relevant chunks retrieved as context
4. Claude receives question + document context
5. Claude generates answer with citations

### Example Queries

- "Which FMPs have Environmental Impact Statements vs Assessments?"
- "What council members voted in favor of Amendment 44?"
- "What stakeholders commented on the scoping document for dolphin wahoo?"
- "Show me all amendments that address size limits"
- "What are the current catch limits for red snapper?"

## File Structure

```
src/
├── constants/
│   └── document_types.py      # Document type constants
├── scrapers/
│   ├── base_document_scraper.py       # Base scraper class
│   ├── briefing_books_scraper.py      # Briefing books
│   ├── amendments_scraper.py          # Amendments (TODO)
│   └── meetings_document_scraper.py   # Meetings (TODO)
├── services/
│   ├── pdf_extractor.py               # PDF text extraction
│   ├── document_processor.py          # Document processing worker (TODO)
│   └── document_chunker.py            # Text chunking (TODO)
├── routes/
│   └── document_routes.py             # Document API endpoints (TODO)
└── models/
    ├── fmp_document.py                # Document model (TODO)
    └── document_chunk.py              # Chunk model (TODO)

migrations/
└── create_fmp_documents.py    # Database schema migration
```

## Dependencies

### Required Python Packages

```
PyPDF2>=3.0.0          # PDF text extraction (fallback)
pdfplumber>=0.10.0     # PDF text extraction (primary)
beautifulsoup4>=4.12.0 # HTML parsing
requests>=2.31.0       # HTTP requests
python-dateutil>=2.8.0 # Date parsing
```

Add to `requirements.txt`:
```bash
PyPDF2==3.0.1
pdfplumber==0.10.3
```

## Usage

### Running Scrapers

```python
from src.scrapers.briefing_books_scraper import BriefingBooksScraper

# Scrape briefing books
scraper = BriefingBooksScraper()
results = scraper.scrape_briefing_books(limit=10)

print(f"Found: {results['books_found']} books")
print(f"Queued: {results['documents_queued']} documents")
```

### Extracting PDF Text

```python
from src.services.pdf_extractor import PDFExtractor

extractor = PDFExtractor()

# Extract from URL
result = extractor.extract_from_url('https://safmc.net/path/to/document.pdf')

if result['success']:
    print(f"Extracted {len(result['text'])} characters")
    print(f"Pages: {result['page_count']}")
    print(f"Tables: {result.get('table_count', 0)}")
```

## Implementation Status

✅ **Completed:**
- Database schema design
- Document type constants
- Base scraper infrastructure
- Briefing books scraper
- PDF extraction service
- Documentation

🔄 **In Progress:**
- Document processor worker
- Document API endpoints

📋 **TODO:**
- Amendments scraper
- Meetings document scraper
- Document chunking service
- Search API implementation
- AI Assistant integration
- Frontend document viewer

## Future Enhancements

1. **Semantic Search**: Implement embedding vectors for similarity search
2. **OCR Support**: Extract text from scanned PDFs
3. **Entity Recognition**: Extract names, dates, regulations
4. **Automated Categorization**: ML-based document classification
5. **Change Detection**: Track document updates over time
6. **Citation Graph**: Build relationship graph between documents
7. **Summarization**: Auto-generate executive summaries
8. **Translation**: Support multiple languages

## Performance Considerations

- **Rate Limiting**: 1-2 second delay between requests
- **Batch Processing**: Process documents in background queue
- **Caching**: Cache extracted text to avoid reprocessing
- **Incremental Updates**: Only scrape new/modified documents
- **Resource Management**: Clean up temporary PDF files
- **Database Indexing**: Optimize search performance with proper indices

## Monitoring

Track these metrics:
- Documents scraped per day
- Extraction success rate
- Processing time per document
- Queue depth
- Search query performance
- Storage usage
