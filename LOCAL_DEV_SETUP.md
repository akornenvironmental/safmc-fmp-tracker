# Local Development Setup Guide

This guide will help you set up the SAFMC FMP Tracker for local development so you can quickly make changes without deploying to Render.

## Prerequisites

You need:
- Python 3.9+ (✓ You have Python 3.14)
- PostgreSQL database
- Node.js and npm (for the React frontend)

## Step 1: Install PostgreSQL

### On macOS (using Homebrew):
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create your database
createdb safmc_fmp_tracker
```

### Alternative: Use Postgres.app
Download from: https://postgresapp.com/
- Simpler GUI interface
- Creates database automatically

## Step 2: Set Up Python Backend

### 2.1 Create Virtual Environment
```bash
cd /Users/akorn/Desktop/SAFMC-FMP
python3 -m venv venv
source venv/bin/activate  # Activates the virtual environment
```

### 2.2 Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2.3 Create Environment File
```bash
cp .env.example .env
```

Then edit `.env` with your settings:
```env
# Database Configuration
DATABASE_URL=postgresql://localhost/safmc_fmp_tracker

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-local-secret-key-change-me
PORT=5000

# Scheduler Configuration (optional for local dev)
ENABLE_SCHEDULER=false

# AI Integration (optional - only if you want AI features)
CLAUDE_API_KEY=your-key-here-if-needed
ANTHROPIC_API_KEY=your-key-here-if-needed
```

### 2.4 Initialize the Database
```bash
# Run migrations to create all tables
flask db upgrade

# Or if that doesn't work, just start the app (it will auto-create tables)
python app.py
```

The app will automatically create all necessary tables including the `user_feedback` table.

## Step 3: Set Up React Frontend

### 3.1 Install Node Dependencies
```bash
cd client
npm install
```

### 3.2 Configure Frontend API URL
The frontend is already configured to use `http://localhost:5000` for local development (see `client/src/config.js`).

### 3.3 Build Frontend for Development
```bash
npm run dev
```

This starts the Vite dev server on `http://localhost:5173`

## Step 4: Run Both Servers

You'll need two terminal windows:

### Terminal 1: Backend (Python/Flask)
```bash
cd /Users/akorn/Desktop/SAFMC-FMP
source venv/bin/activate
python app.py
```

Backend will run on: `http://localhost:5000`

### Terminal 2: Frontend (React/Vite)
```bash
cd /Users/akorn/Desktop/SAFMC-FMP/client
npm run dev
```

Frontend will run on: `http://localhost:5173`

## Step 5: Access Your Application

Open your browser to: `http://localhost:5173`

The React dev server will proxy API requests to your Flask backend on port 5000.

## Quick Commands Reference

### Start Development (both servers)
```bash
# Terminal 1 - Backend
cd /Users/akorn/Desktop/SAFMC-FMP && source venv/bin/activate && python app.py

# Terminal 2 - Frontend
cd /Users/akorn/Desktop/SAFMC-FMP/client && npm run dev
```

### Stop Development
- Press `Ctrl+C` in each terminal window

## Feedback Page Features

The feedback page (`/feedback-management`) already includes:

✓ **Delete Feedback**: Red "Delete" button in the modal
✓ **Mark as Completed**: Green "Accept" button marks feedback as "resolved"
✓ **Quick Actions**: Archive, Accept, or Delete with one click
✓ **Status Updates**: Change status manually with dropdown

These features are already implemented in:
- Frontend: `client/src/pages/FeedbackManagement.jsx` (lines 97-127, 129-137, 374-396)
- Backend: `src/routes/api_routes.py` (lines 1956-2044)

## Troubleshooting

### Database Connection Issues
If you get "connection refused" errors:
```bash
# Check if PostgreSQL is running
brew services list

# Restart PostgreSQL
brew services restart postgresql@15

# Or if using Postgres.app, open the app and click "Start"
```

### Port Already in Use
If port 5000 or 5173 is already taken:
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Missing Python Packages
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Build Issues
```bash
cd client
rm -rf node_modules package-lock.json
npm install
```

## Testing Feedback Features

1. Create an admin user (you'll need to do this via database or authentication system)
2. Navigate to `/feedback-management`
3. Click on any feedback item to open the modal
4. Test the quick action buttons:
   - **Accept** (green): Marks as resolved
   - **Archive** (gray): Archives the feedback
   - **Delete** (red): Permanently deletes (with confirmation)

## Next Steps

Once your local environment is running:
1. Make changes to the code
2. Frontend auto-reloads on save (Vite hot reload)
3. Backend requires restart (Ctrl+C then `python app.py` again)
4. Test your changes locally
5. Commit and push to GitHub when ready
6. Render will auto-deploy from GitHub

## Need Help?

Check these files:
- Backend API: `src/routes/api_routes.py` (search for "feedback")
- Frontend Page: `client/src/pages/FeedbackManagement.jsx`
- Database Models: `app.py` (user_feedback table initialization)
