"""
Update Aaron's role to super_admin
"""
import psycopg2

DATABASE_URL = "postgresql://safmc_user:SvMkI8VcP70Xjpm3YkfzAMNxURAhwZ0n@dpg-d3tpj9hbh1hs73alm8m0-a.oregon-postgres.render.com/safmc_interviews"

def update_aaron_role():
    """Update Aaron to super_admin"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("Updating Aaron Kornbluth to super_admin...")
        cursor.execute("""
            UPDATE users
            SET role = 'super_admin'
            WHERE email = 'aaron.kornbluth@gmail.com'
        """)
        conn.commit()
        print("✅ Updated aaron.kornbluth@gmail.com to super_admin")

        # Verify
        print("\n" + "="*60)
        print("ALL USERS:")
        print("="*60)
        cursor.execute("""
            SELECT email, name, role, invitation_status, "isActive"
            FROM users
            ORDER BY "createdAt"
        """)

        users = cursor.fetchall()
        for user in users:
            email, name, role, inv_status, is_active = user
            status_icon = "✓" if inv_status == 'accepted' else "⏳"
            role_icon = "👑" if role == 'super_admin' else ("🔧" if role == 'admin' else "👤")
            active_icon = "✅" if is_active else "❌"
            print(f"{status_icon} {role_icon} {active_icon} {name} ({email})")
            print(f"   Role: {role}")
            print()

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    update_aaron_role()
