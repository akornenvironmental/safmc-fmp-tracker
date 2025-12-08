#!/usr/bin/env python3
"""
One-time script to populate start_date and completion_date for all amendments
Run this after deploying the date extraction feature
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try different import paths for different environments
try:
    from src.app import create_app
    from src.scrapers.amendments_scraper import AmendmentsScraper
    from src.models.action import Action
    from src.config.extensions import db
except ModuleNotFoundError:
    # If running from /opt/render/project/src, use app directly
    from app import create_app
    from src.scrapers.amendments_scraper import AmendmentsScraper
    from src.models.action import Action
    from src.config.extensions import db

from datetime import datetime

def main():
    print("=" * 80)
    print("Populating Amendment Dates from SAFMC")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        # Initialize scraper
        scraper = AmendmentsScraper()

        print("\n1. Scraping amendments from SAFMC website...")
        results = scraper.scrape_all()

        print(f"   ✓ Found {results['total_found']} amendments")
        if results['errors']:
            print(f"   ⚠ {len(results['errors'])} errors occurred")
            for error in results['errors'][:3]:
                print(f"     - {error}")

        print("\n2. Updating database with extracted dates...")
        updated_count = 0
        dates_added = 0

        for amendment_data in results['amendments']:
            action = Action.query.filter_by(action_id=amendment_data['action_id']).first()

            if action:
                # Track if we're adding new date info
                had_dates = bool(action.start_date or action.completion_date)

                # Update dates from scraper
                if amendment_data.get('start_date'):
                    action.start_date = amendment_data['start_date']
                if amendment_data.get('completion_date'):
                    action.completion_date = amendment_data['completion_date']

                # Update other fields
                action.progress_percentage = amendment_data.get('progress_percentage', action.progress_percentage)
                action.last_scraped = datetime.utcnow()
                action.updated_at = datetime.utcnow()

                updated_count += 1

                # Count new dates
                if not had_dates and (action.start_date or action.completion_date):
                    dates_added += 1
                    print(f"   ✓ {action.action_id}: Added dates (start={action.start_date}, completion={action.completion_date})")

        # Commit all changes
        db.session.commit()

        print(f"\n3. Summary:")
        print(f"   ✓ Updated {updated_count} actions")
        print(f"   ✓ Added dates to {dates_added} actions that didn't have them")

        # Show some examples
        print("\n4. Sample completed amendments with dates:")
        completed_with_dates = Action.query.filter(
            Action.completion_date.isnot(None),
            Action.progress_percentage >= 100
        ).limit(5).all()

        for action in completed_with_dates:
            print(f"   - {action.action_id}: {action.title}")
            print(f"     Start: {action.start_date}, Completion: {action.completion_date}")

        print("\n" + "=" * 80)
        print("Date population complete!")
        print("=" * 80)

if __name__ == '__main__':
    main()
