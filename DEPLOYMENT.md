# SAFMC FMP Tracker - Deployment Guide

## Quick Deploy to Render (Recommended)

### Prerequisites
1. GitHub account
2. Render account (sign up at https://render.com - free tier available)
3. Your code pushed to a GitHub repository

### Step-by-Step Deployment

#### 1. Prepare Your Repository

```bash
cd safmc-fmp-tracker

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: SAFMC FMP Tracker"

# Create repository on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/safmc-fmp-tracker.git
git branch -M main
git push -u origin main
```

#### 2. Deploy to Render

**Option A: Using Blueprint (Automatic - Recommended)**

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Blueprint"
3. Connect your GitHub account
4. Select your `safmc-fmp-tracker` repository
5. Render will automatically:
   - Detect `render.yaml`
   - Create PostgreSQL database
   - Set up web service
   - Configure environment variables
6. Click "Apply" to start deployment

**Option B: Manual Setup**

1. **Create Database**
   - Go to Render Dashboard
   - Click "New +" → "PostgreSQL"
   - Name: `safmc-fmp-db`
   - Plan: Free
   - Click "Create Database"
   - Copy the "Internal Database URL"

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your repository
   - Configure:
     - Name: `safmc-fmp-tracker`
     - Environment: Python 3
     - Region: Oregon (or your preference)
     - Branch: main
     - Build Command: `pip install -r requirements.txt && flask db upgrade`
     - Start Command: `gunicorn app:app`
     - Plan: Free

3. **Add Environment Variables**
   - In your web service dashboard, go to "Environment"
   - Add:
     ```
     FLASK_ENV=production
     DATABASE_URL=[paste your database URL]
     SECRET_KEY=[generate a random string]
     ENABLE_SCHEDULER=true
     ```

#### 3. Generate Secret Key

To generate a secure SECRET_KEY:

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

#### 4. Verify Deployment

Once deployed, your app will be available at:
```
https://safmc-fmp-tracker.onrender.com
```

Test the health endpoint:
```bash
curl https://safmc-fmp-tracker.onrender.com/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-03T...",
  "database": "connected"
}
```

#### 5. Initialize Data

Trigger the initial scraping:

```bash
curl -X POST https://safmc-fmp-tracker.onrender.com/api/scrape/all
```

This will populate your database with current SAFMC data.

## Local Development Setup

### 1. Clone and Setup

```bash
git clone https://github.com/YOUR_USERNAME/safmc-fmp-tracker.git
cd safmc-fmp-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

Install PostgreSQL locally:

**macOS:**
```bash
brew install postgresql
brew services start postgresql
createdb safmc_fmp_tracker
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql
sudo service postgresql start
sudo -u postgres createdb safmc_fmp_tracker
```

**Windows:**
- Download and install from https://www.postgresql.org/download/windows/
- Use pgAdmin to create database `safmc_fmp_tracker`

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://localhost/safmc_fmp_tracker
FLASK_ENV=development
SECRET_KEY=dev-secret-key
PORT=5000
ENABLE_SCHEDULER=true
```

### 4. Initialize Database

```bash
python init_db.py
```

### 5. Run Application

```bash
python app.py
```

Visit: http://localhost:5000

### 6. Load Initial Data

In another terminal:
```bash
curl -X POST http://localhost:5000/api/scrape/all
```

## Troubleshooting

### Common Issues

**Issue: "ModuleNotFoundError"**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**Issue: "Database connection failed"**
- Check DATABASE_URL is correct
- Verify PostgreSQL is running
- Test connection: `psql -d safmc_fmp_tracker`

**Issue: "Table does not exist"**
```bash
python init_db.py
```

**Issue: "Port already in use"**
```bash
# Change PORT in .env or:
lsof -ti:5000 | xargs kill -9  # macOS/Linux
```

### Render-Specific Issues

**Issue: Build fails**
- Check build logs in Render dashboard
- Verify `requirements.txt` is correct
- Ensure all dependencies are compatible

**Issue: Database not connecting**
- Verify DATABASE_URL environment variable
- Check database is in same region as web service
- Ensure Internal Database URL is used (not External)

**Issue: App crashes after deployment**
- Check application logs in Render dashboard
- Verify all environment variables are set
- Check for missing dependencies

## Monitoring and Maintenance

### Check Application Logs

**Render:**
- Go to your web service dashboard
- Click "Logs" tab
- View real-time logs

**Local:**
```bash
# Logs are printed to console
# Or check application-specific log files
```

### Database Backups

**Render:**
- Automatic daily backups on paid plans
- Manual backup: Dashboard → Database → Backups

**Local:**
```bash
pg_dump safmc_fmp_tracker > backup.sql
# Restore: psql safmc_fmp_tracker < backup.sql
```

### Update Application

```bash
git pull origin main
# Render will auto-deploy on push to main
```

### Manual Data Refresh

```bash
curl -X POST https://your-app.onrender.com/api/scrape/all
```

### View Scrape Logs

```bash
curl https://your-app.onrender.com/api/logs/scrape
```

## Scaling Considerations

### Free Tier Limitations
- Render free tier spins down after 15 minutes of inactivity
- First request after spin down may be slow (30-60 seconds)
- Database: 1 GB storage, 97 hours/month

### Upgrade to Paid Plan ($7/month)
- No spin down
- Always-on application
- Better performance
- More database storage

### Performance Optimization
1. Enable caching for frequently accessed data
2. Optimize database queries
3. Add indexes to frequently queried columns
4. Consider CDN for static assets

## Security Best Practices

1. **Never commit sensitive data**
   - Keep `.env` in `.gitignore`
   - Use environment variables for all secrets

2. **Use strong SECRET_KEY**
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Keep dependencies updated**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

4. **Monitor logs regularly**
   - Check for suspicious activity
   - Monitor scraping errors

## Support

- **Issues**: Open an issue on GitHub
- **Documentation**: See README.md
- **Render Support**: https://render.com/docs

## Next Steps

After successful deployment:

1. ✅ Verify health endpoint
2. ✅ Trigger initial data scrape
3. ✅ Check dashboard displays data correctly
4. ✅ Set up monitoring/alerts (optional)
5. ✅ Configure custom domain (optional)
6. ✅ Set up automated testing (optional)
