"""
Create FMP documents and document chunks tables for comprehensive document storage
"""

import psycopg2
import os
from datetime import datetime

def run_migration():
    """Create FMP document storage tables"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False

    # Fix Render's postgres:// URL to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        print("🔄 Creating fmp_documents table...")

        # Create main documents table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fmp_documents (
                id SERIAL PRIMARY KEY,
                document_id VARCHAR(200) UNIQUE NOT NULL,
                title VARCHAR(500) NOT NULL,
                document_type VARCHAR(100) NOT NULL,

                -- FMP and amendment info
                fmp VARCHAR(100),
                amendment_number VARCHAR(50),
                regulatory_action VARCHAR(100),

                -- Document metadata
                document_date DATE,
                publication_date DATE,
                effective_date DATE,
                status VARCHAR(50),

                -- Source information
                source_url TEXT NOT NULL,
                download_url TEXT,
                file_path TEXT,
                file_type VARCHAR(20),
                file_size_bytes INTEGER,

                -- Content
                description TEXT,
                summary TEXT,
                full_text TEXT,

                -- Categorization
                keywords TEXT[],
                species TEXT[],
                topics TEXT[],
                affected_regulations TEXT[],

                -- Related entities
                related_actions INTEGER[],
                related_meetings INTEGER[],
                related_assessments INTEGER[],

                -- Processing status
                processed BOOLEAN DEFAULT FALSE,
                indexed BOOLEAN DEFAULT FALSE,
                extraction_error TEXT,

                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_scraped TIMESTAMP,

                -- Full text search
                search_vector TSVECTOR
            );
        """)

        print("✅ fmp_documents table created")

        # Create document chunks table for AI/RAG
        print("🔄 Creating document_chunks table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY,
                document_id INTEGER REFERENCES fmp_documents(id) ON DELETE CASCADE,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                chunk_type VARCHAR(50),

                -- Section metadata
                section_title VARCHAR(300),
                page_number INTEGER,

                -- Vector embedding (for semantic search)
                embedding_model VARCHAR(100),
                embedding_vector FLOAT[],

                -- Metadata for context
                metadata JSONB,

                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(document_id, chunk_index)
            );
        """)

        print("✅ document_chunks table created")

        # Create scraping queue table
        print("🔄 Creating document_scrape_queue table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS document_scrape_queue (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                document_type VARCHAR(100),
                fmp VARCHAR(100),
                priority INTEGER DEFAULT 5,
                status VARCHAR(50) DEFAULT 'pending',
                attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                error_message TEXT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );
        """)

        print("✅ document_scrape_queue table created")

        # Create indices for performance
        print("🔄 Creating indices...")
        cur.execute("""
            -- Documents table indices
            CREATE INDEX IF NOT EXISTS idx_documents_type ON fmp_documents(document_type);
            CREATE INDEX IF NOT EXISTS idx_documents_fmp ON fmp_documents(fmp);
            CREATE INDEX IF NOT EXISTS idx_documents_status ON fmp_documents(status);
            CREATE INDEX IF NOT EXISTS idx_documents_date ON fmp_documents(document_date);
            CREATE INDEX IF NOT EXISTS idx_documents_processed ON fmp_documents(processed);
            CREATE INDEX IF NOT EXISTS idx_documents_keywords ON fmp_documents USING GIN(keywords);
            CREATE INDEX IF NOT EXISTS idx_documents_species ON fmp_documents USING GIN(species);

            -- Full text search index
            CREATE INDEX IF NOT EXISTS idx_documents_search ON fmp_documents USING GIN(search_vector);

            -- Document chunks indices
            CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);
            CREATE INDEX IF NOT EXISTS idx_chunks_type ON document_chunks(chunk_type);

            -- Scrape queue indices
            CREATE INDEX IF NOT EXISTS idx_queue_status ON document_scrape_queue(status);
            CREATE INDEX IF NOT EXISTS idx_queue_priority ON document_scrape_queue(priority DESC);
        """)

        print("✅ Indices created")

        # Create trigger to update search_vector automatically
        print("🔄 Creating search vector trigger...")
        cur.execute("""
            CREATE OR REPLACE FUNCTION documents_search_vector_update() RETURNS TRIGGER AS $$
            BEGIN
                NEW.search_vector :=
                    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
                    setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'C') ||
                    setweight(to_tsvector('english', COALESCE(NEW.full_text, '')), 'D');
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS documents_search_vector_trigger ON fmp_documents;

            CREATE TRIGGER documents_search_vector_trigger
            BEFORE INSERT OR UPDATE OF title, description, summary, full_text
            ON fmp_documents
            FOR EACH ROW
            EXECUTE FUNCTION documents_search_vector_update();
        """)

        print("✅ Search vector trigger created")

        conn.commit()
        cur.close()
        conn.close()

        print("✅ Migration completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    run_migration()
