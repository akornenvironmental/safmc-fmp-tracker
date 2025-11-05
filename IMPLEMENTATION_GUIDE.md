# SAFMC FMP Tracker - Comprehensive Enhancement Implementation Guide

## 📋 Overview

Based on the SAFMC Process Review team meeting transcript, this guide outlines the comprehensive enhancements needed for the FMP Tracker. The implementation is structured in phases for systematic development.

---

## ✅ PHASE 1: COMPLETED - Database Foundation

### What's Been Built

**1. Database Schema (`migrations/add_comprehensive_tracking_features.sql`)**
- ✅ Roll call voting tables (council_members, motions, votes)
- ✅ White papers and scoping items tables
- ✅ Executive orders table
- ✅ Legislative tracking tables (legislation, regulations)
- ✅ Stock assessment tables (stock_assessments, assessment_comments)
- ✅ AP and SSC report tables
- ✅ Document management system tables
- ✅ Cross-reference tables (action_documents, meeting_documents, action_topics, meeting_topics)
- ✅ Audit log table

**2. Python Models (src/models/)**
- ✅ `council_member.py` - CouncilMember, Motion, Vote models
- ✅ `white_paper.py` - WhitePaper, ScopingItem models
- ✅ `executive_order.py` - ExecutiveOrder model
- ✅ `legislation.py` - Legislation, Regulation models
- ✅ `stock_assessment.py` - StockAssessment, AssessmentComment models
- ✅ `reports.py` - APReport, SSCReport models
- ✅ `document.py` - Document, ActionDocument, MeetingDocument, ActionTopic, MeetingTopic, AuditLog models
- ✅ Updated `__init__.py` to import all new models

### Next Step for Phase 1

**Run the database migration:**

```bash
cd /Users/akorn/safmc-fmp-tracker
psql $DATABASE_URL -f migrations/add_comprehensive_tracking_features.sql
```

---

## 🔨 PHASE 2: Backend API Development

### What Needs to Be Built

**1. API Routes (`src/routes/`)**

Create new route files:

#### A. `voting_routes.py`
```python
# Endpoints needed:
# GET /api/council-members - List all council members
# GET /api/council-members/<id> - Get member details + voting history
# GET /api/motions - List all motions (filterable by meeting, FMP, date range)
# GET /api/motions/<id> - Get motion details + all votes
# GET /api/votes - Get votes (filterable by member, motion, result)
# POST /api/motions - Create motion (admin only)
# POST /api/votes - Record votes (admin only)
```

**Key Features:**
- Filter votes by council member to see voting history
- Filter by FMP, topic, date range
- Export voting records to CSV/Excel
- Vote summary statistics

#### B. `white_paper_routes.py`
```python
# Endpoints:
# GET /api/white-papers - List white papers
# GET /api/white-papers/<id> - Get white paper details
# GET /api/scoping - List scoping items
# GET /api/scoping/<id> - Get scoping item details
# POST /api/white-papers - Create white paper (admin)
# POST /api/scoping - Create scoping item (admin)
```

#### C. `executive_order_routes.py`
```python
# Endpoints:
# GET /api/executive-orders - List EOs
# GET /api/executive-orders/<eo_number> - Get EO details
# GET /api/executive-orders/requiring-response - EOs needing council action
# POST /api/executive-orders - Create EO (admin)
# PUT /api/executive-orders/<id>/response - Submit council response
```

#### D. `legislation_routes.py`
```python
# Endpoints:
# GET /api/legislation - List bills (filter by jurisdiction, status, FMP)
# GET /api/legislation/<id> - Get bill details
# GET /api/regulations - List regulations
# GET /api/regulations/<id> - Get regulation details
# POST /api/legislation/scan - Trigger policy scan
# GET /api/legislation/relevant - Get high-relevance items
```

#### E. `stock_assessment_routes.py`
```python
# Endpoints:
# GET /api/assessments - List assessments (filter by species, status, FMP)
# GET /api/assessments/<sedar_number> - Get assessment details + comments
# GET /api/assessments/<id>/comments - Get assessment comments
# POST /api/assessments - Create assessment (admin)
# POST /api/assessments/<id>/comments - Add comment
```

