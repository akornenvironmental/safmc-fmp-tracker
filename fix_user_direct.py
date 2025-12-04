"""
Direct database script to fix Aaron's invitation status
Uses psycopg2 to connect directly to the Render database
"""
import psycopg2
from datetime import datetime

# Render database URL from your deployment
DATABASE_URL = "postgresql://safmc_user:SvMkI8VcP70Xjpm3YkfzAMNxURAhwZ0n@dpg-d3tpj9hbh1hs73alm8m0-a.oregon-postgres.render.com/safmc_interviews"

def fix_aaron_user():
    """Fix Aaron's invitation status"""
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check current status
        print("\n" + "="*60)
        print("CURRENT USER STATUS:")
        print("="*60)
        cursor.execute("""
            SELECT id, email, name, role, invitation_status, invitation_accepted_at, created_at, is_active
            FROM users
            ORDER BY created_at
        """)

        users = cursor.fetchall()
        aaron_id = None

        for user in users:
            user_id, email, name, role, inv_status, inv_accepted, created, is_active = user
            status_icon = "✓" if inv_status == 'accepted' else "⏳"
            print(f"{status_icon} {name} ({email})")
            print(f"   Role: {role}")
            print(f"   Invitation: {inv_status}")
            print(f"   Accepted at: {inv_accepted}")
            print(f"   Created: {created}")
            print(f"   Active: {is_active}")
            print()

            if email == 'aaron.kornbluth@gmail.com':
                aaron_id = user_id

        # Fix Aaron's status if needed
        if aaron_id:
            print("\n" + "="*60)
            print("UPDATING AARON'S INVITATION STATUS:")
            print("="*60)
            cursor.execute("""
                UPDATE users
                SET invitation_status = 'accepted',
                    invitation_accepted_at = created_at
                WHERE id = %s
            """, (aaron_id,))

            conn.commit()
            print("✅ Successfully updated Aaron's invitation status to 'accepted'")

            # Verify the update
            cursor.execute("""
                SELECT email, name, invitation_status, invitation_accepted_at
                FROM users
                WHERE id = %s
            """, (aaron_id,))

            result = cursor.fetchone()
            print(f"\nVerified: {result[1]} ({result[0]})")
            print(f"  Status: {result[2]}")
            print(f"  Accepted at: {result[3]}")
        else:
            print("❌ Aaron's user not found in database!")

        cursor.close()
        conn.close()
        print("\n✅ Done!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    fix_aaron_user()
