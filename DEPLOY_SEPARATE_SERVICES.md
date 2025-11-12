# Deploying Frontend and Backend as Separate Services

## Overview

This guide walks you through splitting the monolithic deployment into two separate services:
- **safmc-fmp-tracker-backend**: Python/Flask API only
- **safmc-fmp-tracker-frontend**: React Static Site (NEW)

## Benefits
- Faster frontend deployments (no backend rebuild)
- Better caching via CDN for static assets
- Independent scaling
- Cleaner separation of concerns

---

## Step 1: Rename Existing Service (Backend)

In Render dashboard for `safmc-fmp-tracker`:

1. Go to Settings → General
2. Change Name from `safmc-fmp-tracker` to `safmc-fmp-tracker-backend`
3. Note the backend URL (e.g., `https://safmc-fmp-tracker-backend.onrender.com` or keep current URL)

---

## Step 2: Update Backend Build (Remove Frontend)

The backend currently builds both frontend and backend. Let's make it backend-only.

### Option A: Update build.sh (Simpler - Keep Monolith Temporarily)
Keep the current setup but don't serve frontend. The frontend Static Site will handle that.

**No changes needed** - Just deploy the new frontend!

### Option B: Backend-Only build.sh (Cleaner)
Update `build.sh` to remove frontend building:

```bash
#!/bin/bash
set -ex

echo "================================================"
echo "=== SAFMC FMP Tracker Backend Build ==="
echo "================================================"

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Setting permissions ==="
chmod +x start.sh

echo "================================================"
echo "=== Backend build complete ==="
echo "================================================"
```

---

## Step 3: Create New Static Site (Frontend)

### In Render Dashboard:

1. Click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure the Static Site:

**Name:** `safmc-fmp-tracker-frontend`

**Branch:** `main` (or your deployment branch)

**Root Directory:** `client`

**Build Command:**
```
npm install && npm run build
```

**Publish Directory:**
```
dist
```

### Environment Variables for Frontend:

Add this environment variable:

**Key:** `VITE_API_BASE_URL`
**Value:** `https://safmc-fmp-tracker-backend.onrender.com`
(or whatever your backend URL is)

---

## Step 4: Update Backend CORS

The backend needs to allow requests from the new frontend domain.

### In backend `app.py`, update CORS configuration:

Find the CORS setup and add the frontend URL:

```python
from flask_cors import CORS

# Allow frontend domain
CORS(app, origins=[
    "http://localhost:5173",  # Local development
    "https://safmc-fmp-tracker-frontend.onrender.com",  # Production frontend
    "https://your-custom-domain.com"  # If you have a custom domain
])
```

---

## Step 5: Custom Domains (Optional)

If using custom domains:

1. **Backend:** `api.safmc-fmp-tracker.com`
2. **Frontend:** `safmc-fmp-tracker.com` or `app.safmc-fmp-tracker.com`

Update `VITE_API_BASE_URL` to use your custom backend domain.

---

## Deployment URLs

After setup, you'll have:

- **Backend API:** `https://safmc-fmp-tracker-backend.onrender.com`
- **Frontend App:** `https://safmc-fmp-tracker-frontend.onrender.com`
- **Database:** `safmc-fmp-tracker-db` (unchanged)

---

## Testing the Setup

### 1. Test Backend Directly:
```bash
curl https://safmc-fmp-tracker-backend.onrender.com/health
```

Should return: `{"status": "healthy", ...}`

### 2. Test Frontend:
Visit: `https://safmc-fmp-tracker-frontend.onrender.com`

Should load the React app and make API calls to the backend.

### 3. Check Browser Network Tab:
- Open DevTools → Network
- Look for API calls going to `safmc-fmp-tracker-backend.onrender.com`
- Should see successful responses (not 404 or CORS errors)

---

## Rollback Plan

If something goes wrong:

1. **Keep backend service as-is** (it still has the built frontend in `client/dist`)
2. Simply delete the new frontend Static Site
3. The monolithic deployment continues working at the backend URL

---

## Current vs. New Architecture

### Current (Monolithic):
```
safmc-fmp-tracker (Web Service)
├── Build: Python + React build
├── Serve: Flask serves API + static React files
└── URL: https://safmc-fmp-tracker.onrender.com
```

### New (Separated):
```
safmc-fmp-tracker-backend (Web Service)
├── Build: Python only
├── Serve: Flask API only
└── URL: https://safmc-fmp-tracker-backend.onrender.com

safmc-fmp-tracker-frontend (Static Site)
├── Build: npm build
├── Serve: CDN-cached static files
└── URL: https://safmc-fmp-tracker-frontend.onrender.com
```

---

## FAQ

**Q: Will my database connection break?**
A: No. The backend service keeps the same DATABASE_URL environment variable.

**Q: Will magic link auth still work?**
A: Yes, as long as CORS is configured properly and cookies are handled correctly.

**Q: What happens to the old URL?**
A: It will redirect or you can keep it pointing to the backend. Update users to use the new frontend URL.

**Q: How do I update just the frontend now?**
A: Commit frontend changes → Render auto-deploys **only** the frontend Static Site (fast!).

**Q: How do I update just the backend now?**
A: Commit backend changes → Render auto-deploys **only** the backend Web Service.

---

## Next Steps

1. Rename existing service to `safmc-fmp-tracker-backend` ✓
2. Create new Static Site `safmc-fmp-tracker-frontend` ✓
3. Update backend CORS
4. Test the setup
5. Update any documentation/links with new frontend URL