#### F. `report_routes.py`
```python
# Endpoints:
# GET /api/ap-reports - List AP reports (filter by panel, FMP, date)
# GET /api/ap-reports/<id> - Get AP report details
# GET /api/ssc-reports - List SSC reports (filter by species, FMP, date)
# GET /api/ssc-reports/<id> - Get SSC report details
# POST /api/ap-reports - Create AP report (admin)
# POST /api/ssc-reports - Create SSC report (admin)
```

#### G. `document_routes.py`
```python
# Endpoints:
# GET /api/documents - List documents (filter by type, FMP, topic)
# GET /api/documents/<id> - Get document details
# GET /api/documents/search - Full-text search across all documents
# POST /api/documents - Upload document
# GET /api/actions/<id>/documents - Get all documents for an action
# GET /api/meetings/<id>/documents - Get all documents for a meeting
```

#### H. `search_routes.py` (AI-Powered)
```python
# Endpoints:
# POST /api/search/topic - Search meetings/actions by topic (AI-powered)
# POST /api/search/natural-language - Natural language queries
# Examples:
#   "What meetings discussed striped bass in 2024?"
#   "What were the final motions for the shrimp amendment?"
#   "Show me all votes by Chris Moore on red snapper"
```

**2. Update `api_routes.py`**

Register all new route blueprints:

```python
from src.routes import (
    voting_routes,
    white_paper_routes,
    executive_order_routes,
    legislation_routes,
    stock_assessment_routes,
    report_routes,
    document_routes,
    search_routes
)

app.register_blueprint(voting_routes.bp)
app.register_blueprint(white_paper_routes.bp)
app.register_blueprint(executive_order_routes.bp)
app.register_blueprint(legislation_routes.bp)
app.register_blueprint(stock_assessment_routes.bp)
app.register_blueprint(report_routes.bp)
app.register_blueprint(document_routes.bp)
app.register_blueprint(search_routes.bp)
```

---

## 🕷️ PHASE 3: Data Collection - Scrapers

### What Needs to Be Built

**1. SEDAR Stock Assessment Scraper (`src/scrapers/sedar_scraper.py`)**

```python
class SEDARScraper:
    """
    Scrapes SEDAR website for stock assessments
    - Main page: https://sedarweb.org/sedar-assessments/
    - Assessment pages with status, dates, reports, comments
    - Comment periods and public comments
    """
    def scrape_assessments():
        # Scrape assessment list
        # For each assessment, scrape details page
        # Extract: species, type, status, dates, reports, comments

    def scrape_assessment_comments(sedar_number):
        # Scrape comments for specific assessment
```

**2. Executive Order Scraper (`src/scrapers/executive_order_scraper.py`)**

```python
class ExecutiveOrderScraper:
    """
    Scrapes Federal Register for Executive Orders
    - API: https://www.federalregister.gov/api/v1/documents
    - Filter for fisheries-related EOs
    - Check keywords: fishery, NOAA, commerce, marine, ocean
    """
```

**3. Legislative Scraper (`src/scrapers/legislative_scraper.py`)**

```python
class LegislativeScraper:
    """
    Scrapes legislation from multiple sources

    Federal:
    - Congress.gov API for federal bills
    - Keywords: fishery, magnuson, marine, NOAA, aquaculture

    State:
    - North Carolina Legislature API
    - South Carolina Legislature website
    - Georgia Legislature website
    - Florida Legislature website
    """
```

**4. Federal Register Regulations Scraper (`src/scrapers/regulation_scraper.py`)**

```python
class RegulationScraper:
    """
    Scrapes Federal Register for fisheries regulations
    - API: https://www.federalregister.gov/api/v1/documents
    - Filter: agency=noaa, type=rule
    - CFR parts: 50 CFR 600-699 (fisheries)
    """
```

**5. AP Report Scraper (`src/scrapers/ap_report_scraper.py`)**

```python
class APReportScraper:
    """
    Scrapes SAFMC.net for Advisory Panel reports
    - Find AP meeting pages
    - Extract reports, recommendations
    - Link to related council actions
    """
```

**6. SSC Report Scraper (`src/scrapers/ssc_report_scraper.py`)**

```python
class SSCReportScraper:
    """
    Scrapes SAFMC.net for SSC reports
    - SSC meeting pages
    - ABC recommendations
    - Species assessments
    """
```

