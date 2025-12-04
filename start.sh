#!/bin/bash
# Startup script for Render deployment

echo "Starting SAFMC FMP Tracker..."

# Initialize database tables
echo "Initializing database..."
python init_db.py

# Seed stock assessment data
echo "Seeding stock assessment data..."
python seed_stock_assessments.py

# Run refresh token migration
echo "Running refresh token migration..."
python migrations/add_refresh_token_to_users.py

# Run organization column migration
echo "Running organization column migration..."
python migrations/add_organization_to_users.py

# Create SSC tables
echo "Creating SSC tables..."
python create_ssc_tables_with_app_context.py || echo "SSC tables may already exist"

# Seed SSC members
echo "Seeding SSC members..."
python seed_ssc_members_production.py || echo "SSC members may already exist"

# Start Gunicorn
echo "Starting Gunicorn web server..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
