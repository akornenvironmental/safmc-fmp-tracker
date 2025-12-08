#!/usr/bin/env python3
"""
Quick fix for Implementation stage progress percentages
Updates all actions with 'Implementation' stage to 100%
"""

import os
import sys
from sqlalchemy import create_engine, text

# Database URL from your Render environment
DATABASE_URL = "postgresql://safmc_fmp_user:2q7bzxUgJdhCdjaJhKOsfEsVrEpsrvyp@dpg-d44eeo3uibrs73a2nkhg-a.oregon-postgres.render.com/safmc_fmp_tracker"

def main():
    print("=" * 80)
    print("SAFMC FMP Tracker - Quick Progress Fix")
    print("=" * 80)
    print("\nConnecting to database...")

    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()

            try:
                # First, check how many need updating
                print("\nChecking actions that need updating...")
                result = conn.execute(text("""
                    SELECT COUNT(*) as count
                    FROM actions
                    WHERE LOWER(progress_stage) LIKE '%implementation%'
                      AND progress_percentage != 100
                """))

                count = result.scalar()
                print(f"Found {count} actions with Implementation stage at less than 100%")

                if count == 0:
                    print("\n✅ All Implementation actions already at 100%!")
                    print("No updates needed.")
                    trans.commit()
                    return

                # Show sample of what will be updated
                print("\nSample actions that will be updated:")
                print("-" * 80)
                result = conn.execute(text("""
                    SELECT title, progress_stage, progress_percentage
                    FROM actions
                    WHERE LOWER(progress_stage) LIKE '%implementation%'
                      AND progress_percentage != 100
                    ORDER BY title
                    LIMIT 10
                """))

                for row in result:
                    title = row[0][:50] + "..." if len(row[0]) > 50 else row[0]
                    print(f"  {title:55} | {row[1]:20} | {row[2]:3}% → 100%")

                if count > 10:
                    print(f"  ... and {count - 10} more")

                print("\n" + "=" * 80)
                confirm = input(f"\nUpdate {count} actions to 100%? (yes/no): ").strip().lower()

                if confirm != 'yes':
                    print("\n❌ Cancelled - no changes made")
                    trans.rollback()
                    return

                # Perform the update
                print("\n🔄 Updating actions...")
                result = conn.execute(text("""
                    UPDATE actions
                    SET progress_percentage = 100,
                        updated_at = NOW()
                    WHERE LOWER(progress_stage) LIKE '%implementation%'
                      AND progress_percentage != 100
                """))

                updated = result.rowcount

                # Commit transaction
                trans.commit()

                print(f"\n✅ Successfully updated {updated} actions!")

                # Show verification
                print("\nVerification - Sample updated actions:")
                print("-" * 80)
                result = conn.execute(text("""
                    SELECT title, progress_stage, progress_percentage
                    FROM actions
                    WHERE LOWER(progress_stage) LIKE '%implementation%'
                    ORDER BY title
                    LIMIT 5
                """))

                for row in result:
                    title = row[0][:50] + "..." if len(row[0]) > 50 else row[0]
                    checkmark = "✅" if row[2] == 100 else "❌"
                    print(f"  {checkmark} {title:55} | {row[1]:20} | {row[2]:3}%")

                print("\n" + "=" * 80)
                print("✅ COMPLETE! Refresh your Actions page to see the updates.")
                print("=" * 80)

            except Exception as e:
                trans.rollback()
                print(f"\n❌ Error during update: {e}")
                sys.exit(1)

    except Exception as e:
        print(f"\n❌ Database connection error: {e}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == '__main__':
    main()
