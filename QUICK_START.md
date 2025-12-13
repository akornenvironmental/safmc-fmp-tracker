# Quick Start - Local Development

## Prerequisites Checklist

Before you start, make sure you have:

- [ ] **PostgreSQL installed** (needed for database)
  - Install: `brew install postgresql@15`
  - Start: `brew services start postgresql@15`
  - Create DB: `createdb safmc_fmp_tracker`
  - Or use [Postgres.app](https://postgresapp.com/) (easier GUI option)

- [ ] **Python 3.9+** (✓ you have 3.14)

- [ ] **Node.js & npm** (for React frontend)
  - Check: `node --version` and `npm --version`
  - Install: https://nodejs.org/

## One-Time Setup

Run these commands once:

```bash
# Navigate to project
cd /Users/akorn/Desktop/SAFMC-FMP

# 1. Create Python virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Create environment file
cp .env.example .env
# Edit .env if needed (defaults work fine for local dev)

# 5. Install frontend dependencies
cd client
npm install
cd ..
```

## Daily Development Workflow

### Option 1: Automatic (Recommended)

Run this single command:
```bash
./start-dev.sh
```

This will:
- Check your environment
- Start backend on port 5000
- Start frontend on port 5173
- Open both in your terminal

Press `Ctrl+C` to stop everything.

### Option 2: Manual (Two Terminal Windows)

**Terminal 1 - Backend:**
```bash
cd /Users/akorn/Desktop/SAFMC-FMP
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/akorn/Desktop/SAFMC-FMP/client
npm run dev
```

### Option 3: Semi-Automatic (Opens Terminal Windows)

```bash
./start-dev-manual.sh
```

This opens 2 terminal windows for you automatically.

## Access Your Application

Once both servers are running:

🌐 **Open:** http://localhost:5173

- Backend API: http://localhost:5000
- Frontend Dev Server: http://localhost:5173

## Feedback Management Features

Your feedback page (`/feedback-management`) includes:

### ✅ Quick Actions (already implemented!)

1. **Delete Feedback**
   - Red "Delete" button in the modal
   - Confirms before deleting
   - Permanently removes feedback from database

2. **Mark as Completed**
   - Green "Accept" button
   - Marks feedback status as "resolved"
   - Adds admin notes and timestamp

3. **Archive Feedback**
   - Gray "Archive" button
   - Moves to archived status
   - Keeps record but hides from active view

### 📍 Where to Find the Code

- **Frontend:** `client/src/pages/FeedbackManagement.jsx`
  - Delete function: lines 97-127
  - Accept function: lines 129-137
  - UI buttons: lines 372-396

- **Backend API:** `src/routes/api_routes.py`
  - DELETE endpoint: lines 2014-2044
  - PATCH endpoint (update status): lines 1956-2010

## Making Changes

1. **Frontend Changes** (JavaScript/React)
   - Edit files in `client/src/`
   - Vite auto-reloads on save (instant preview!)
   - No need to restart server

2. **Backend Changes** (Python/Flask)
   - Edit files in `src/` or `app.py`
   - Must restart: Press `Ctrl+C` then run `python app.py` again

3. **Test Your Changes**
   - Make changes
   - Test in browser at http://localhost:5173
   - Check terminal for errors

4. **Deploy to Production**
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```
   Render will auto-deploy from GitHub.

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
brew services list

# Restart if needed
brew services restart postgresql@15
```

### Port Already in Use
```bash
# Kill process on port 5000 (backend)
lsof -ti:5000 | xargs kill -9

# Kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```

### Python Package Errors
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Build Errors
```bash
cd client
rm -rf node_modules package-lock.json
npm install
```

## Common Tasks

### View Database
```bash
# Connect to PostgreSQL
psql safmc_fmp_tracker

# List all tables
\dt

# View feedback table
SELECT * FROM user_feedback ORDER BY created_at DESC LIMIT 10;

# Exit psql
\q
```

### Create Admin User
You'll need admin access to view the feedback page. If you need to create an admin user, you can do it through the database:

```sql
-- Connect to database
psql safmc_fmp_tracker

-- Create admin user (adjust email/password as needed)
INSERT INTO users (email, name, role)
VALUES ('admin@example.com', 'Admin User', 'admin');
```

### Reset Database
```bash
# Drop and recreate database (WARNING: deletes all data!)
dropdb safmc_fmp_tracker
createdb safmc_fmp_tracker

# Restart app to recreate tables
python app.py
```

## Need More Help?

See the full guide: `LOCAL_DEV_SETUP.md`