**7. Enhanced Comments Scraper**

Update existing `comments_scraper.py` to:
- Auto-discover all comment pages on SAFMC.net
- Extract comment metadata (stakeholder type, state, topics)
- Use AI to extract sentiment, key concerns, topics

**8. Meeting Minutes Topic Extractor (`src/scrapers/minutes_analyzer.py`)**

```python
class MinutesAnalyzer:
    """
    Uses AI to extract topics from meeting minutes
    - Parse meeting documents
    - Extract discussed topics with timestamps
    - Link topics to motions and votes
    - Store in meeting_topics table
    """
```

---

## 🎨 PHASE 4: Frontend Components

### What Needs to Be Built

**1. Roll Call Vote Tracking**

Create: `client/src/pages/Votes.jsx`

```jsx
<VotesPage>
  <VoteFilters>
    - Filter by council member
    - Filter by FMP
    - Filter by date range
    - Filter by vote result (passed/failed)
  </VoteFilters>

  <VotesTable>
    - Motion text
    - Vote date
    - Maker/Seconder
    - Vote result
    - Vote breakdown (Yes/No/Abstain)
    - Click to expand full vote details
  </VotesTable>

  <CouncilMemberProfile>
    - Member info
    - Voting history
    - Vote statistics
    - Export voting record
  </CouncilMemberProfile>
</VotesPage>
```

**2. White Papers & Scoping**

Create: `client/src/pages/WhitePapers.jsx`

```jsx
<WhitePapersPage>
  <Tabs>
    - White Papers tab
    - Scoping Items tab
  </Tabs>

  <WhitePapersTable>
    - Title, FMP, Topic
    - Status (Requested → In Progress → Completed)
    - Council Action Taken
    - Link to document
  </WhitePapersTable>

  <ScopingTable>
    - Title, FMP, Type
    - Comment period dates
    - Action initiated? (Yes/No)
    - Status
  </ScopingTable>
</WhitePapersPage>
```

**3. Executive Orders**

Create: `client/src/pages/ExecutiveOrders.jsx`

```jsx
<ExecutiveOrdersPage>
  <EOTable>
    - EO Number
    - Title
    - Issue Date
    - FMPs Affected
    - Response Required?
    - Response Deadline
    - Status
    - Action buttons (View, Submit Response)
  </EOTable>

  <EODetailModal>
    - Full summary
    - Council response form
    - Timeline of actions
  </EODetailModal>
</ExecutiveOrdersPage>
```

**4. Legislative & Regulatory Tracking**

Create: `client/src/pages/Policy.jsx`

```jsx
<PolicyPage>
  <Tabs>
    - Legislation tab
    - Regulations tab
  </Tabs>

  <PolicyFilters>
    - Jurisdiction (Federal, NC, SC, GA, FL)
    - Status
    - FMP
    - Relevance score
    - Council action required
  </PolicyFilters>

  <LegislationTable>
    - Bill number
    - Title
    - Sponsor
    - Status
    - Relevance score
    - Council commented?
    - Link to bill text
  </LegislationTable>

  <RegulationTable>
    - Regulation number
    - CFR citation
    - Title
    - Agency
    - Comment period
    - Status
  </RegulationTable>
</PolicyPage>
```

**5. Stock Assessments**

Create: `client/src/pages/Assessments.jsx`

```jsx
<AssessmentsPage>
  <AssessmentFilters>
    - Species
    - Status
    - FMP
    - Assessment type
  </AssessmentFilters>

  <AssessmentsTable>
    - SEDAR Number
    - Species
    - Status
    - Stock Status (Overfished, etc.)
    - ABC/ACL/OFL values
    - Completion date
    - Links to reports
  </AssessmentsTable>

  <AssessmentDetail>
    - Full assessment info
    - Timeline
    - Comments section
    - Related SSC reports
    - Related council actions
  </AssessmentDetail>
</AssessmentsPage>
```

**6. AP & SSC Reports**

Create: `client/src/pages/Reports.jsx`

