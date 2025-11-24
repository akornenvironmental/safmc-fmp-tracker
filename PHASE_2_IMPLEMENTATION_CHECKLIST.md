# Phase 2: Vector Search - Implementation Checklist

**Goal:** Enable natural language queries across all SAFMC documents
**Timeline:** 5 days
**Cost:** ~$0.20 setup + $5-10/month

---

## Pre-Implementation Setup

### Step 1: Service Signups (30 minutes)

- [ ] **OpenAI API**
  - Sign up at: https://platform.openai.com/
  - Add payment method (required even for small usage)
  - Generate API key
  - Note: Usage will be ~$0.02 per 1,000 documents
  - Model: `text-embedding-3-small` (1536 dimensions, $0.02/1M tokens)

- [ ] **Pinecone Vector Database**
  - Sign up at: https://www.pinecone.io/
  - Choose "Starter" (free) plan - 1M vectors, plenty for SAFMC
  - Create new index: `safmc-documents`
  - Dimensions: 1536 (matches OpenAI embedding model)
  - Metric: Cosine similarity
  - Note API key and environment (e.g., `us-east-1-aws`)

- [ ] **Add Environment Variables to Render**
  ```
  OPENAI_API_KEY=sk-...
  PINECONE_API_KEY=...
  PINECONE_ENVIRONMENT=us-east-1-aws
  ```

---

## Day 1: Dependencies & Document Processor

### Step 2: Install Dependencies (15 minutes)

- [ ] Add to `requirements.txt`:
  ```
  openai==1.6.1
  pinecone-client==3.0.0
  pypdf2==3.0.1
  pdfplumber==0.10.3
  tiktoken==0.5.2
  ```

- [ ] Test locally:
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Commit and push to trigger deployment

### Step 3: Create Document Processor Service (4 hours)

- [ ] Create `src/services/document_processor.py`
  - [ ] `__init__` - Initialize OpenAI and Pinecone clients
  - [ ] `extract_text_from_pdf(pdf_path)` - Extract text using pdfplumber/PyPDF2
  - [ ] `chunk_text(text, chunk_size=500, overlap=50)` - Split into overlapping chunks
  - [ ] `generate_embedding(text)` - Call OpenAI API for embeddings
  - [ ] `process_document(document_id, document_path, metadata)` - Full pipeline
  - [ ] `search(query, top_k=5, filter=None)` - Vector similarity search

- [ ] Test document processor locally:
  ```python
  from src.services.document_processor import DocumentProcessor

  processor = DocumentProcessor()
  # Test with a sample PDF
  processor.process_document(1, "test.pdf", {"title": "Test", "fmp": "Snapper Grouper"})

  # Test search
  results = processor.search("red snapper size limits")
  print(results)
  ```

---

## Day 2: Database & Queue Processor

### Step 4: Database Schema Updates (30 minutes)

- [ ] Create migration file: `migrations/add_document_processing_fields.sql`
  ```sql
  ALTER TABLE fmp_documents ADD COLUMN IF NOT EXISTS processed BOOLEAN DEFAULT FALSE;
  ALTER TABLE fmp_documents ADD COLUMN IF NOT EXISTS chunks_created INTEGER;
  ALTER TABLE fmp_documents ADD COLUMN IF NOT EXISTS processing_error TEXT;
  ALTER TABLE fmp_documents ADD COLUMN IF NOT EXISTS processed_date TIMESTAMP;
  ```

- [ ] Update `src/models/fmp_document.py`:
  ```python
  processed = db.Column(db.Boolean, default=False)
  chunks_created = db.Column(db.Integer)
  processing_error = db.Column(db.Text)
  processed_date = db.Column(db.DateTime)
  ```

- [ ] Run migration (create script or run SQL directly on production DB)

### Step 5: Background Queue Processor (3 hours)

- [ ] Create `src/services/document_queue_processor.py`
  - [ ] `__init__` - Initialize DocumentProcessor
  - [ ] `process_queue(batch_size=10)` - Process unprocessed documents
  - [ ] `download_pdf(url)` - Download PDF to temp file
  - [ ] `reprocess_failed()` - Retry failed documents
  - [ ] Error handling and logging

- [ ] Test queue processor:
  ```python
  from src.services.document_queue_processor import DocumentQueueProcessor

  processor = DocumentQueueProcessor()
  processor.process_queue(batch_size=5)  # Test with 5 docs
  ```

---

## Day 3: AI Service Integration

### Step 6: Update AI Service (2 hours)

- [ ] Modify `src/services/ai_service.py`:
  - [ ] Add method: `answer_question_with_context(question, fmp_filter=None)`
  - [ ] Search vector DB for relevant chunks
  - [ ] Build context from top 5 chunks
  - [ ] Include document citations in prompt
  - [ ] Pass to Claude with context
  - [ ] Return answer + sources

- [ ] Test AI service with context:
  ```python
  from src.services.ai_service import AIService

  ai = AIService()
  result = ai.answer_question_with_context("What are the size limits for red snapper?")
  print(result['answer'])
  print(result['sources'])
  ```

---

## Day 4: API Endpoints & Testing

### Step 7: Create API Endpoints (2 hours)

- [ ] Add to `src/routes/api_routes.py`:

  **Admin Endpoint - Process Document Queue:**
  ```python
  @bp.route('/documents/process-queue', methods=['POST'])
  @require_admin
  def process_document_queue():
      # Process batch_size documents
      # Return success/failure counts
  ```

  **Public Endpoint - Semantic Search:**
  ```python
  @bp.route('/documents/search', methods=['POST'])
  def search_documents():
      # Search by natural language query
      # Optional FMP filter
      # Return relevant chunks with scores
  ```

  **Enhanced Endpoint - AI with Context:**
  ```python
  @bp.route('/ai/query', methods=['POST'])
  def ai_query_with_context():
      # Get question from body
      # Search vector DB
      # Call AI with context
      # Return answer + citations
  ```

