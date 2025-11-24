# Phase 2: Vector Search & Document Intelligence

## Overview
Enable natural language queries across all SAFMC documents by implementing vector embeddings and semantic search. Users will be able to ask questions like:
- "What amendments addressed red snapper size limits in 2020?"
- "Show me all public comments about recreational for-hire limits"
- "Find documents discussing stock assessment uncertainty"

---

## Architecture

```
PDF/Documents → Text Extraction → Chunking → Embeddings → Vector DB → Semantic Search
                (PyPDF2/pdfplumber)  (500 words)  (OpenAI)    (Pinecone)      ↓
                                                                         AI Assistant
```

---

## Required Services

### 1. OpenAI API
- **Purpose**: Generate text embeddings
- **Model**: `text-embedding-3-small`
- **Cost**: ~$0.02 per 1,000 documents
- **Sign up**: https://platform.openai.com/
- **API Key**: Store in environment variable `OPENAI_API_KEY`

### 2. Pinecone Vector Database
- **Purpose**: Store and query vector embeddings
- **Plan**: Free tier (1M vectors - sufficient for SAFMC)
- **Sign up**: https://www.pinecone.io/
- **API Key**: Store in environment variable `PINECONE_API_KEY`
- **Environment**: Store in `PINECONE_ENVIRONMENT`

---

## Implementation Steps

### Step 1: Install Dependencies

```bash
pip install openai pinecone-client pypdf2 pdfplumber tiktoken
```

Add to `requirements.txt`:
```
openai==1.6.1
pinecone-client==3.0.0
pypdf2==3.0.1
pdfplumber==0.10.3
tiktoken==0.5.2
```

### Step 2: Document Processor Service

Create `src/services/document_processor.py`:

```python
"""
Document processing service for PDF text extraction and embedding generation
"""
import openai
import pinecone
from pypdf2 import PdfReader
import pdfplumber
from typing import List, Dict
import os

class DocumentProcessor:
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # Initialize Pinecone
        pinecone.init(
            api_key=os.getenv('PINECONE_API_KEY'),
            environment=os.getenv('PINECONE_ENVIRONMENT', 'us-east-1-aws')
        )

        # Create or connect to index
        self.index_name = 'safmc-documents'
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.index_name,
                dimension=1536,  # text-embedding-3-small dimension
                metric='cosine'
            )
        self.index = pinecone.Index(self.index_name)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(pdf_path) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() or ''
                return text
        except:
            # Fallback to PyPDF2
            reader = PdfReader(pdf_path)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
            return text

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def process_document(self, document_id: int, document_path: str, metadata: Dict) -> int:
        """
        Process a document: extract text, chunk, embed, and store in Pinecone

        Returns: Number of chunks created
        """
        # Extract text
        text = self.extract_text_from_pdf(document_path)

        # Chunk text
        chunks = self.chunk_text(text)

        # Generate embeddings and store
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = self.generate_embedding(chunk)

            # Prepare vector with metadata
            vector_id = f"{document_id}_chunk_{i}"
            vector_metadata = {
                **metadata,
                'chunk_index': i,
                'text': chunk[:1000],  # Store preview (Pinecone has metadata size limits)
                'document_id': document_id
            }

            vectors.append((vector_id, embedding, vector_metadata))

        # Upsert to Pinecone in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)

        return len(chunks)

    def search(self, query: str, top_k: int = 5, filter: Dict = None) -> List[Dict]:
        """
        Search for relevant document chunks

        Args:
            query: Natural language search query
            top_k: Number of results to return
            filter: Optional metadata filters (e.g., {'fmp': 'Snapper Grouper'})

        Returns: List of relevant chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )

        return results['matches']
```

### Step 3: Update AI Service

Modify `src/services/ai_service.py` to use document context:

