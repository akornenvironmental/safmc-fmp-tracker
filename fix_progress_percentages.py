#!/usr/bin/env python3
"""
Fix Progress Percentages - Update existing actions with correct progress values
Run this script to update all actions in the database with corrected progress percentages
"""

import os
import sys
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def fix_progress_percentages():
    """Update progress percentages for all actions based on their stage"""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Please set it or run from Render shell")
        return False

    # Create engine
    engine = create_engine(database_url)

    # Define stage to percentage mapping (matches amendments_scraper.py logic)
    stage_mappings = [
        ('implemented', 100),
        ('completed', 100),
        ('implementation', 95),  # Note: "Implementation" gets 95%, "Implemented" gets 100%
        ('rule making', 85),
        ('rulemaking', 85),
        ('secretarial review', 75),
        ('final approval', 65),
        ('public hearing', 45),
        ('scoping', 25),
        ('pre-scoping', 10),
    ]

    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()

            try:
                # Get all actions with their current progress_stage
                result = conn.execute(text("""
                    SELECT id, action_id, title, progress_stage, progress_percentage
                    FROM actions
                    WHERE progress_stage IS NOT NULL
                    ORDER BY id
                """))

                actions = result.fetchall()
                print(f"\nFound {len(actions)} actions with progress stages")

                updates = []

                for action in actions:
                    action_id = action[1]
                    title = action[2]
                    current_stage = action[3]
                    current_progress = action[4]

                    if not current_stage:
                        continue

                    stage_lower = current_stage.lower()
                    new_progress = 0

                    # Check for "implemented" or "completed" first (100%)
                    if 'implemented' in stage_lower or 'completed' in stage_lower:
                        new_progress = 100
                    else:
                        # Check other stages
                        for stage_keyword, percentage in stage_mappings:
                            if stage_keyword in stage_lower:
                                new_progress = percentage
                                break

                    # Only update if changed
                    if new_progress != current_progress and new_progress > 0:
                        updates.append({
                            'action_id': action_id,
                            'title': title[:50],
                            'stage': current_stage,
                            'old_progress': current_progress,
                            'new_progress': new_progress
                        })

                print(f"\n{len(updates)} actions need progress updates:")
                print("-" * 80)

                for update in updates[:10]:  # Show first 10
                    print(f"{update['action_id']:30} | {update['stage']:20} | {update['old_progress']:3}% → {update['new_progress']:3}%")

                if len(updates) > 10:
                    print(f"... and {len(updates) - 10} more")

                # Ask for confirmation
                print("\n" + "=" * 80)
                response = input(f"\nUpdate {len(updates)} actions? (yes/no): ").strip().lower()

                if response != 'yes':
                    print("Cancelled - no changes made")
                    trans.rollback()
                    return False

                # Perform updates
                print("\nUpdating actions...")
                for update in updates:
                    conn.execute(text("""
                        UPDATE actions
                        SET progress_percentage = :new_progress,
                            updated_at = NOW()
                        WHERE action_id = :action_id
                    """), {
                        'action_id': update['action_id'],
                        'new_progress': update['new_progress']
                    })

                # Commit transaction
                trans.commit()

                print(f"\n✅ Successfully updated {len(updates)} actions!")
                print("\nSummary of changes:")

                # Show breakdown by stage
                stage_counts = {}
                for update in updates:
                    stage = update['stage']
                    if stage not in stage_counts:
                        stage_counts[stage] = 0
                    stage_counts[stage] += 1

                for stage, count in sorted(stage_counts.items()):
                    print(f"  {stage:30} : {count:3} actions updated")

                return True

            except Exception as e:
                trans.rollback()
                print(f"\n❌ Error during update: {e}")
                return False

    except Exception as e:
        print(f"\n❌ Database connection error: {e}")
        return False
    finally:
        engine.dispose()


if __name__ == '__main__':
    print("=" * 80)
    print("SAFMC FMP Tracker - Fix Progress Percentages")
    print("=" * 80)
    print("\nThis script will update progress percentages to match the fixed calculation:")
    print("  • 'Implemented' or 'Completed' → 100%")
    print("  • 'Implementation' → 95%")
    print("  • Other stages → as per mapping")
    print("\n" + "=" * 80)

    success = fix_progress_percentages()

    sys.exit(0 if success else 1)
