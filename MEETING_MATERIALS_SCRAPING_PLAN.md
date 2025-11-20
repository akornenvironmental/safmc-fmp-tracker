# SAFMC Meeting Materials Comprehensive Scraping & Analysis Plan

## Overview

Build a complete system to scrape, process, analyze, and query ALL council meeting materials including:
- Briefing books (PDFs)
- Agendas & overviews
- Committee reports
- Decision documents
- Scientific reports (SEDAR, SSC)
- Presentations
- Data analyses (Excel files)
- Public comments
- Draft amendments
- Staff reports

**Target Example**: https://safmc.net/events/june-2025-council-meeting/ (110+ documents)

---

## System Architecture

### Phase 1: Document Discovery & Download ✅
```
Meeting Page URL
    ↓
HTML Parser
    ↓
Extract all document URLs
    ↓
Download PDFs/Excel files
    ↓
Store in S3/local storage
    ↓
Create Document records in database
```

### Phase 2: Content Extraction 📄
```
PDF/Excel File
    ↓
Text Extraction (PyPDF2, pdfplumber, or python-docx)
    ↓
Clean & normalize text
    ↓
Store full_text in Document model
    ↓
Create DocumentChunks for AI analysis
```

### Phase 3: AI Analysis & Entity Extraction 🤖
```
Document Text
    ↓
AI Analysis (Claude API)
    ↓
Extract:
  - Summary
  - Key topics/themes
  - Mentioned species
  - Mentioned amendments/actions
  - Geographic locations
  - Stakeholder groups
    ↓
Store in Document metadata
    ↓
Link to Actions, Meetings, Amendments
```

### Phase 4: Search & Query 🔍
```
User Query
    ↓
Full-text search (PostgreSQL)
    ↓
AI-powered semantic search
    ↓
Return relevant documents + chunks
    ↓
Generate AI summary of results
```

---

## Database Schema (Already Exists!)

### Core Tables

✅ **documents** - Main document metadata
- id, title, document_type, fmp, file_url, file_type
- full_text, summary, topics
- related_action_id, related_meeting_id
- created_at, updated_at

✅ **document_chunks** - Text chunks for AI context
- id, document_id, chunk_index
- chunk_text, chunk_size, token_count, page_numbers
- section_title, heading_hierarchy
- keywords, entities
- search_vector (full-text search)

✅ **document_processing** - Processing status tracking
- id, document_id, status
- pdf_extracted, text_quality_score
- chunks_created, chunk_count
- ai_summary_generated, key_points_extracted

✅ **action_documents** - Link documents to actions
✅ **meeting_documents** - Link documents to meetings

---

## Implementation Components

### 1. Meeting Page Scraper
**File**: `src/scrapers/meeting_materials_scraper.py`

**Responsibilities**:
- Fetch council meeting page HTML
- Extract all document URLs
- Parse document metadata from filenames
  - Committee code (FC1, SG, MC, HE_S)
  - Attachment number (A1, A2a, etc.)
  - Date (202506, 20250613)
  - Document type (pdf, xlsx)
- Classify document types:
  - Agenda/Overview
  - Committee Report
  - Attachment
  - Public Comment
  - Decision Document
  - etc.
- Download files
- Create Document records

**Key Functions**:
```python
def scrape_meeting_materials(meeting_url: str) -> Dict:
    """Scrape all materials from a meeting page"""

def parse_document_metadata(url: str, filename: str) -> Dict:
    """Extract metadata from URL/filename"""

def classify_document_type(filename: str, context: str) -> str:
    """Classify document type"""

def download_document(url: str, save_path: str) -> bool:
    """Download document file"""
```

### 2. PDF Text Extractor
**File**: `src/services/pdf_extractor.py`

**Responsibilities**:
- Extract text from PDFs
- Handle OCR for scanned documents
- Preserve structure (headings, sections)
- Extract page numbers
- Quality assessment

**Libraries**:
- `pdfplumber` - Best for text extraction with layout
- `PyPDF2` - Fallback
- `pytesseract` - OCR for scanned docs

**Key Functions**:
```python
def extract_pdf_text(file_path: str) -> Dict:
    """Extract text with metadata"""
    return {
        'full_text': str,
        'pages': List[Dict],  # page_number, text
        'quality_score': float,
        'is_scanned': bool
    }
```

### 3. Document Chunker
**File**: `src/services/document_chunker.py`

