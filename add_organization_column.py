"""
Add organization column to users table
"""
import psycopg2

DATABASE_URL = "postgresql://safmc_user:SvMkI8VcP70Xjpm3YkfzAMNxURAhwZ0n@dpg-d3tpj9hbh1hs73alm8m0-a.oregon-postgres.render.com/safmc_interviews"

def add_organization_column():
    """Add organization column"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check if column exists
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'organization'
        """)
        exists = cursor.fetchone()

        if not exists:
            print("Adding organization column...")
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN organization VARCHAR(255)
            """)
            conn.commit()
            print("✅ Added organization column")

            # Populate with some default values based on email domains
            print("\nPopulating organization data from email domains...")
            cursor.execute("""
                UPDATE users
                SET organization = CASE
                    WHEN email LIKE '%akorn%' THEN 'akorn environmental'
                    WHEN email LIKE '%safmc%' THEN 'SAFMC'
                    WHEN email LIKE '%cynoscion%' THEN 'Cynoscion Environmental Consulting LLC'
                    WHEN email LIKE '%bennett%' THEN 'Bennett Nickerson Environmental Consulting'
                    WHEN email LIKE '%hydra%' THEN 'Hydra Scientific LLC'
                    ELSE NULL
                END
                WHERE organization IS NULL
            """)
            conn.commit()
            rows_updated = cursor.rowcount
            print(f"✅ Updated {rows_updated} users with organization data")
        else:
            print("✅ Organization column already exists")

        # Display all users
        print("\n" + "="*60)
        print("ALL USERS WITH ORGANIZATIONS:")
        print("="*60)
        cursor.execute("""
            SELECT email, name, organization, role
            FROM users
            ORDER BY "createdAt"
        """)

        users = cursor.fetchall()
        for user in users:
            email, name, org, role = user
            role_icon = "👑" if role == 'super_admin' else ("🔧" if role == 'admin' else "👤")
            print(f"{role_icon} {name} ({email})")
            print(f"   Organization: {org or '(not set)'}")
            print(f"   Role: {role}")
            print()

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_organization_column()