```python
def answer_question_with_context(self, question: str, fmp_filter: str = None) -> Dict:
    """
    Answer question using document context from vector search
    """
    # Search for relevant document chunks
    from src.services.document_processor import DocumentProcessor
    processor = DocumentProcessor()

    filter_dict = {'fmp': fmp_filter} if fmp_filter else None
    relevant_chunks = processor.search(question, top_k=5, filter=filter_dict)

    # Build context from chunks
    context = "\n\n".join([
        f"Document: {chunk['metadata'].get('title', 'Unknown')}\n"
        f"Source: {chunk['metadata'].get('source_url', 'N/A')}\n"
        f"Content: {chunk['metadata']['text']}"
        for chunk in relevant_chunks
    ])

    # Build prompt with context
    prompt = f"""You are an expert on South Atlantic Fishery Management Council regulations and amendments.

Based on the following document excerpts, answer the user's question accurately and cite specific documents.

CONTEXT:
{context}

QUESTION: {question}

Provide a detailed answer with specific citations to the documents above."""

    # Call Claude with context
    response = self.client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        'answer': response.content[0].text,
        'sources': [
            {
                'title': chunk['metadata'].get('title'),
                'url': chunk['metadata'].get('source_url'),
                'relevance_score': chunk['score']
            }
            for chunk in relevant_chunks
        ]
    }
```

### Step 4: Background Processing Queue

Create `src/services/document_queue_processor.py`:

```python
"""
Background worker to process documents from the queue
"""
from src.models.document import Document
from src.services.document_processor import DocumentProcessor
from src.config.extensions import db
from sqlalchemy import and_
import requests
import tempfile
import os

class DocumentQueueProcessor:
    def __init__(self):
        self.processor = DocumentProcessor()

    def process_queue(self, batch_size: int = 10):
        """Process documents from queue"""
        # Get unprocessed documents
        documents = Document.query.filter(
            and_(
                Document.processed == False,
                Document.url.isnot(None)
            )
        ).limit(batch_size).all()

        for doc in documents:
            try:
                print(f"Processing document {doc.id}: {doc.title}")

                # Download PDF
                response = requests.get(doc.url, timeout=30)
                response.raise_for_status()

                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name

                # Process document
                metadata = {
                    'title': doc.title,
                    'source_url': doc.url,
                    'fmp': doc.fmp or 'Unknown',
                    'document_type': doc.document_type or 'Unknown',
                    'date': str(doc.date) if doc.date else None
                }

                chunks_created = self.processor.process_document(
                    document_id=doc.id,
                    document_path=tmp_path,
                    metadata=metadata
                )

                # Mark as processed
                doc.processed = True
                doc.chunks_created = chunks_created
                db.session.commit()

                print(f"✓ Processed {chunks_created} chunks")

                # Clean up temp file
                os.unlink(tmp_path)

            except Exception as e:
                print(f"✗ Error processing document {doc.id}: {e}")
                # Mark as errored but don't stop processing
                doc.processing_error = str(e)[:500]
                db.session.commit()

    def reprocess_failed(self):
        """Reprocess documents that failed"""
        failed_docs = Document.query.filter(
            Document.processing_error.isnot(None)
        ).all()

        for doc in failed_docs:
            doc.processing_error = None
            doc.processed = False

        db.session.commit()
        self.process_queue(batch_size=len(failed_docs))
```

### Step 5: Add API Endpoints

Add to `src/routes/api_routes.py`:

```python
@bp.route('/documents/process-queue', methods=['POST'])
@require_admin
def process_document_queue():
    """Process documents from queue (admin only)"""
    from src.services.document_queue_processor import DocumentQueueProcessor

    batch_size = request.json.get('batch_size', 10)
    processor = DocumentQueueProcessor()
    processor.process_queue(batch_size=batch_size)

    return jsonify({
        'success': True,
        'message': f'Processed up to {batch_size} documents'
    })

@bp.route('/documents/search', methods=['POST'])
def search_documents():
    """Search documents using natural language"""
    query = request.json.get('query')
    fmp_filter = request.json.get('fmp')

    if not query:
        return jsonify({'error': 'Query required'}), 400

    from src.services.document_processor import DocumentProcessor
    processor = DocumentProcessor()

    filter_dict = {'fmp': fmp_filter} if fmp_filter else None
    results = processor.search(query, top_k=10, filter=filter_dict)

    return jsonify({
        'results': [
            {
                'title': r['metadata'].get('title'),
                'url': r['metadata'].get('source_url'),
                'excerpt': r['metadata'].get('text', '')[:200],
                'relevance_score': r['score'],
                'fmp': r['metadata'].get('fmp')
            }
            for r in results
        ]
    })
```

### Step 6: Database Schema Updates

Add to existing `Document` model:

```python
# Add to src/models/document.py
processed = db.Column(db.Boolean, default=False)
chunks_created = db.Column(db.Integer)
processing_error = db.Column(db.Text)
processed_date = db.Column(db.DateTime)
```

