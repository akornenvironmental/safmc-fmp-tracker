"""
Fix Aaron's user record:
1. Set invitation_status to 'accepted'
2. Set invitation_accepted_at to creation date
"""
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import app from app.py
from app import app, db
from src.models.user import User

def fix_aaron_user():
    """Fix Aaron's user record"""
    with app.app_context():
        # Find Aaron's user
        aaron = User.query.filter_by(email='aaron.kornbluth@gmail.com').first()

        if not aaron:
            print("❌ Aaron's user not found!")
            print("\nSearching for all users...")
            all_users = User.query.all()
            for user in all_users:
                print(f"  - {user.email} ({user.role}) - Invitation: {user.invitation_status}")
            return

        print(f"Found user: {aaron.email}")
        print(f"  Current invitation_status: {aaron.invitation_status}")
        print(f"  Current invitation_accepted_at: {aaron.invitation_accepted_at}")
        print(f"  Role: {aaron.role}")
        print(f"  Active: {aaron.is_active}")
        print(f"  Created: {aaron.created_at}")

        # Update invitation status
        if aaron.invitation_status != 'accepted':
            aaron.invitation_status = 'accepted'
            aaron.invitation_accepted_at = aaron.created_at  # Set to creation date
            db.session.commit()
            print("\n✅ Successfully updated Aaron's invitation status to 'accepted'")
        else:
            print("\n✅ Aaron's invitation status is already 'accepted'")

        # Display all users and their statuses
        print("\n" + "="*60)
        print("ALL USERS:")
        print("="*60)
        all_users = User.query.all()
        for user in all_users:
            status = "✓ Accepted" if user.invitation_status == 'accepted' else "⏳ Pending"
            print(f"{user.name or 'No name'} ({user.email})")
            print(f"  Role: {user.role}")
            print(f"  Invitation: {status}")
            print(f"  Active: {'Yes' if user.is_active else 'No'}")
            print()

if __name__ == '__main__':
    fix_aaron_user()
