"""
Add invitation status columns to the users table
"""
import psycopg2
from datetime import datetime

# Render database URL
DATABASE_URL = "postgresql://safmc_user:SvMkI8VcP70Xjpm3YkfzAMNxURAhwZ0n@dpg-d3tpj9hbh1hs73alm8m0-a.oregon-postgres.render.com/safmc_interviews"

def add_invitation_columns():
    """Add invitation status tracking columns"""
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check current table structure
        print("\nChecking current users table structure...")
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print("\nCurrent columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")

        # Check if invitation_status already exists
        has_invitation_status = any(col[0] == 'invitation_status' for col in columns)

        if not has_invitation_status:
            print("\n" + "="*60)
            print("ADDING INVITATION STATUS COLUMNS:")
            print("="*60)

            # Create the enum type first
            print("1. Creating invitation_status enum type...")
            cursor.execute("""
                DO $$ BEGIN
                    CREATE TYPE invitation_status AS ENUM ('pending', 'accepted');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """)

            # Add invitation_status column
            print("2. Adding invitation_status column...")
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS invitation_status invitation_status DEFAULT 'pending'
            """)

            # Add invitation_accepted_at column
            print("3. Adding invitation_accepted_at column...")
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS invitation_accepted_at TIMESTAMP
            """)

            # Set existing users who have logged in to 'accepted'
            print("4. Setting invitation status for existing users...")
            cursor.execute("""
                UPDATE users
                SET invitation_status = 'accepted',
                    invitation_accepted_at = "lastLogin"
                WHERE "lastLogin" IS NOT NULL
            """)

            rows_updated = cursor.rowcount
            print(f"   Updated {rows_updated} users with lastLogin to 'accepted'")

            # Set remaining users (who haven't logged in) to 'accepted' with their creation date
            cursor.execute("""
                UPDATE users
                SET invitation_status = 'accepted',
                    invitation_accepted_at = "createdAt"
                WHERE "lastLogin" IS NULL AND invitation_status = 'pending'
            """)

            rows_updated = cursor.rowcount
            print(f"   Updated {rows_updated} users without last_login to 'accepted' (using created_at)")

            conn.commit()
            print("\n✅ Successfully added invitation status columns!")
        else:
            print("\n✅ Invitation status columns already exist!")

        # Display all users with their invitation status
        print("\n" + "="*60)
        print("ALL USERS - INVITATION STATUS:")
        print("="*60)
        cursor.execute("""
            SELECT email, name, role, invitation_status,
                   invitation_accepted_at, "lastLogin", "createdAt"
            FROM users
            ORDER BY "createdAt"
        """)

        users = cursor.fetchall()
        for user in users:
            email, name, role, inv_status, inv_accepted, last_login, created = user
            status_icon = "✓" if inv_status == 'accepted' else "⏳"
            print(f"{status_icon} {name} ({email})")
            print(f"   Role: {role}")
            print(f"   Invitation: {inv_status}")
            print(f"   Accepted at: {inv_accepted}")
            print(f"   Last login: {last_login}")
            print()

        cursor.close()
        conn.close()
        print("✅ Done!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_invitation_columns()
