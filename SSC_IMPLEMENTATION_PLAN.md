# SSC Module Implementation Plan
**SAFMC FMP Tracker - Scientific and Statistical Committee Integration**

## Overview

Comprehensive tracking and analysis of the SAFMC Scientific and Statistical Committee's work, including meetings, members, recommendations, and connections to Council decisions.

---

## Phase 1: Database & Data Collection (Est. 4-6 hours)

### 1.1 Database Setup ✅
**Status:** Schema designed and ready to deploy

**Tables Created:**
- `ssc_members` - 21 committee members with expertise and terms
- `ssc_meetings` - Meeting schedule, locations, and materials
- `ssc_recommendations` - Recommendations to the Council
- `ssc_council_connections` - Links SSC recommendations to Council actions
- `ssc_documents` - Meeting documents (agendas, reports, presentations)
- `ssc_meeting_attendees` - Attendance tracking

**Run migration:**
```bash
python3 migrations/create_ssc_tables.py
```

### 1.2 Initial Data Seeding
**Seed current SSC members:**
- Dr. Marcel Reichert (SC, At-large) - **Chair**
- Dr. Walter Bubley (SC, State-designated) - **Vice-Chair**
- 19 additional members with states, seat types, expertise

**Historical meeting data:**
- Scrape meetings from https://safmc.net/scientific-and-statistical-committee-meeting/
- Import meetings back to ~2020
- Link agenda URLs, briefing books, reports

---

## Phase 2: Backend API (Est. 6-8 hours)

### 2.1 SSC Routes (`src/routes/ssc_routes.py`)

```python
GET  /api/ssc/members          - List all SSC members
GET  /api/ssc/members/:id      - Get member details
GET  /api/ssc/meetings         - List SSC meetings (paginated, filtered)
GET  /api/ssc/meetings/:id     - Get meeting details with recommendations
GET  /api/ssc/recommendations  - List recommendations (filtered by status, species, FMP)
GET  /api/ssc/recommendations/:id - Get recommendation with Council connections
POST /api/ssc/recommendations  - Create new recommendation (admin only)
PUT  /api/ssc/recommendations/:id - Update recommendation (admin only)
GET  /api/ssc/analytics        - SSC analytics and insights
GET  /api/ssc/connections      - Get SSC-Council connection map
```

### 2.2 Data Scraper (`src/scrapers/ssc_scraper.py`)

**Scrapes from safmc.net:**
- SSC meeting dates, locations, types
- Meeting materials (agendas, briefing books, reports)
- Parses meeting reports for recommendations
- Extracts species, FMP references, ABC values

**Run via:**
```bash
python3 src/scrapers/ssc_scraper.py
```

Or automated cron job (weekly):
```cron
0 3 * * 1 cd /path/to/app && python3 src/scrapers/ssc_scraper.py
```

---

## Phase 3: Frontend UI (Est. 8-10 hours)

### 3.1 Navigation
**Add to Sidebar (`client/src/components/Sidebar.jsx`):**
```jsx
{
  name: 'SSC',
  icon: FlaskConical,  // Science/lab icon
  path: '/ssc',
  badge: sscUpcomingCount
}
```

### 3.2 SSC Pages

#### **A. SSC Dashboard** (`client/src/pages/SSC/SSCDashboard.jsx`)
**Route:** `/ssc`

**Sections:**
- Upcoming SSC meetings (next 6 months)
- Recent recommendations status
- SSC-Council connection map visualization
- Top topics being discussed
- Species most frequently addressed

#### **B. SSC Meetings** (`client/src/pages/SSC/SSCMeetings.jsx`)
**Route:** `/ssc/meetings`

**Features:**
- Calendar view of meetings
- Filter: Upcoming / Past / All
- Each meeting card shows:
  - Date, location, meeting type
  - Links to agenda, briefing book, report
  - Topics and species discussed
  - Number of recommendations made
- Click meeting → detailed view with recommendations

#### **C. SSC Members Directory** (`client/src/pages/SSC/SSCMembers.jsx`)
**Route:** `/ssc/members`

**Features:**
- Grid/list view of 21 members
- Filter by:
  - State (NC, FL, SC, GA, etc.)
  - Seat type (At-large, State-designated, Economist, Social Scientist)
  - Expertise area
  - Active/Inactive status
- Member cards show:
  - Name, title, affiliation
  - Seat type and state
  - Expertise area
  - Chair/Vice-Chair badge
  - Contact info (if available)
- Click member → bio, publications, meeting attendance

#### **D. SSC Recommendations** (`client/src/pages/SSC/SSCRecommendations.jsx`)
**Route:** `/ssc/recommendations`

**Features:**
- Table of all SSC recommendations
- Filter by:
  - Status (Pending, Adopted, Rejected, Modified)
  - Species
  - FMP
  - Recommendation type (ABC, Stock Assessment, Management Measure)
  - Date range
- Columns:
  - Recommendation #
  - Title
  - Meeting date
  - Species
  - FMP
  - Status
  - Council response
- Click recommendation → full details + Council connections

#### **E. SSC-Council Connections** (`client/src/pages/SSC/SSCConnections.jsx`)
**Route:** `/ssc/connections`

