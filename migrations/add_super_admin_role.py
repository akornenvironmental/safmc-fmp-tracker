"""Add 'super_admin' to user_roles enum

Run this migration with:
python migrations/add_super_admin_role.py
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/safmc_fmp_tracker')

def upgrade():
    """Add 'super_admin' to user_roles enum"""
    engine = create_engine(DATABASE_URL)

    print("=" * 60)
    print("SAFMC FMP Tracker - Add super_admin Role Migration")
    print("=" * 60)
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    print()

    with engine.connect() as conn:
        # Check current enum values
        print("Checking current user_roles enum values...")
        result = conn.execute(text("""
            SELECT unnest(enum_range(NULL::user_roles))::text AS role;
        """))
        current_roles = [row[0] for row in result]
        print(f"Current roles: {current_roles}")

        if 'super_admin' in current_roles:
            print("✓ 'super_admin' role already exists in enum")
            return

        # Add 'super_admin' to the enum
        print("\nAdding 'super_admin' to user_roles enum...")
        conn.execute(text("""
            ALTER TYPE user_roles ADD VALUE IF NOT EXISTS 'super_admin';
        """))
        conn.commit()
        print("✓ 'super_admin' role added to enum")

        # Verify the change
        print("\nVerifying updated enum values...")
        result = conn.execute(text("""
            SELECT unnest(enum_range(NULL::user_roles))::text AS role;
        """))
        updated_roles = [row[0] for row in result]
        print(f"Updated roles: {updated_roles}")

    print("\n" + "=" * 60)
    print("Migration complete! The super_admin role can now be used.")
    print("=" * 60)

def downgrade():
    """Cannot remove enum values in PostgreSQL easily

    Note: PostgreSQL does not support removing enum values directly.
    To remove 'super_admin', you would need to:
    1. Update all users with 'super_admin' role to another role
    2. Drop the enum type
    3. Recreate it without 'super_admin'
    4. Restore all role assignments

    This is complex and risky, so downgrade is not implemented.
    """
    print("⚠️  Downgrade not supported for enum value additions")
    print("PostgreSQL does not allow removing enum values")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--down', action='store_true', help='Run downgrade')
    args = parser.parse_args()

    if args.down:
        downgrade()
    else:
        upgrade()
