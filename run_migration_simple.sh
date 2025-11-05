#!/bin/bash
# Simple migration runner for Render shell

echo "=================================="
echo "Running FMP Tracker Migration"
echo "=================================="
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL not set"
    exit 1
fi

# Run the migration
python3 << 'PYTHON_SCRIPT'
import os
import psycopg2

database_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(database_url)
conn.autocommit = True
cursor = conn.cursor()

# Read and execute migration
with open('migrations/add_comprehensive_tracking_features.sql', 'r') as f:
    sql = f.read()

print("Executing migration...")
cursor.execute(sql)

# Verify
cursor.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN (
        'council_members', 'motions', 'votes',
        'white_papers', 'scoping_items',
        'executive_orders',
        'legislation', 'regulations',
        'stock_assessments', 'assessment_comments',
        'ap_reports', 'ssc_reports',
        'documents'
    )
    ORDER BY table_name
""")

tables = cursor.fetchall()
print(f"\n✅ Created {len(tables)} new tables:")
for table in tables:
    print(f"  • {table[0]}")

cursor.close()
conn.close()
print("\n🎉 Migration complete!")
PYTHON_SCRIPT

echo ""
echo "✅ All done!"
