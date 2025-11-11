# User Logging & Permissions Migration

## Overview
This migration adds comprehensive user activity logging and role-based permissions to the SAFMC FMP Tracker.

## What's Included

### Backend (Already Implemented)
- ✅ `user_activity_logs` table schema
- ✅ Permission middleware (`@require_admin`, `@require_super_admin`)
- ✅ Activity logging middleware (`@log_activity`)
- ✅ User management API (CRUD operations - super admin only)
- ✅ Activity log viewing API (admin+)
- ✅ Auth routes updated with activity logging

### Migration Files
1. `add_user_logging_system.py` - Python migration script (requires SQLAlchemy)
2. **`add_user_logging_system.sql`** - Standalone SQL file (recommended)

## How to Run the Migration

### Option 1: Via Render Shell (Recommended)

1. Go to your Render dashboard: https://dashboard.render.com
2. Navigate to your backend service (SAFMC FMP Tracker backend)
3. Click "Shell" in the top right corner
4. Run the following command:

```bash
psql $DATABASE_URL -f migrations/add_user_logging_system.sql
```

This will:
- Add 'super_admin' to the user_roles ENUM
- Create the user_activity_logs table with all indexes
- Set up full-text search trigger

### Option 2: Via Python Script (Alternative)

If you prefer the Python script:

```bash
# In Render Shell
python migrations/add_user_logging_system.py
```

This provides more detailed output but requires the script to run in the proper environment.

## Verification

After running the migration, verify it worked:

```sql
-- Check if super_admin role exists
SELECT enumlabel FROM pg_enum WHERE enumtypid = (
    SELECT oid FROM pg_type WHERE typname = 'user_roles'
);

-- Check if user_activity_logs table exists
\dt user_activity_logs

-- Check indexes
\di idx_activity_*
```

## Next Steps

Once the migration is complete:

1. **Promote a user to super_admin** (do this via Render Shell):
   ```sql
   UPDATE users SET role = 'super_admin' WHERE email = 'your-email@example.com';
   ```

2. **Test the endpoints**:
   - GET `/api/admin/users` - List all users
   - POST `/api/admin/users` - Create a new user
   - GET `/api/admin/activity-logs` - View activity logs

3. **Build the frontend UI** (next task):
   - User management page (super admin only)
   - Activity log viewer (admin+)
   - User profile display

## API Endpoints

### User Management (Super Admin Only)
- `GET /api/admin/users` - List users (with pagination & filtering)
- `GET /api/admin/users/<id>` - Get user details
- `POST /api/admin/users` - Create user
- `PUT /api/admin/users/<id>` - Update user
- `DELETE /api/admin/users/<id>` - Delete user

### Activity Logs (Admin+)
- `GET /api/admin/activity-logs` - Get logs (with filtering)
- `GET /api/admin/activity-logs/stats` - Get statistics
- `GET /api/admin/activity-logs/export` - Export logs

## Activity Types

The system logs these activities:
- **Auth**: login, logout, login_failed
- **Users**: created, updated, deleted, role_changed
- **Actions**: viewed, created, updated, deleted, exported
- **Meetings**: viewed, created, updated, deleted, exported
- **Comments**: viewed, created, updated, deleted, exported
- **Assessments**: viewed, synced, exported
- **Data**: scraped, exported, imported, bulk_updated
- **AI**: query, query_failed
- **Admin**: settings_viewed, settings_updated, logs_viewed, logs_exported

## Rollback

If you need to rollback:

```sql
DROP TABLE IF EXISTS user_activity_logs CASCADE;
-- Note: Cannot remove ENUM values in PostgreSQL
```

## Support

If you encounter issues:
1. Check the Render logs for error messages
2. Ensure DATABASE_URL is properly set
3. Verify the users table exists and has the correct structure