Run migration:
```python
# migrations/add_document_processing_fields.py
ALTER TABLE documents ADD COLUMN processed BOOLEAN DEFAULT FALSE;
ALTER TABLE documents ADD COLUMN chunks_created INTEGER;
ALTER TABLE documents ADD COLUMN processing_error TEXT;
ALTER TABLE documents ADD COLUMN processed_date TIMESTAMP;
```

---

## Testing Phase 2

### 1. Process Sample Documents

```bash
curl -X POST https://safmc-fmp-tracker.onrender.com/api/documents/process-queue \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 5}'
```

### 2. Test Search

```bash
curl -X POST https://safmc-fmp-tracker.onrender.com/api/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the size limits for red snapper?",
    "fmp": "Snapper Grouper"
  }'
```

### 3. Test AI Assistant with Context

Update frontend to use new context-aware endpoint.

---

## Cost Estimates

### One-Time Setup
- **500 documents** × 10 pages avg = 5,000 pages
- **~10,000 chunks** (2 chunks per page avg)
- **Embedding generation**: $0.20 one-time

### Monthly Costs
- **Pinecone**: $0 (free tier - 1M vectors)
- **OpenAI embeddings**: Minimal (only for new documents + queries)
- **Estimated monthly**: < $5

### Query Costs
- Each user question: ~$0.0001 (embedding generation)
- **1,000 questions/month**: ~$0.10

**Total estimated cost: $0.20 setup + $5/month = Very affordable!**

---

## Performance Metrics

### Expected Performance
- **Document processing**: 2-5 documents/minute
- **Search latency**: < 500ms
- **Relevance**: 85%+ accuracy for domain-specific questions
- **Total processing time** (500 docs): 2-4 hours

### Monitoring
- Track processing success/failure rates
- Monitor search quality feedback
- Log query performance
- Track cost per query

---

## Deployment Checklist

- [ ] Sign up for OpenAI API
- [ ] Sign up for Pinecone
- [ ] Add environment variables to Render
  - `OPENAI_API_KEY`
  - `PINECONE_API_KEY`
  - `PINECONE_ENVIRONMENT`
- [ ] Install dependencies
- [ ] Run database migrations
- [ ] Deploy code to Render
- [ ] Process initial document batch (test with 10 docs)
- [ ] Verify search functionality
- [ ] Process remaining documents
- [ ] Update frontend to use new search
- [ ] Add usage monitoring

---

## Future Enhancements

### v2.1 - Advanced Features
- Multi-document comparison
- Timeline-aware search ("amendments before 2020")
- Automatic summarization
- Citation verification

### v2.2 - Performance
- Caching layer for common queries
- Batch query processing
- Progressive document processing

### v2.3 - Intelligence
- Related document recommendations
- Automatic tagging
- Anomaly detection (unusual amendments)
- Trend analysis

---

## Support & Troubleshooting

### Common Issues

**"OpenAI API error"**
- Verify API key is correct
- Check billing/quota limits
- Test with simpler query

**"Pinecone connection failed"**
- Verify API key and environment
- Check index exists
- Ensure dimensions match (1536)

**"PDF extraction failed"**
- Try alternative extractor
- Check PDF is not password-protected
- Verify PDF is not corrupted

**"Search returns irrelevant results"**
- Adjust chunk size (try 750 words)
- Increase overlap (try 100 words)
- Add more metadata filters
- Tune relevance threshold

### Getting Help
- OpenAI docs: https://platform.openai.com/docs
- Pinecone docs: https://docs.pinecone.io/
- Check logs: `GET /api/logs/scrape`

---

## Timeline

**Week 1**: Setup & Infrastructure
- Day 1-2: API signups, environment setup
- Day 3-4: Implement document processor
- Day 5: Testing and debugging

**Week 2**: Integration & Processing
- Day 1-2: Update AI service
- Day 3: Process initial documents
- Day 4-5: Frontend integration

**Week 3**: Polish & Launch
- Day 1-2: Process all documents
- Day 3-4: User testing
- Day 5: Launch!

**Total**: 3 weeks to full production

---

## Success Metrics

- ✅ All historical documents processed
- ✅ < 500ms search latency
- ✅ 85%+ relevance on test queries
- ✅ Users can ask natural language questions
- ✅ AI Assistant provides cited answers
- ✅ Monthly costs under budget

Phase 2 will transform SAFMC FMP Tracker into a true knowledge base where users can discover information naturally, without knowing exact document names or locations!
