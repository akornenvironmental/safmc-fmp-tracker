#!/usr/bin/env python3
"""
Simple script to run the amendments scraper and update all titles
This bypasses authentication since it runs directly on the server
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app import create_app
    from scrapers.amendments_scraper import AmendmentsScraper
    from models.action import Action
    from config.extensions import db
    from datetime import datetime

    print("=" * 80)
    print("Running Amendments Scraper to Update Titles")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        print("\n1. Initializing scraper...")
        scraper = AmendmentsScraper()

        print("2. Scraping amendments from SAFMC...")
        results = scraper.scrape_all()

        print(f"   Found {results['total_found']} amendments")

        print("\n3. Updating database with cleaned titles and expanded acronyms...")
        items_new = 0
        items_updated = 0

        for amendment_data in results['amendments']:
            action = Action.query.filter_by(action_id=amendment_data['action_id']).first()

            if action:
                # Update existing action
                action.title = amendment_data['title']
                action.type = amendment_data['type']
                action.fmp = amendment_data['fmp']
                action.progress_stage = amendment_data['progress_stage']
                action.progress_percentage = amendment_data.get('progress_percentage', 0)
                action.phase = amendment_data.get('phase', '')
                action.description = amendment_data['description']
                action.lead_staff = amendment_data['lead_staff']
                action.source_url = amendment_data.get('source_url', action.source_url)
                action.status = amendment_data.get('status')
                action.start_date = amendment_data.get('start_date')
                action.completion_date = amendment_data.get('completion_date')
                action.last_scraped = datetime.utcnow()
                action.updated_at = datetime.utcnow()
                items_updated += 1
                print(f"   ✓ Updated: {action.title}")
            else:
                # Create new action
                action = Action(
                    action_id=amendment_data['action_id'],
                    title=amendment_data['title'],
                    type=amendment_data['type'],
                    fmp=amendment_data['fmp'],
                    progress_stage=amendment_data['progress_stage'],
                    progress_percentage=amendment_data.get('progress_percentage', 0),
                    phase=amendment_data.get('phase', ''),
                    description=amendment_data['description'],
                    lead_staff=amendment_data['lead_staff'],
                    source_url=amendment_data['source_url'],
                    status=amendment_data.get('status'),
                    start_date=amendment_data.get('start_date'),
                    completion_date=amendment_data.get('completion_date'),
                    last_scraped=datetime.utcnow()
                )
                db.session.add(action)
                items_new += 1
                print(f"   ✓ Created: {action.title}")

        # Commit all changes
        db.session.commit()

        print(f"\n4. Summary:")
        print(f"   ✓ New actions: {items_new}")
        print(f"   ✓ Updated actions: {items_updated}")
        print(f"   ✓ Total processed: {items_new + items_updated}")

        if results['errors']:
            print(f"\n   ⚠ Errors encountered: {len(results['errors'])}")
            for error in results['errors'][:5]:
                print(f"     - {error}")

        print("\n" + "=" * 80)
        print("Scraper completed successfully!")
        print("All titles have been cleaned and acronyms expanded.")
        print("=" * 80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