```jsx
<ReportsPage>
  <Tabs>
    - AP Reports tab
    - SSC Reports tab
  </Tabs>

  <APReportsTable>
    - Report title
    - Advisory Panel
    - FMP
    - Meeting date
    - Recommendations
    - Council action taken
    - Link to document
  </APReportsTable>

  <SSCReportsTable>
    - Report title
    - Species
    - ABC Recommendation
    - Rationale
    - Related assessment
    - Council action
  </SSCReportsTable>
</ReportsPage>
```

**7. Document Library**

Create: `client/src/pages/Documents.jsx`

```jsx
<DocumentsPage>
  <DocumentSearch>
    - Full-text search
    - Filter by type
    - Filter by FMP
    - Filter by date
    - Filter by topics
  </DocumentSearch>

  <DocumentsGrid>
    - Document cards with thumbnails
    - Title, type, date
    - Topics/tags
    - Quick actions (View, Download)
  </DocumentsGrid>

  <DocumentDetail>
    - Full metadata
    - Related items (actions, meetings, assessments)
    - Preview (if possible)
  </DocumentDetail>
</DocumentsPage>
```

**8. AI-Powered Search**

Update: `client/src/components/AIAssistant.jsx`

```jsx
<AIAssistant>
  <NaturalLanguageSearch>
    - "What meetings discussed striped bass?"
    - "Show votes by Chris Moore on red snapper"
    - "What were final motions for shrimp amendment?"
  </NaturalLanguageSearch>

  <SearchResults>
    - Meetings with topic
    - Actions related to query
    - Documents matching query
    - Votes matching criteria
    - Link to full records
  </SearchResults>
</AIAssistant>
```

**9. Enhanced Actions Page**

Update: `client/src/pages/ActionsEnhanced.jsx`

Add:
- Related Documents section
- Roll Call Votes section
- AP/SSC Reports section
- Stock Assessment link
- White Papers link
- Timeline view

**10. Enhanced Meetings Page**

Update: `client/src/pages/MeetingsEnhanced.jsx`

Add:
- Topics Discussed section
- Motions & Votes section
- Meeting Documents section
- AP members present
- SSC members present

**11. Enhanced Dashboard**

Update: `client/src/pages/Dashboard.jsx`

Add:
- Upcoming EO response deadlines
- Open comment periods (amendments + assessments)
- Recent votes
- Pending legislative items
- Assessment status summary
- Quick search bar (AI-powered)

---

## 🤖 PHASE 5: AI Integration

### What Needs to Be Built

**1. Topic Extraction Service (`src/services/ai_topic_extractor.py`)**

```python
class TopicExtractor:
    """
    Uses Claude API to extract topics from documents
    - Meeting minutes → topics + discussion duration
    - Actions → relevant topics + relevance scores
    - Comments → key concerns + sentiment
    """
```

**2. Natural Language Search (`src/services/ai_search.py`)**

```python
class AISearch:
    """
    Natural language query processing
    - Parse user intent
    - Query appropriate tables
    - Return formatted results

    Examples:
    - "meetings about striped bass" → search meeting_topics
    - "Chris Moore votes on red snapper" → filter votes by member + topic
    - "final motions for shrimp amendment" → search motions by action_id
    """
```

**3. Document Summarization (`src/services/ai_summarizer.py`)**

```python
class DocumentSummarizer:
    """
    Generate summaries of long documents
    - Assessment reports → executive summaries
    - Meeting minutes → key decisions summary
    - White papers → key findings
    """
```

**4. Comment Analysis (`src/services/ai_comment_analyzer.py`)**

```python
class CommentAnalyzer:
    """
    Analyze public comments
    - Extract sentiment (-1.0 to 1.0)
    - Extract key concerns
    - Extract stakeholder type
    - Group similar comments
    """
```

---

## 📊 PHASE 6: Data Population

### Initial Data Tasks

**1. Seed Council Members**
- Create script to populate current and past council members
- Source: SAFMC website council member list

**2. Import Historical Votes**
- Parse meeting minutes for roll call votes
- Extract motion text, votes
- Populate motions and votes tables

**3. Backfill White Papers**
- Review council meeting materials
- Identify white papers that didn't become amendments
- Add to database

**4. Import Historical Assessments**
- Scrape all completed SEDAR assessments
- Populate stock_assessments table
- Link to SSC reports where available

**5. Populate AP/SSC Reports**
- Scrape historical AP meeting reports
- Scrape historical SSC reports
- Extract ABC recommendations

