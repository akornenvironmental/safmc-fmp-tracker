# Invitation Tracking Migration

This migration adds invitation tracking fields to the users table.

## Fields Added
- `invitation_status` - ENUM('pending', 'accepted') - Tracks whether user has accepted invitation
- `invitation_accepted_at` - TIMESTAMP - When user accepted invitation

## Running on Render

### Option 1: Via Render Shell
1. Go to Render Dashboard
2. Navigate to your web service
3. Click "Shell" tab
4. Run:
```bash
python3 migrations/add_invitation_tracking_to_users.py
```

### Option 2: Via Manual SQL
Connect to your Render PostgreSQL database and run:
```sql
-- Create enum type if it doesn't exist
DO $$ BEGIN
    CREATE TYPE invitation_status AS ENUM ('pending', 'accepted');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Add columns
ALTER TABLE users
ADD COLUMN IF NOT EXISTS invitation_status invitation_status DEFAULT 'pending';

ALTER TABLE users
ADD COLUMN IF NOT EXISTS invitation_accepted_at TIMESTAMP;
```

## Verification
After running, verify with:
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name IN ('invitation_status', 'invitation_accepted_at');
```

## Related Code Changes
- `/src/models/user.py` - Model updated with new fields
- `/src/routes/auth_routes.py` - Login flow marks invitation as accepted
- `/client/src/pages/UserManagement.jsx` - UI displays invitation status
