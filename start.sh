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

# Start Gunicorn
echo "Starting Gunicorn web server..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
