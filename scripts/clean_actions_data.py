"""
Clean Actions Data - Remove junk/placeholder entries and duplicates
This script removes:
1. Vague/placeholder titles (?, TBD, dates, etc.)
2. CMP-prefixed duplicates
3. Malformed title entries
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.extensions import db
from src.models.action import Action
from src.models.workplan import WorkplanItem
from app import app

def main():
    with app.app_context():
        print("=" * 80)
        print("CLEANING ACTIONS DATABASE")
        print("=" * 80)

        total_before = Action.query.count()
        print(f"\nTotal actions before cleanup: {total_before}")

        # 1. DELETE VAGUE/PLACEHOLDER TITLES
        print("\n" + "-" * 80)
        print("1. Deleting vague/placeholder title entries...")
        print("-" * 80)

        vague_titles = [
            "?",
            "TBD",
            "Tentative Start",
            "Primary",
            "Secondary",
            "SERO Priority",
            "2026-12-01 00:00:00"
        ]

        # Also delete titles starting with these phrases
        vague_prefixes = [
            "TBD pending",
            "Timing will be discussed",
            "Upon completion of",
            "Part of the"
        ]

        deleted_vague = 0
        actions_to_delete = []

        # Collect actions to delete
        for title in vague_titles:
            actions = Action.query.filter_by(title=title).all()
            actions_to_delete.extend(actions)

        for prefix in vague_prefixes:
            actions = Action.query.filter(Action.title.like(f'{prefix}%')).all()
            actions_to_delete.extend(actions)

        # Remove duplicates
        actions_to_delete = list(set(actions_to_delete))

        # Clear workplan references and delete
        for action in actions_to_delete:
            # Clear any workplan item references to this action
            workplan_items = WorkplanItem.query.filter_by(action_id=action.action_id).all()
            if workplan_items:
                print(f"  Clearing {len(workplan_items)} workplan reference(s) for '{action.title}'")
                for item in workplan_items:
                    item.action_id = None

            print(f"  Deleting: '{action.title}' (ID: {action.id}, action_id: {action.action_id})")
            db.session.delete(action)
            deleted_vague += 1

        print(f"\nDeleted {deleted_vague} vague/placeholder entries")

        # 2. DELETE CMP-PREFIXED DUPLICATES
        print("\n" + "-" * 80)
        print("2. Deleting CMP-prefixed duplicates...")
        print("-" * 80)

        # Find all CMP actions
        cmp_actions = Action.query.filter(
            (Action.title.like('CMP %')) &
            (Action.fmp == 'Coastal Migratory Pelagics')
        ).all()

        deleted_duplicates = 0
        for cmp_action in cmp_actions:
            # Try to find full-name equivalent
            full_title = cmp_action.title.replace('CMP ', 'Coastal Migratory Pelagics ')

            # Check if full version exists
            full_version = Action.query.filter_by(
                title=full_title,
                fmp='Coastal Migratory Pelagics'
            ).first()

            if full_version:
                # Clear any workplan item references to this action
                workplan_items = WorkplanItem.query.filter_by(action_id=cmp_action.action_id).all()
                if workplan_items:
                    print(f"  Clearing {len(workplan_items)} workplan reference(s), updating to use full version")
                    for item in workplan_items:
                        item.action_id = full_version.action_id  # Point to full version instead

                print(f"  Deleting duplicate: '{cmp_action.title}' (ID: {cmp_action.id})")
                print(f"    Keeping: '{full_version.title}' (ID: {full_version.id})")
                db.session.delete(cmp_action)
                deleted_duplicates += 1

        print(f"\nDeleted {deleted_duplicates} CMP duplicate entries")

        # 3. DELETE MALFORMED TITLES (sentence fragments)
        print("\n" + "-" * 80)
        print("3. Deleting malformed title entries (sentence fragments)...")
        print("-" * 80)

        malformed_patterns = [
            "Included in the Comprehensive",
            "Eliminated closed area for",
            "NMFS is proposing changes"
        ]

        deleted_malformed = 0
        for pattern in malformed_patterns:
            actions = Action.query.filter(Action.title.like(f'{pattern}%')).all()
            for action in actions:
                # Clear any workplan item references to this action
                workplan_items = WorkplanItem.query.filter_by(action_id=action.action_id).all()
                if workplan_items:
                    print(f"  Clearing {len(workplan_items)} workplan reference(s) for '{action.title}'")
                    for item in workplan_items:
                        item.action_id = None

                print(f"  Deleting malformed: '{action.title}' (ID: {action.id})")
                db.session.delete(action)
                deleted_malformed += 1

        print(f"\nDeleted {deleted_malformed} malformed entries")

        # COMMIT ALL DELETIONS
        print("\n" + "=" * 80)
        print(f"SUMMARY:")
        print(f"  Vague/placeholder entries: {deleted_vague}")
        print(f"  CMP duplicates: {deleted_duplicates}")
        print(f"  Malformed titles: {deleted_malformed}")
        print(f"  TOTAL DELETED: {deleted_vague + deleted_duplicates + deleted_malformed}")
        print("=" * 80)

        user_input = input("\nProceed with deletion? (yes/no): ")
        if user_input.lower() == 'yes':
            db.session.commit()
            total_after = Action.query.count()
            print(f"\n✓ Database cleaned successfully!")
            print(f"  Actions before: {total_before}")
            print(f"  Actions after: {total_after}")
            print(f"  Removed: {total_before - total_after}")
        else:
            db.session.rollback()
            print("\n✗ Cleanup cancelled. No changes made.")

if __name__ == '__main__':
    main()
