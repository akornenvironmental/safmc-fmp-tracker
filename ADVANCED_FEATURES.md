# SAFMC FMP Tracker - Advanced Features

## New Features Added

### 1. AI Query System (Claude API Integration)

The system now includes an AI-powered query service using Claude API for intelligent analysis and responses.

#### Features
- Natural language queries about FMP data
- Pattern analysis of amendment development
- Automated status report generation
- Content search across all FMP documents

#### API Endpoints

**Query AI System**
```bash
POST /api/ai/query
Content-Type: application/json

{
  "question": "What is the current status of Snapper Grouper amendments?"
}
```

**Analyze Patterns**
```bash
POST /api/ai/analyze

# Returns analysis of FMP development patterns, bottlenecks, and recommendations
```

**Generate Status Report**
```bash
POST /api/ai/report

# Returns comprehensive status report of all current SAFMC activities
```

**Search Content**
```bash
POST /api/ai/search
Content-Type: application/json

{
  "search_terms": "size limits dolphin wahoo"
}
```

#### Configuration

Add to your `.env` file:
```env
CLAUDE_API_KEY=your-claude-api-key-here
```

Get your API key from: https://console.anthropic.com/

#### Example Usage

```python
# Query the AI system
response = requests.post('http://localhost:5000/api/ai/query', json={
    'question': 'What amendments are currently in the review phase?'
})

result = response.json()
print(result['answer'])
```

### 2. Enhanced Public Comments System

Comprehensive public comments tracking with automated scraping, analysis, and categorization.

#### Features
- **Automated Scraping**: Scrapes public comments from Google Sheets CSV exports
- **Smart Categorization**: Automatically determines commenter type (Commercial, For-Hire, NGO, etc.)
- **Position Analysis**: Extracts support/oppose positions from comment text
- **Topic Extraction**: Identifies key topics mentioned in comments
- **Geographic Analysis**: Tracks comments by state
- **Duplicate Detection**: Removes duplicate comments intelligently

#### Data Model

Enhanced Comment model includes:
- **Commenter Type**: For-Hire, Commercial, NGO, Government, Academic, Private/Recreational
- **Position**: Strong Support, Support, Neutral, Mixed, Oppose, Strong Oppose
- **Key Topics**: Extracted topics (Size Limits, Bag Limits, Season, Gear, etc.)
- **Geographic Data**: City and State
- **Amendment Phase**: Phase when comment was submitted

#### API Endpoints

**Get Comments**
```bash
GET /api/comments
GET /api/comments?action_id=dw-reg-3
```

**Get Comment Analytics**
```bash
GET /api/comments/analytics
GET /api/comments/analytics?action_id=sg-am-46

# Returns breakdown by:
# - Phase
# - Position (support/oppose)
# - Commenter type
# - State
# - Top topics
```

**Scrape Comments**
```bash
POST /api/scrape/comments

# Scrapes all configured comment sources and saves to database
```

#### Comment Sources

Currently configured sources (editable in `src/scrapers/comments_scraper.py`):
- Dolphin Wahoo Regulatory Amendment 3
- Coral Amendment 11/Shrimp Amendment 12
- Snapper Grouper Amendment 46

#### Example Analytics Response

```json
{
  "total": 152,
  "by_phase": {
    "Public Comment": 85,
    "Scoping": 45,
    "Public Hearing": 22
  },
  "by_position": {
    "Support": 67,
    "Oppose": 45,
    "Neutral": 28,
    "Mixed": 12
  },
  "by_type": {
    "For-Hire": 42,
    "Commercial": 38,
    "Private/Recreational": 52,
    "NGO": 15,
    "Government": 5
  },
  "by_state": {
    "FL": 85,
    "NC": 34,
    "SC": 23,
    "GA": 10
  },
  "top_topics": {
    "Size Limits": 68,
    "Bag Limits": 52,
    "Season": 45,
    "Conservation": 38,
    "Economic": 32
  }
}
```

### 3. Analytics & Reporting

#### Features
- Real-time dashboard statistics
- Comment analytics with breakdowns
- Pattern analysis for amendments
- Automated status reports

#### Accessing Analytics

**Dashboard Stats**
```bash
GET /api/dashboard/stats
```

**Comment Analytics**
```bash
GET /api/comments/analytics
GET /api/comments/analytics?action_id=sg-am-46
```

### 4. Enhanced Scraping System

The scraping system has been expanded to include:
- **Amendments** - From SAFMC website
- **Meetings** - From SAFMC calendar
- **Comments** - From Google Sheets sources

#### Scrape Everything

```bash
POST /api/scrape/all

# Returns:
{
  "success": true,
  "amendments": { ... },
  "meetings": { ... }
}
```

#### Individual Scraping

```bash
POST /api/scrape/amendments
POST /api/scrape/meetings
POST /api/scrape/comments
```

## Advanced Use Cases

### 1. AI-Powered Dashboard

```javascript
// Ask AI for summary
fetch('/api/ai/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'Summarize all amendments in review phase'
  })
})
.then(res => res.json())
.then(data => {
  console.log(data.answer);
});
```

### 2. Comment Sentiment Analysis

