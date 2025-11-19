-- SAFMC Document Management System
-- Tables for storing and analyzing PDFs, meeting documents, and related content

-- Main documents table: stores PDF metadata and full text
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) UNIQUE NOT NULL,  -- e.g., 'amendment-sg-49', 'meeting-2024-03-transcript'
    title VARCHAR(500) NOT NULL,
    document_type VARCHAR(50) NOT NULL,  -- 'amendment', 'environmental_analysis', 'meeting_transcript', 'briefing_book', etc.
    action_id VARCHAR(255),  -- Links to actions table
    meeting_id VARCHAR(255),  -- Links to meetings table if applicable

    -- Source information
    source_url TEXT NOT NULL,
    download_url TEXT,
    file_size_bytes BIGINT,
    file_hash VARCHAR(64),  -- SHA256 hash to detect duplicates

    -- Content
    full_text TEXT,  -- Complete extracted text from PDF
    page_count INTEGER,
    has_images BOOLEAN DEFAULT FALSE,

    -- Metadata
    publish_date DATE,
    author VARCHAR(255),
    fmp VARCHAR(100),  -- Fishery Management Plan
    status VARCHAR(50),  -- 'active', 'archived', 'superseded'

    -- Processing
    processing_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    processing_error TEXT,
    processed_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scraped TIMESTAMP,

    -- Full-text search
    search_vector tsvector,

    FOREIGN KEY (action_id) REFERENCES actions(id) ON DELETE SET NULL
);

-- Document chunks: split large documents for AI context windows
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,  -- Order within document

    -- Content
    chunk_text TEXT NOT NULL,
    chunk_size INTEGER,  -- Character count
    page_numbers INTEGER[],  -- Which pages this chunk covers

    -- Context
    section_title VARCHAR(500),  -- e.g., "3.2 Environmental Impact Analysis"
    heading_hierarchy TEXT[],  -- Breadcrumb of headings

    -- Metadata for relevance
    keywords TEXT[],
    entities TEXT[],  -- Organizations, species, locations mentioned

    -- Full-text search
    search_vector tsvector,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE (document_id, chunk_index)
);

-- Document relationships: track related documents
CREATE TABLE IF NOT EXISTS document_relationships (
    id SERIAL PRIMARY KEY,
    parent_document_id INTEGER NOT NULL,
    child_document_id INTEGER NOT NULL,
    relationship_type VARCHAR(50) NOT NULL,  -- 'amendment', 'supersedes', 'supplements', 'references'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (parent_document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (child_document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE (parent_document_id, child_document_id, relationship_type)
);

-- Public comments extracted from documents
CREATE TABLE IF NOT EXISTS document_comments (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,

    -- Comment content
    commenter_name VARCHAR(255),
    commenter_organization VARCHAR(255),
    commenter_email VARCHAR(255),
    comment_text TEXT,
    comment_date DATE,

    -- Location in document
    page_number INTEGER,
    section_reference VARCHAR(255),

    -- Categorization
    topics TEXT[],
    sentiment VARCHAR(20),  -- 'positive', 'negative', 'neutral', 'mixed'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Scraping queue and history
CREATE TABLE IF NOT EXISTS scrape_queue (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 5,  -- 1=high, 10=low

    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'in_progress', 'completed', 'failed'
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,

    error_message TEXT,

    scheduled_for TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_documents_action_id ON documents(action_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_fmp ON documents(fmp);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_processing_status ON documents(processing_status);
CREATE INDEX idx_documents_search ON documents USING GIN(search_vector);

CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_search ON document_chunks USING GIN(search_vector);

CREATE INDEX idx_scrape_queue_status ON scrape_queue(status, priority);

-- Create function to update search vectors
CREATE OR REPLACE FUNCTION update_document_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.full_text, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_chunk_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.section_title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.chunk_text, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
DROP TRIGGER IF EXISTS documents_search_vector_update ON documents;
CREATE TRIGGER documents_search_vector_update
    BEFORE INSERT OR UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_document_search_vector();

DROP TRIGGER IF EXISTS chunks_search_vector_update ON document_chunks;
CREATE TRIGGER chunks_search_vector_update
    BEFORE INSERT OR UPDATE ON document_chunks
    FOR EACH ROW EXECUTE FUNCTION update_chunk_search_vector();

-- Create view for easy querying
CREATE OR REPLACE VIEW v_searchable_documents AS
SELECT
    d.id,
    d.document_id,
    d.title,
    d.document_type,
    d.action_id,
    a.title as action_title,
    d.fmp,
    d.publish_date,
    d.page_count,
    d.source_url,
    d.status,
    COUNT(dc.id) as chunk_count,
    d.created_at
FROM documents d
LEFT JOIN actions a ON d.action_id = a.id
LEFT JOIN document_chunks dc ON d.id = dc.document_id
WHERE d.processing_status = 'completed'
GROUP BY d.id, a.title;

COMMENT ON TABLE documents IS 'Stores PDF documents, meeting transcripts, and related materials from SAFMC';
COMMENT ON TABLE document_chunks IS 'Text chunks optimized for AI context windows (typically 2000-4000 chars)';
COMMENT ON TABLE document_relationships IS 'Tracks how documents relate to each other (amendments, supplements, etc)';
COMMENT ON TABLE document_comments IS 'Public comments extracted from PDF documents';
COMMENT ON TABLE scrape_queue IS 'Queue for managing document downloads and processing';
