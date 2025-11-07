"""
Create AI query log table for tracking and troubleshooting AI Assistant usage
"""

import psycopg2
import os
from datetime import datetime

def run_migration():
    """Create AI query log table"""

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

        print("🔄 Creating ai_query_log table...")

        # Create AI query log table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ai_query_log (
                id SERIAL PRIMARY KEY,

                -- User information
                user_id INTEGER,
                user_email VARCHAR(255),
                user_ip VARCHAR(50),

                -- Query details
                question TEXT NOT NULL,
                response TEXT,

                -- Context provided to AI
                context_documents INTEGER[],
                context_size_chars INTEGER,

                -- API details
                model VARCHAR(100),
                tokens_used INTEGER,
                response_time_ms INTEGER,

                -- Status
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,

                -- Metadata
                user_agent TEXT,
                session_id VARCHAR(100),

                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                -- Full text search on queries
                search_vector TSVECTOR
            );
        """)

        print("✅ ai_query_log table created")

        # Create indices
        print("🔄 Creating indices...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_ai_log_user ON ai_query_log(user_id);
            CREATE INDEX IF NOT EXISTS idx_ai_log_created ON ai_query_log(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_ai_log_success ON ai_query_log(success);
            CREATE INDEX IF NOT EXISTS idx_ai_log_search ON ai_query_log USING GIN(search_vector);
        """)

        print("✅ Indices created")

        # Create trigger for search vector
        print("🔄 Creating search vector trigger...")
        cur.execute("""
            CREATE OR REPLACE FUNCTION ai_log_search_vector_update() RETURNS TRIGGER AS $$
            BEGIN
                NEW.search_vector :=
                    setweight(to_tsvector('english', COALESCE(NEW.question, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(NEW.response, '')), 'B');
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS ai_log_search_vector_trigger ON ai_query_log;

            CREATE TRIGGER ai_log_search_vector_trigger
            BEFORE INSERT OR UPDATE OF question, response
            ON ai_query_log
            FOR EACH ROW
            EXECUTE FUNCTION ai_log_search_vector_update();
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
