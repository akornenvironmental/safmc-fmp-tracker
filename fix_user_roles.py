"""
Fix user roles to match the expected structure
Aaron should be super_admin
"""
import psycopg2

# Render database URL
DATABASE_URL = "postgresql://safmc_user:SvMkI8VcP70Xjpm3YkfzAMNxURAhwZ0n@dpg-d3tpj9hbh1hs73alm8m0-a.oregon-postgres.render.com/safmc_interviews"

def fix_user_roles():
    """Update user roles"""
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check what role enum values exist
        print("\nChecking role enum values...")
        cursor.execute("""
            SELECT e.enumlabel
            FROM pg_enum e
            JOIN pg_type t ON e.enumtypid = t.oid
            WHERE t.typname = 'user_roles'
            ORDER BY e.enumsortorder
        """)
        role_values = cursor.fetchall()
        print("Available roles:", [r[0] for r in role_values])

        # If super_admin doesn't exist in enum, we need to add it
        has_super_admin = any(r[0] == 'super_admin' for r in role_values)

        if not has_super_admin:
            print("\nAdding super_admin to role enum...")
            cursor.execute("ALTER TYPE user_roles ADD VALUE 'super_admin'")
            conn.commit()
            print("✅ Added super_admin role")

        # Update Aaron to super_admin
        print("\n" + "="*60)
        print("UPDATING AARON'S ROLE TO SUPER_ADMIN:")
        print("="*60)
        cursor.execute("""
            UPDATE users
            SET role = 'super_admin'
            WHERE email = 'aaron.kornbluth@gmail.com'
        """)
        conn.commit()
        print("✅ Updated aaron.kornbluth@gmail.com to super_admin")

        # Display all users with their roles
        print("\n" + "="*60)
        print("ALL USERS - ROLES:")
        print("="*60)
        cursor.execute("""
            SELECT email, name, role, invitation_status, "lastLogin"
            FROM users
            ORDER BY "createdAt"
        """)

        users = cursor.fetchall()
        for user in users:
            email, name, role, inv_status, last_login = user
            status_icon = "✓" if inv_status == 'accepted' else "⏳"
            role_icon = "👑" if role == 'super_admin' else "👤"
            print(f"{status_icon} {role_icon} {name} ({email})")
            print(f"   Role: {role}")
            print(f"   Invitation: {inv_status}")
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
    fix_user_roles()
