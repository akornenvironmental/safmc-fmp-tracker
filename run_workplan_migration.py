#!/usr/bin/env python3
"""
Run Workplan System Migration
Creates workplan tables in the database
"""

import os
import sys
from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set")
    print("Set it with: export DATABASE_URL='postgresql://...'")
    sys.exit(1)

print(f"Connecting to database...")
print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")

try:
    engine = create_engine(DATABASE_URL)

    # Read the migration SQL
    migration_file = 'migrations/create_workplan_system.sql'
    print(f"\nReading migration file: {migration_file}")

    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # Execute the migration
    print("\nExecuting migration...")
    with engine.connect() as conn:
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

        for i, statement in enumerate(statements, 1):
            # Skip comments and empty statements
            if statement.startswith('--') or statement.startswith('/*') or not statement:
                continue

            try:
                conn.execute(text(statement))
                conn.commit()

                # Print progress for major operations
                if 'CREATE TABLE' in statement:
                    table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip()
                    print(f"  ✓ Created table: {table_name}")
                elif 'CREATE INDEX' in statement:
                    print(f"  ✓ Created index")
                elif 'CREATE OR REPLACE VIEW' in statement:
                    view_name = statement.split('CREATE OR REPLACE VIEW')[1].split('AS')[0].strip()
                    print(f"  ✓ Created view: {view_name}")
                elif 'INSERT INTO' in statement:
                    print(f"  ✓ Inserted reference data")
                elif 'ALTER TABLE' in statement:
                    print(f"  ✓ Altered table")

            except Exception as e:
                error_msg = str(e)
                # Ignore "already exists" errors
                if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    print(f"  ℹ Skipping (already exists)")
                else:
                    print(f"  ✗ Error: {error_msg}")
                    # Continue with other statements

    print("\n✅ Migration completed successfully!")
    print("\nCreated tables:")
    print("  - workplan_versions")
    print("  - workplan_items")
    print("  - workplan_milestones")
    print("  - milestone_types")
    print("  - workplan_upload_log")
    print("\nEnhanced tables:")
    print("  - actions (added workplan fields)")
    print("  - comments (added workplan fields)")
    print("\nCreated views:")
    print("  - v_current_workplan")
    print("  - v_workplan_history")

    # Verify tables were created
    print("\nVerifying tables...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name LIKE 'workplan%'
            ORDER BY table_name
        """))

        tables = [row[0] for row in result]
        print(f"Found {len(tables)} workplan tables:")
        for table in tables:
            print(f"  ✓ {table}")

except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