**Responsibilities**:
- Split documents into AI-sized chunks
- Preserve context (headings, sections)
- Generate search vectors
- Extract keywords/entities

**Chunking Strategies**:
1. **Fixed Size** - 4000-8000 chars per chunk
2. **Semantic** - Split on section boundaries
3. **Paragraph** - Split on paragraph breaks

**Key Functions**:
```python
def chunk_document(document_id: int, strategy: str = 'semantic') -> int:
    """Chunk document and create DocumentChunk records"""

def extract_chunk_metadata(chunk_text: str) -> Dict:
    """Extract keywords, entities from chunk"""
```

### 4. AI Analysis Service
**File**: `src/services/document_analysis.py`

**Responsibilities**:
- Generate document summaries
- Extract key points
- Identify topics/themes
- Find entity mentions (species, actions, locations)
- Link to existing database entities

**Key Functions**:
```python
def analyze_document_with_ai(document_id: int) -> Dict:
    """Full AI analysis of document"""

def generate_summary(text: str) -> str:
    """Generate concise summary"""

def extract_entities(text: str) -> Dict:
    """Extract species, actions, locations, etc."""

def link_to_actions(document_id: int) -> List[str]:
    """Find related actions/amendments"""
```

### 5. Search Service
**File**: `src/services/document_search.py`

**Responsibilities**:
- Full-text search across documents
- Semantic search using AI
- Return relevant chunks
- Generate answer from context

**Key Functions**:
```python
def search_documents(query: str, filters: Dict = None) -> List[Dict]:
    """Search documents and return results"""

def ai_query_documents(question: str) -> str:
    """Ask a question, get AI-generated answer"""
```

---

## Document Type Classification

Based on URL/filename patterns:

| Pattern | Type | Example |
|---------|------|---------|
| `*_agendaoverview_*` | Agenda/Overview | `sgcomsc_agendaoverview_202506-pdf` |
| `*_summaryreport_*` | Committee Report | `fc1_summaryreport_202506_final-pdf` |
| `*_a\d+_*` or `*_a\d+[a-z]_*` | Attachment | `fc1_a1a_noaa-ole-sed-council-report-pdf` |
| `*comment*` | Public Comment | `shrimp-amendment-12-comment_merrifield-pdf` |
| `*decision*` | Decision Document | `fc1_a4_for-hire-reporting-improvement_decisiondocument-pdf` |
| `*workplan*` | Workplan | `fc2_a1_safmc_workplanq3_202509-xlsx` |
| `*meeting*minutes*` | Meeting Minutes | `mc_meetingminutes_202503-pdf` |
| `*_apreport_*` | Advisory Panel Report | `mc_a1a_mcapreport_202503-pdf` |
| `*sedar*` or `*ssc*` | Scientific Report | `ssc-report-sedar78-spanish-mackerel-pdf` |
| `*presentation*` | Presentation | `staff-presentation-coral-amendment-11-pdf` |

### Committee/Session Codes

| Code | Meaning |
|------|---------|
| FC1 | Full Council Session 1 |
| FC2 | Full Council Session 2 |
| SG | Snapper Grouper Committee |
| SGCOMSC | SG Commercial Subcommittee |
| MC | Mackerel Cobia Committee |
| HE_S | Habitat & Ecosystem / Shrimp Joint |
| EXCOM | Executive Committee |
| DW | Dolphin Wahoo |

---

## API Endpoints

### Trigger Meeting Scrape
```
POST /api/meetings/:meetingId/scrape-materials

Response:
{
  "success": true,
  "documents_found": 110,
  "documents_downloaded": 110,
  "documents_processed": 85,
  "errors": []
}
```

### Get Meeting Documents
```
GET /api/meetings/:meetingId/documents

Response:
{
  "meeting": {...},
  "documents": [
    {
      "id": 123,
      "title": "Snapper Grouper Committee Agenda",
      "document_type": "Agenda/Overview",
      "file_url": "...",
      "summary": "...",
      "topics": ["Black Sea Bass", "Commercial Fishery"]
    }
  ]
}
```

### Search Documents
```
GET /api/documents/search?q=black+sea+bass&meeting_id=123

Response:
{
  "total": 15,
  "documents": [...],
  "chunks": [...]  // Relevant chunks with highlights
}
```

### AI Query
```
POST /api/documents/query
{
  "question": "What are the proposed changes to black sea bass regulations?",
  "meeting_id": 123
}

Response:
{
  "answer": "Based on the June 2025 meeting materials...",
  "sources": [
    {"document_id": 456, "chunk_id": 789, "relevance": 0.95}
  ]
}
```