**Features:**
- Visual flowchart/network diagram showing:
  - SSC Meeting → Recommendations → Council Meetings → Actions
- Filter by:
  - Date range
  - Species
  - FMP
  - Connection strength (High, Medium, Low influence)
- Analytics:
  - % of SSC recommendations adopted by Council
  - Average time from SSC recommendation to Council action
  - Most influential SSC recommendations
  - Topics where SSC guidance is most/least followed

---

## Phase 4: AI Analysis Features (Est. 4-6 hours)

### 4.1 SSC Analytics Dashboard

**Metrics tracked:**
- Meeting frequency and attendance patterns
- Recommendation types and outcomes
- Species most frequently discussed
- FMP coverage analysis
- SSC expertise gaps (areas lacking member specialization)
- Recommendation adoption rate by topic/species

### 4.2 AI-Powered Insights

**Natural language queries via Claude:**
```
"What percentage of SSC ABC recommendations were adopted by the Council in 2024?"
"Show me all SSC recommendations for Red Snapper"
"Which SSC members attended the most meetings?"
"What topics has the SSC addressed most frequently?"
"Compare SSC recommendations vs actual Council actions for Gag Grouper"
```

**Analysis features:**
- Recommendation sentiment analysis (conservative vs aggressive)
- SSC workload trends over time
- Predictive analytics: "Based on SSC recommendation, predict Council action"
- Expertise utilization: "Is the SSC's expertise being fully leveraged?"

### 4.3 Automated Reports

**Weekly SSC Digest:**
- Upcoming SSC meetings
- Recent recommendations
- Council responses to SSC guidance
- Trending topics

---

## Phase 5: Advanced Features (Future)

### 5.1 SSC Recommendation Tracking
- Email notifications when SSC makes new recommendations
- Track status changes (Pending → Adopted)
- Link recommendations to final Council amendments

### 5.2 SSC Workload Analysis
- Visualize SSC meeting density by month/year
- Track recommendation processing times
- Identify bottlenecks in SSC-Council workflow

### 5.3 Public Engagement
- Public comment on SSC recommendations
- Transparency dashboard showing how public input influenced SSC

### 5.4 Integration with SEDAR
- Link SSC recommendations to SEDAR stock assessments
- Track SSC participation in SEDAR reviews
- Visualize SSC's role in stock assessment process

---

## Data Sources

### Primary Source
- **SAFMC SSC Page:** https://safmc.net/scientific-and-statistical-committee-meeting/
- **SSC Members:** https://safmc.net/about/scientific-and-statistical-committee/

### Data to Scrape
1. **Meetings:**
   - Meeting dates, locations
   - Agenda PDFs
   - Briefing book PDFs
   - Final report PDFs
   - Webinar links

2. **Recommendations:**
   - Extracted from meeting reports (PDF parsing required)
   - ABC values
   - Stock assessment reviews
   - Management measure recommendations

3. **Members:**
   - Names, states, seat types
   - Affiliations
   - Expertise areas
   - Terms of service

---

## SSC Member Data (For Initial Seed)

```python
SSC_MEMBERS = [
    {
        "name": "Dr. Marcel Reichert",
        "state": "SC",
        "seat_type": "At-large",
        "is_chair": True,
        "expertise_area": "Marine Biology, Stock Assessment"
    },
    {
        "name": "Dr. Walter Bubley",
        "state": "SC",
        "seat_type": "State-designated",
        "is_vice_chair": True,
        "expertise_area": "Fisheries Science"
    },
    {
        "name": "Dr. Jeff Buckel",
        "state": "NC",
        "seat_type": "At-large",
        "expertise_area": "Fish Ecology"
    },
    # ... 18 more members
]
```

---

## Timeline Estimate

| Phase | Task | Hours |
|-------|------|-------|
| 1 | Database setup & seeding | 4-6 |
| 2 | Backend API & scraper | 6-8 |
| 3 | Frontend UI (5 pages) | 8-10 |
| 4 | AI analysis features | 4-6 |
| **Total** | | **22-30 hours** |

---

## Key Features Summary

✅ **Comprehensive SSC Tracking**
- 21 member directory with expertise
- Meeting schedule and materials
- Recommendations to Council
- Visual SSC-Council connections

✅ **Analytics & Insights**
- Recommendation adoption rates
- SSC workload trends
- Expertise gap analysis
- Council response tracking

✅ **Integration with Existing System**
- Links SSC recommendations → Council meetings → Actions
- Unified species/FMP tracking
- Consistent UI/UX with existing pages

✅ **AI-Powered Analysis**
- Natural language queries about SSC work
- Predictive analytics on Council responses
- Automated insights and reports

---

## Next Steps

1. **Run migration** to create SSC tables
2. **Seed SSC members** with current roster
3. **Build scraper** to import historical meetings
4. **Create SSC routes** in backend
5. **Add SSC nav item** to sidebar
6. **Build SSC dashboard** page
7. **Implement remaining pages** (meetings, members, recommendations, connections)
8. **Add AI analysis features**
9. **Test and deploy**

---

## Questions?

Contact: Aaron Kornbluth (aaron.kornbluth@gmail.com)

**Ready to build!** 🚀
