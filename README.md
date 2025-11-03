# SAFMC FMP Tracker

A comprehensive tracking system for South Atlantic Fishery Management Council (SAFMC) Fishery Management Plan amendments, meetings, and public comments.

## Features

### Core Features
- **Action Tracking**: Monitor amendments, frameworks, and regulatory actions across all FMPs
- **Progress Tracking**: Visual progress indicators with stage-based tracking
- **Meeting Management**: Track SAFMC meetings and events
- **Web Scraping**: Automated data collection from SAFMC website
- **Public Comments**: Track and manage public comments on actions
- **REST API**: Full API for data access and integration
- **Modern Dashboard**: Clean, responsive web interface

### Advanced Features (NEW!)
- **AI Query System**: Natural language queries powered by Claude API
  - Ask questions about FMP development in plain English
  - Automated pattern analysis and recommendations
  - Intelligent search across all documents
- **Enhanced Comment Analysis**: Comprehensive public comment tracking
  - Automatic categorization (Commercial, For-Hire, NGO, etc.)
  - Sentiment analysis (Support, Oppose, Mixed)
  - Topic extraction and geographic analysis
  - Real-time analytics and reporting
- **Automated Discovery**: Find new comment sources automatically
- **Analytics Dashboard**: Deep insights into FMP development patterns

📖 See [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) for detailed documentation

## Tech Stack

- **Backend**: Python 3.9+ with Flask
- **Database**: PostgreSQL
- **Scraping**: BeautifulSoup4 + Requests
- **Scheduling**: APScheduler
- **Hosting**: Render
- **Frontend**: HTML/CSS/JavaScript

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/safmc-fmp-tracker.git
   cd safmc-fmp-tracker
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`

### Database Setup

Create a PostgreSQL database:
```bash
createdb safmc_fmp_tracker
```

Update your `.env` file with the database URL:
```
DATABASE_URL=postgresql://user:password@localhost:5432/safmc_fmp_tracker
```

### Initial Data Load

To populate the database with current SAFMC data:
```bash
curl -X POST http://localhost:5000/api/scrape/all
```

## Deployment to Render

### Prerequisites
- GitHub account
- Render account (free tier available)

### Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/safmc-fmp-tracker.git
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" and select "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml` and set up:
     - Web service
     - PostgreSQL database
     - Environment variables

3. **Configure Environment Variables**
   In Render dashboard, add:
   - `FLASK_ENV=production`
   - `SECRET_KEY` (will be auto-generated)
   - `ENABLE_SCHEDULER=true`

4. **Deploy**
   - Render will automatically deploy on every push to main branch
   - First deployment may take 5-10 minutes

## API Endpoints

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-amendments` - Get recent amendments

### Actions
- `GET /api/actions` - Get all actions (with optional filters)
- `GET /api/actions/<action_id>` - Get specific action with details

### Meetings
- `GET /api/meetings` - Get all meetings
- `GET /api/meetings/<meeting_id>` - Get specific meeting

### Comments
- `GET /api/comments` - Get all comments
- `GET /api/comments?action_id=<id>` - Get comments for specific action

### Scraping
- `POST /api/scrape/amendments` - Manually trigger amendments scraping
- `POST /api/scrape/meetings` - Manually trigger meetings scraping
- `POST /api/scrape/all` - Scrape all data

### Logs
- `GET /api/logs/scrape` - Get scraping logs

## Database Schema

### Actions Table
- Tracks amendments, frameworks, and regulatory actions
- Includes progress stages, percentages, and phases
- Links to milestones and comments

### Meetings Table
- Stores SAFMC meetings and events
- Includes dates, locations, and agendas

### Comments Table
- Public comments on fishery management actions
- Tracks response status

### Milestones Table
- Action milestones and dependencies

### Scrape Logs Table
- Tracks scraping operations and results

## Automated Scraping

The system automatically scrapes SAFMC website daily at 2 AM (configurable):

- Amendments under development
- Individual FMP pages
- Meeting schedules

Configure in `.env`:
```
ENABLE_SCHEDULER=true
```

## Development

### Database Migrations

Create a new migration:
```bash
flask db migrate -m "Description of changes"
```

Apply migrations:
```bash
flask db upgrade
```

### Running Tests
```bash
pytest tests/
```

### Code Structure
```
safmc-fmp-tracker/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── migrations/           # Database migrations
├── public/              # Frontend files
│   ├── index.html
│   ├── css/
│   └── js/
└── src/
    ├── models/          # Database models
    ├── routes/          # API and web routes
    ├── scrapers/        # Web scrapers
    └── services/        # Background services
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `FLASK_ENV` | Environment (development/production) | development |
| `SECRET_KEY` | Flask secret key | Required in production |
| `PORT` | Port to run on | 5000 |
| `ENABLE_SCHEDULER` | Enable automated scraping | true |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- Open a GitHub issue
- Contact: [your-email@example.com]

## Acknowledgments

- Data sourced from [SAFMC.net](https://safmc.net)
- Built for improved transparency in fishery management

## Roadmap

- [ ] Add document management and storage
- [ ] Implement email notifications for updates
- [ ] Add data export (CSV, Excel)
- [ ] Create mobile-responsive design improvements
- [ ] Add user authentication and permissions
- [ ] Integrate with SAFMC calendar API
- [ ] Add data visualization and charts