### Step 8: Test API Endpoints (1 hour)

- [ ] Test process queue endpoint:
  ```bash
  curl -X POST https://safmc-fmp-tracker.onrender.com/api/documents/process-queue \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"batch_size": 5}'
  ```

- [ ] Test search endpoint:
  ```bash
  curl -X POST https://safmc-fmp-tracker.onrender.com/api/documents/search \
    -H "Content-Type: application/json" \
    -d '{"query": "red snapper size limits", "fmp": "Snapper Grouper"}'
  ```

- [ ] Test AI endpoint:
  ```bash
  curl -X POST https://safmc-fmp-tracker.onrender.com/api/ai/query \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"question": "What are the current regulations for red snapper?"}'
  ```

---

## Day 5: Document Processing & Frontend

### Step 9: Process All Documents (2 hours)

- [ ] Process initial batch (10 documents):
  ```bash
  curl -X POST .../api/documents/process-queue \
    -d '{"batch_size": 10}'
  ```

- [ ] Verify in Pinecone dashboard:
  - Check vector count increases
  - Verify metadata is correct

- [ ] Process all documents in batches:
  ```bash
  # Process 50 at a time to avoid timeouts
  for i in {1..10}; do
    curl -X POST .../api/documents/process-queue -d '{"batch_size": 50}'
    sleep 300  # Wait 5 minutes between batches
  done
  ```

- [ ] Monitor:
  - Check processing errors
  - Verify chunk counts
  - Check Pinecone vector count

### Step 10: Frontend Integration (2 hours)

- [ ] Update `AIAssistant.jsx`:
  - [ ] Show "Searching documents..." state
  - [ ] Display citations/sources below answer
  - [ ] Add links to source documents
  - [ ] Show relevance scores (optional)

- [ ] Add example queries specific to SAFMC:
  ```javascript
  const exampleQueries = [
    'What amendments addressed red snapper in 2020?',
    'Show me public comments about recreational limits',
    'What are the current size limits for gag grouper?',
    'Find documents discussing stock assessment uncertainty',
    'What is the status of Dolphin Wahoo Amendment 10?'
  ];
  ```

- [ ] Test in browser:
  - [ ] Ask various questions
  - [ ] Verify citations appear
  - [ ] Check document links work
  - [ ] Test filtering by FMP

---

## Testing & Validation

### Step 11: End-to-End Testing (1 hour)

- [ ] **Test Query Accuracy:**
  ```
  Query: "What are the size limits for red snapper?"
  Expected: Should find relevant amendments/regulations
  Citations: Should include Snapper Grouper amendments
  ```

- [ ] **Test FMP Filtering:**
  ```
  Query: "Catch limits" + FMP: "Dolphin Wahoo"
  Expected: Only Dolphin Wahoo documents
  ```

- [ ] **Test Historical Queries:**
  ```
  Query: "Amendments approved in 2019"
  Expected: Documents from 2019 timeframe
  ```

- [ ] **Test Complex Queries:**
  ```
  Query: "How has red snapper management changed over time?"
  Expected: Multiple amendments across years
  ```

### Step 12: Performance Testing (30 minutes)

- [ ] Measure search latency (target: < 500ms)
- [ ] Test with 10+ concurrent users
- [ ] Monitor OpenAI API costs
- [ ] Check Pinecone query counts

---

## Post-Implementation

### Step 13: Monitoring & Optimization

- [ ] **Set up monitoring:**
  - Document processing success rate
  - Search query performance
  - API costs (OpenAI + Pinecone)
  - User engagement metrics

- [ ] **Create admin dashboard:**
  - Documents processed: X / Y
  - Processing errors
  - Recent searches
  - Popular queries

- [ ] **Optimize if needed:**
  - Adjust chunk size (try 750 words)
  - Increase overlap (try 100 words)
  - Add metadata filters
  - Cache common queries

### Step 14: Documentation

- [ ] Update user documentation
- [ ] Create admin guide for document processing
- [ ] Document troubleshooting steps
- [ ] Add API documentation

---

## Success Criteria

✅ **All historical documents processed** (500+ PDFs)
✅ **Search latency < 500ms**
✅ **85%+ relevance on test queries**
✅ **Users can ask natural language questions**
✅ **AI Assistant provides cited answers**
✅ **Monthly costs under $10**
✅ **No processing errors for >90% of documents**

---

## Rollback Plan

If issues arise:

1. **Vector search not working:** Disable temporarily, fall back to keyword search
2. **Costs too high:** Reduce chunk size, increase caching
3. **Performance issues:** Process documents in smaller batches
4. **API errors:** Check rate limits, verify API keys

---

## Cost Monitoring

### Expected Costs:

**One-time:**
- 500 documents × 10 pages = 5,000 pages
- ~10,000 chunks (2 chunks/page)
- Embedding cost: $0.20

**Monthly:**
- Pinecone: $0 (free tier up to 1M vectors)
- OpenAI queries: ~$0.10 (1,000 searches)
- OpenAI new documents: ~$0.02 (100 new docs/month)
- **Total: ~$0.12/month** (well under budget!)

### Cost per Query:
- Vector search: Free (Pinecone free tier)
- OpenAI embedding: $0.0001
- Claude response: $0.001-0.003
- **Total: ~$0.001-0.003 per query**

---

## Next Steps After Phase 2

1. **Phase 3:** Notification system for stakeholders
2. **Phase 4:** Advanced analytics dashboard
3. **Phase 5:** Mobile PWA
4. **Phase 6:** Public API

Phase 2 transforms the SAFMC FMP Tracker into a true knowledge base! 🚀
