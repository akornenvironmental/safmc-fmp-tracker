"""
Check database structure to understand the role column
"""
import psycopg2

DATABASE_URL = "postgresql://safmc_user:SvMkI8VcP70Xjpm3YkfzAMNxURAhwZ0n@dpg-d3tpj9hbh1hs73alm8m0-a.oregon-postgres.render.com/safmc_interviews"

def check_db():
    """Check database structure"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Get all enum types
        print("All enum types in database:")
        cursor.execute("""
            SELECT t.typname, e.enumlabel
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            ORDER BY t.typname, e.enumsortorder
        """)
        enums = cursor.fetchall()
        current_type = None
        for typname, enumlabel in enums:
            if typname != current_type:
                print(f"\n{typname}:")
                current_type = typname
            print(f"  - {enumlabel}")

        # Get role column details
        print("\n" + "="*60)
        print("Role column details:")
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'role'
        """)
        result = cursor.fetchone()
        if result:
            print(f"  Column: {result[0]}")
            print(f"  Data type: {result[1]}")
            print(f"  UDT name: {result[2]}")

        # Try to get actual role values from users table
        print("\n" + "="*60)
        print("Current role values in users table:")
        cursor.execute("""
            SELECT DISTINCT role FROM users
        """)
        roles = cursor.fetchall()
        for role in roles:
            print(f"  - {role[0]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_db()