```python
import requests

# Get comment analytics for specific amendment
response = requests.get(
    'http://localhost:5000/api/comments/analytics',
    params={'action_id': 'dw-reg-3'}
)

analytics = response.json()

# Calculate support ratio
support = analytics['by_position'].get('Support', 0) + \
          analytics['by_position'].get('Strong Support', 0)
oppose = analytics['by_position'].get('Oppose', 0) + \
         analytics['by_position'].get('Strong Oppose', 0)

support_ratio = support / (support + oppose) if (support + oppose) > 0 else 0
print(f"Support ratio: {support_ratio:.1%}")
```

### 3. Automated Pattern Analysis

```bash
# Analyze patterns in FMP development
curl -X POST http://localhost:5000/api/ai/analyze

# Returns insights like:
# - Average time in each phase
# - Common bottlenecks
# - Recommendations for improvement
```

## Database Schema Updates

### Updated Comment Model

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    comment_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200),
    organization VARCHAR(300),
    email VARCHAR(200),
    city VARCHAR(200),
    state VARCHAR(50),
    action_id VARCHAR(100) REFERENCES actions(action_id),
    comment_date TIMESTAMP,
    comment_type VARCHAR(100),
    commenter_type VARCHAR(100),
    position VARCHAR(100),
    key_topics TEXT,
    comment_text TEXT,
    amendment_phase VARCHAR(100),
    response_status VARCHAR(100),
    response_text TEXT,
    response_date TIMESTAMP,
    source VARCHAR(200),
    source_url VARCHAR(500),
    data_source VARCHAR(300),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Integration Examples

### React/Vue Integration

```javascript
// AIQueryComponent.jsx
import { useState } from 'react';

function AIQueryComponent() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const askAI = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ai/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      const data = await response.json();
      setAnswer(data.answer);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask about FMP development..."
      />
      <button onClick={askAI} disabled={loading}>
        {loading ? 'Thinking...' : 'Ask AI'}
      </button>
      {answer && <div className="answer">{answer}</div>}
    </div>
  );
}
```

### Python Analysis Script

```python
#!/usr/bin/env python3
"""
Analyze SAFMC comment patterns
"""

import requests
import json

API_BASE = 'http://localhost:5000/api'

# Get all amendments
actions_response = requests.get(f'{API_BASE}/actions')
actions = actions_response.json()['actions']

# For each action, get comment analytics
for action in actions:
    action_id = action['id']

    analytics_response = requests.get(
        f'{API_BASE}/comments/analytics',
        params={'action_id': action_id}
    )

    if analytics_response.status_code == 200:
        analytics = analytics_response.json()

        print(f"\n{action['title']}")
        print(f"Total Comments: {analytics['total']}")
        print(f"Support: {analytics['by_position'].get('Support', 0)}")
        print(f"Oppose: {analytics['by_position'].get('Oppose', 0)}")
        print(f"Top Topics: {list(analytics['top_topics'].keys())[:3]}")
```

## Performance Considerations

### AI Query Optimization
- AI queries are cached for frequently asked questions
- Context is limited to most recent/relevant data to reduce tokens
- Fallback responses provided when AI is unavailable

### Comment Scraping
- Scraping runs asynchronously
- Duplicate detection prevents data bloat
- Configurable source list for easy updates

### Database Indexing
```sql
CREATE INDEX idx_comments_action_id ON comments(action_id);
CREATE INDEX idx_comments_position ON comments(position);
CREATE INDEX idx_comments_commenter_type ON comments(commenter_type);
CREATE INDEX idx_comments_state ON comments(state);
```

## Security & Privacy

### Comment Data
- Email addresses are stored for tracking but NOT exposed in public API
- PII is protected according to SAFMC policies
- Comments are scraped from publicly available sources only

### AI System
- Claude API key stored securely in environment variables
- No sensitive data sent to external AI services without sanitization
- All queries logged for audit purposes

## Future Enhancements

Planned features:
- [ ] Automated comment sentiment trending
- [ ] Email notifications for new comments
- [ ] Advanced NLP topic modeling
- [ ] Comment response workflow
- [ ] Multi-language support
- [ ] Export analytics to PDF/Excel
- [ ] Real-time comment monitoring
- [ ] Federal Register integration
- [ ] Automated discovery of new comment sources

## Troubleshooting

### AI Queries Not Working
```bash
# Check if API key is set
echo $CLAUDE_API_KEY

# Test API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'
```

### Comment Scraping Fails
```bash
# Test Google Sheets access
curl "https://docs.google.com/spreadsheets/d/e/2PACX-1vSjyRSAei_lEHn4bmBpCxlkhq_s0RpBdzoUhzM490fgfYTJZbJMuFT6SFF8oeW34JzkkoY6pYOKBjT3/pub?gid=1284034190&single=true&output=csv"

# Check scrape logs
curl http://localhost:5000/api/logs/scrape
```

## Support

For issues or questions about advanced features:
- Check logs: `curl http://localhost:5000/api/logs/scrape`
- Test health: `curl http://localhost:5000/health`
- Review documentation: README.md, DEPLOYMENT.md

## Credits

- **AI Integration**: Anthropic Claude API
- **Comment Analysis**: Natural Language Processing
- **Data Sources**: SAFMC Public Comment Portal
