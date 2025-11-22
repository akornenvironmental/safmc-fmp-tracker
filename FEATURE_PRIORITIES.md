# SAFMC FMP Tracker - Feature Priorities

## Current System Status ✅
- 188 Actions tracked
- 57 Meetings recorded
- 297 Comments captured
- Workplan integration ready
- Full auth system with roles
- AI document analysis system

## Top Priority Features (Pick One to Start)

### 1. Species Profile Pages 🐟
**Why:** Central hub for all species-specific information
**Value:** High visibility, easy to build on existing data
**Effort:** Medium (2-3 hours)
**Components:**
- Aggregate all actions affecting each species
- Link to stock assessments when available
- Show management status (FMP, regulations)
- Timeline visualization of management changes
- Economic data if available

**API Endpoints Needed:**
- GET /api/species - List all species mentioned in actions
- GET /api/species/:name - Species profile with all related data
- GET /api/species/:name/timeline - Management history

**Frontend:**
- Species list page with search/filter
- Individual species profile page
- Timeline component for management history

### 2. Compliance Monitoring Dashboard 📊
**Why:** Track ACL utilization and stock status (once SAFE data is working)
**Value:** High - critical for accountability
**Effort:** Medium (depends on SAFE/SEDAR being fixed)
**Components:**
- Real-time ACL utilization tracking
- Overfishing/overfished status dashboard
- Rebuilding plan progress tracking
- Accountability measure triggers
- Predictive alerts

**Status:** Blocked until SAFE/SEDAR is debugged

### 3. Amendment Comparison Tool 📝
**Why:** Council members need to understand alternatives
**Value:** High for decision-making
**Effort:** Medium-High (3-4 hours)
**Components:**
- Side-by-side comparison of action alternatives
- Visual diff of regulatory text
- Impact comparison (biological, economic, social)
- "What changed from last version?" view
- Historical precedent finder

**API Endpoints Needed:**
- GET /api/actions/:id/alternatives - Get all alternatives for an action
- POST /api/actions/compare - Compare multiple actions
- GET /api/actions/similar - Find similar historical actions

**Frontend:**
- Comparison view with side-by-side layout
- Diff highlighting for text changes
- Impact metrics dashboard

### 4. Meeting Intelligence System 🎯
**Why:** Already scraping meetings, add intelligence
**Value:** High - saves staff time
**Effort:** High (4-5 hours)
**Components:**
- Auto-extract action items from transcripts
- Track follow-ups and assignments
- AI summary of each agenda item
- Key decisions tracker
- Voting record analysis
- Meeting material search

**API Endpoints Needed:**
- GET /api/meetings/:id/action-items - Extracted action items
- GET /api/meetings/:id/summary - AI-generated summary
- POST /api/meetings/:id/extract - Trigger AI extraction
- GET /api/meetings/search - Search across all materials

### 5. Stakeholder Comment Analysis 💬
**Why:** Councils receive hundreds of comments
**Value:** Very High - saves hours of reading
**Effort:** High (4-5 hours)
**Components:**
- AI-powered sentiment analysis
- Auto-categorization by topic
- Geographic clustering
- Stakeholder group identification
- Summary reports ("90% of comments oppose Action 2")
- Trend analysis across comment periods

**API Endpoints Needed:**
- POST /api/comments/analyze - Run AI analysis on comments
- GET /api/comments/:id/sentiment - Get sentiment for comment
- GET /api/comments/topics - Get topic breakdown
- GET /api/comments/summary - Generate summary report

### 6. Advanced Search & Discovery 🔍
**Why:** 188 actions + 297 comments = lots of content
**Value:** High - make data accessible
**Effort:** Medium (3 hours)
**Components:**
- Natural language search
- Semantic search across documents
- Related content recommendations
- Search by outcome
- Filters by FMP, species, date, type

**API Endpoints Needed:**
- GET /api/search - Universal search endpoint
- GET /api/search/related/:id - Find related content
- GET /api/search/suggest - Search suggestions

## Quick Wins (Can Do in <1 hour)

### A. Action Status Dashboard
- Show actions by status (pending, approved, implemented)
- Progress bars for each FMP
- Recent activity feed

### B. Species Quick Reference
- Simple list of all species mentioned
- Count of actions per species
- Link to existing action details

### C. Meeting Calendar View
- Calendar visualization of meetings
- Upcoming meetings highlighted
- Quick access to materials

### D. Export Functionality
- Export actions to CSV/Excel
- Export comments for analysis
- Generate PDF reports

## Recommendation: Start with Species Profile Pages

**Why this first?**
1. Uses existing data (no new scraping needed)
2. High visibility feature
3. Foundation for future features
4. Relatively simple to build
5. Immediate value to users

**Implementation Steps:**
1. Create species extraction service (parse species from actions)
2. Build species API endpoints
3. Create species list page frontend
4. Create species profile page frontend
5. Add timeline visualization

**Estimated Time:** 2-3 hours

