"""
Create user_feedback table for storing user feedback
"""

import psycopg2
import os

def run_migration():
    """Create user_feedback table"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found")
        return False

    # Fix Render's postgres:// URL to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        print("Creating user_feedback table...")

        # Create user_feedback table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255),
                user_name VARCHAR(255),
                component VARCHAR(100),
                url TEXT,
                feedback TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'new',
                admin_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                reviewed_by VARCHAR(255)
            );
        """)

        print("user_feedback table created")

        # Create indices
        print("Creating indices...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_user ON user_feedback(user_email);
            CREATE INDEX IF NOT EXISTS idx_feedback_created ON user_feedback(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_feedback_status ON user_feedback(status);
            CREATE INDEX IF NOT EXISTS idx_feedback_component ON user_feedback(component);
        """)

        print("Indices created")

        conn.commit()
        cur.close()
        conn.close()

        print("Migration completed successfully!")
        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    run_migration()
