"""
Create users table and first admin user

Run this on Render via Shell:
python create_user_table.py
"""
import os
import uuid
from sqlalchemy import create_engine, text

# Get database URL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/safmc_fmp_tracker')

print("=" * 60)
print("SAFMC FMP Tracker - User Table Setup")
print("=" * 60)
print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
print()

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Create ENUM type for roles
    print("Creating user_roles ENUM type...")
    conn.execute(text("""
        DO $$ BEGIN
            CREATE TYPE user_roles AS ENUM ('admin', 'editor');
        EXCEPTION
            WHEN duplicate_object THEN
                RAISE NOTICE 'user_roles type already exists, skipping';
        END $$;
    """))
    conn.commit()
    print("✓ ENUM type ready")

    # Create users table
    print("\nCreating users table...")
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(255),
            role user_roles NOT NULL DEFAULT 'editor',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            last_login TIMESTAMP,
            login_token VARCHAR(255),
            token_expiry TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """))
    conn.commit()
    print("✓ Users table created")

    # Create indexes
    print("\nCreating indexes...")
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
    """))
    conn.commit()
    print("✓ Indexes created")

    # Check if admin user exists
    print("\nChecking for existing admin user...")
    result = conn.execute(text("SELECT email FROM users WHERE role = 'admin' LIMIT 1"))
    existing_admin = result.fetchone()

    if existing_admin:
        print(f"✓ Admin user already exists: {existing_admin[0]}")
    else:
        # Create admin user
        print("\nCreating admin user...")
        admin_email = input("Enter admin email (default: aaron.kornbluth@gmail.com): ").strip() or "aaron.kornbluth@gmail.com"
        admin_name = input("Enter admin name (default: Aaron Kornbluth): ").strip() or "Aaron Kornbluth"

        user_id = str(uuid.uuid4())
        conn.execute(text("""
            INSERT INTO users (id, email, name, role, is_active, created_at, updated_at)
            VALUES (:id, :email, :name, 'admin', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {"id": user_id, "email": admin_email, "name": admin_name})
        conn.commit()
        print(f"✓ Admin user created: {admin_email}")

print("\n" + "=" * 60)
print("Setup complete! You can now log in to the application.")
print("=" * 60)