---

## Processing Pipeline

### Automated Flow

```
New Meeting Detected
    ↓
Scrape meeting page
    ↓
Download all documents (parallel)
    ↓
FOR EACH document:
    ↓
    Extract text (PDF/Excel)
    ↓
    Create chunks
    ↓
    Generate AI summary
    ↓
    Extract entities
    ↓
    Link to actions/amendments
    ↓
Mark processing complete
```

### Manual Triggers

- Admin can manually trigger scraping for any meeting
- Can re-process documents if extraction fails
- Can force AI re-analysis with updated prompts

---

## File Storage Strategy

### Option 1: Local Storage (Development)
```
/Users/akorn/safmc-fmp-tracker/storage/
  documents/
    meetings/
      june-2025/
        fc1_agendaoverview_202506.pdf
        sg_summaryreport_202506.pdf
        ...
```

### Option 2: AWS S3 (Production)
```
s3://safmc-fmp-tracker-docs/
  meetings/
    2025-06-june/
      fc1_agendaoverview_202506.pdf
      ...
```

Store S3 URL in `documents.file_url`

---

## Performance Considerations

### Parallel Processing
- Download documents in parallel (ThreadPoolExecutor)
- Process PDFs in parallel
- Chunk creation can be batched

### Caching
- Cache extracted text to avoid re-processing
- Cache AI summaries (expensive)
- Use document processing status to skip completed docs

### Rate Limiting
- Respect safmc.net (no more than 2 req/sec)
- Claude API rate limits
- Queue long-running tasks (Celery/background jobs)

---

## AI Prompts

### Document Summary
```
Analyze this fishery management council meeting document and provide:

1. A 2-3 sentence summary
2. Key topics discussed (as keywords)
3. Any species mentioned
4. Any amendments/actions referenced
5. Geographic areas mentioned

Document text:
{text}
```

### Entity Extraction
```
Extract the following from this document:

- Species names (common and scientific)
- Amendment/regulation numbers (e.g., "SG Reg 37", "Coral 11")
- Locations (states, regions, management areas)
- Stakeholder groups (commercial, recreational, for-hire, NGO)
- Numeric values (catch limits, size limits, quotas)

Document text:
{text}
```

### Question Answering
```
Based on the following document chunks from a fishery management meeting, answer this question:

Question: {question}

Context:
{chunks}

Provide a clear, concise answer citing specific sections where relevant.
```

---

## Testing Plan

### Unit Tests
- URL extraction from HTML
- Document metadata parsing
- PDF text extraction quality
- Chunking strategies
- Entity extraction accuracy

### Integration Tests
- Full scrape → download → process pipeline
- AI analysis end-to-end
- Search functionality
- Document linking to actions/meetings

### Data Quality
- Monitor text extraction quality scores
- Review AI-generated summaries
- Validate entity linkages
- Check for duplicate documents

---

## Next Steps

1. ✅ Analyze meeting page structure
2. ✅ Design system architecture
3. 🚧 Implement meeting materials scraper
4. 🚧 Implement PDF text extractor
5. 🚧 Implement document chunker
6. 🚧 Implement AI analysis service
7. 🚧 Create API endpoints
8. 🚧 Build frontend document browser
9. 🚧 Test with June 2025 meeting (110 docs)
10. 🚧 Deploy and monitor

---

## Success Metrics

- **Document Coverage**: 95%+ of meeting documents scraped
- **Text Quality**: 90%+ quality score on extractions
- **Processing Speed**: <2 min per document average
- **Search Relevance**: User can find relevant info in <3 searches
- **AI Accuracy**: Summaries/entities validated by domain experts

---

## Files to Create

```
src/scrapers/
  └── meeting_materials_scraper.py

src/services/
  ├── pdf_extractor.py
  ├── document_chunker.py
  ├── document_analysis.py
  └── document_search.py

src/routes/
  └── document_routes.py (enhance existing)

storage/
  └── documents/
      └── meetings/

tests/
  ├── test_meeting_scraper.py
  ├── test_pdf_extraction.py
  └── test_document_search.py

MEETING_MATERIALS_SCRAPING_PLAN.md (this file)
```

---

This comprehensive system will make ALL council meeting materials searchable, analyzable, and connected to the rest of the FMP Tracker data!