---

## 🚀 Deployment Checklist

### Before Deploying

- [ ] Run database migrations on production
- [ ] Test all new API endpoints
- [ ] Test scrapers don't overload source websites
- [ ] Configure rate limiting for external APIs
- [ ] Set up cron jobs for automated scraping
- [ ] Test AI search functionality
- [ ] Verify document upload/storage works
- [ ] Test export functionality (CSV/Excel)
- [ ] Performance test with large datasets
- [ ] Set up error logging for new features
- [ ] Update documentation

### Monitoring

- Set up alerts for:
  - Scraper failures
  - API rate limit errors
  - Database errors
  - AI service failures
  - Long query times

---

## 🎯 Priority Implementation Order

Based on team meeting pain points:

### High Priority (Weeks 1-2)
1. ✅ Database schema & models (DONE)
2. Topic-based search API + frontend
3. Roll call vote tracking
4. Document management system
5. Fix meeting sync issues

### Medium Priority (Weeks 3-4)
6. SEDAR stock assessment integration
7. AP/SSC report repository
8. White paper & scoping tracker
9. Enhanced comments with AI analysis

### Lower Priority (Weeks 5-6)
10. Executive Order tracker
11. Legislative & regulatory tracking
12. Full AI natural language search

---

## 📝 Testing Plan

### Unit Tests Needed

For each model, test:
- CRUD operations
- Relationships
- Data validation
- to_dict() methods

### Integration Tests Needed

- API endpoints return correct data
- Filtering works correctly
- Search functionality
- Export functionality
- Cross-references work

### Scraper Tests

- Don't overload source websites
- Handle errors gracefully
- Parse data correctly
- Update vs insert logic works

---

## 💡 Future Enhancements

### Phase 7+ (Future)

**Real-time Notifications:**
- Email alerts for EO response deadlines
- Alerts for new comment periods
- Alerts for upcoming assessments

**Advanced Analytics:**
- Voting patterns analysis
- Comment sentiment trends over time
- Amendment success rate by FMP
- Timeline visualizations

**Mobile App:**
- React Native version for iOS/Android
- Push notifications
- Offline access to documents

**Public API:**
- REST API for external developers
- API keys and rate limiting
- Public data only

---

## 📚 Resources & References

### External APIs

- **Congress.gov API**: https://api.congress.gov/
- **Federal Register API**: https://www.federalregister.gov/developers/api/v1
- **SEDAR**: https://sedarweb.org/
- **State Legislature APIs**: Varies by state

### Libraries Needed

Add to `requirements.txt`:

```python
# Already have
beautifulsoup4==4.12.2
lxml==5.1.0
requests==2.31.0
feedparser==6.0.11

# Need to add
pdfplumber==0.10.3  # For PDF text extraction
python-docx==1.1.0  # For DOCX parsing
anthropic==0.18.1   # Claude API (if not already)
celery==5.3.4       # For background tasks
redis==5.0.1        # For Celery broker
```

---

## 🎓 Training Materials Needed

### For Team

1. User guide for new features
2. Video walkthrough of each section
3. Admin guide for data entry
4. Troubleshooting guide

### For Stakeholders

1. Public-facing user guide
2. FAQ document
3. Tutorial videos
4. Quick reference cards

---

## 📞 Support & Maintenance

### Ongoing Tasks

- Weekly scraper monitoring
- Monthly data quality checks
- Quarterly feature reviews
- Annual security audits
- Regular backups

---

## 🏁 Summary

This implementation adds:
- **10 new database tables** with comprehensive relationships
- **8 new API route files** with 50+ endpoints
- **8 new scraper classes** for automated data collection
- **10 new frontend pages/components** with advanced features
- **4 AI services** for intelligent search and analysis

Total estimated implementation time: **4-6 weeks** for full deployment.

**Next Immediate Steps:**
1. Run database migration
2. Build API routes (start with voting_routes.py)
3. Build one scraper (suggest SEDAR first)
4. Build one frontend page (suggest Votes.jsx)
5. Test end-to-end workflow
6. Repeat for other features

---

**Created:** January 5, 2025
**Last Updated:** January 5, 2025
**Status:** Ready for Phase 2 implementation
