#!/usr/bin/env python3
"""
Add admin users to the database

USAGE:
On Render, run via shell:
  python add_admin_users.py

Locally with .env:
  python add_admin_users.py
"""
import os
import sys

# Try to load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import psycopg2

# Admin users to add
admin_users = [
    ("Jake Spencer", "jakespencer6596@gmail.com"),
    ("Lily Maddox", "lilymaddox14@gmail.com"),
    ("Jessie Mandirola", "mandiroj@gmail.com"),
    ("Sarah Gaichas", "sgaichas@gmail.com")
]

def add_admin_users():
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        print("On Render, make sure to run this via the shell where DATABASE_URL is available")
        sys.exit(1)
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Adding admin users...")
        
        for name, email in admin_users:
            # Check if user exists
            cursor.execute("SELECT id, is_admin FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            
            if result:
                user_id, is_admin = result
                if not is_admin:
                    cursor.execute("UPDATE users SET is_admin = TRUE WHERE id = %s", (user_id,))
                    print(f"✓ Updated {name} ({email}) to admin")
                else:
                    print(f"• {name} ({email}) is already an admin")
            else:
                # Pre-create user as admin (they'll use magic link on first login)
                cursor.execute(
                    "INSERT INTO users (name, email, is_admin) VALUES (%s, %s, TRUE)",
                    (name, email)
                )
                print(f"✓ Pre-created admin user {name} ({email})")
        
        conn.commit()
        print("\n✅ All admin users processed successfully!")
        
        # Verify
        cursor.execute("SELECT name, email FROM users WHERE is_admin = TRUE ORDER BY name")
        admins = cursor.fetchall()
        print(f"\nCurrent admin users ({len(admins)}):")
        for name, email in admins:
            print(f"  • {name} ({email})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    add_admin_users()
