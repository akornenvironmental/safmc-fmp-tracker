# Stock Assessment Tracking Feature - Implementation Plan

Based on analysis of SEDAR (https://sedarweb.org/) and StockSMART (https://apps-st.fisheries.noaa.gov/stocksmart), here's the comprehensive plan for stock assessment tracking.

---

## 📊 Data Sources Analysis

### SEDAR Website
**Key Capabilities:**
- 106+ numbered assessment projects
- Document repository with search
- Event calendar (workshops, meetings, reviews)
- Project schedules and timelines
- Public comment submissions
- Assessment terms of reference

**Data to Scrape:**
- Assessment project details (SEDAR-1 through SEDAR-106+)
- Project schedules and deadlines
- Workshop/meeting dates → integrate with calendar
- Public comment submissions (Google Sheets)
- Assessment documents and reports
- Species/stock information

### StockSMART
**Key Capabilities:**
- Stock status indicators (B/BMSY, F/FMSY)
- Time series data (catch, abundance, fishing mortality, recruitment)
- Kobe plots (stock condition visualization)
- Assessment counts and history
- Filterable by: Science center, jurisdiction, FMP, ecosystem, species
- Data downloads with custom field selection

**Data to Scrape/API:**
- Stock status (overfished/overfishing indicators)
- Biomass and fishing mortality metrics
- Recruitment data
- Catch statistics
- Assessment history (2005-present)
- MSY, OFL, ABC, ACL values

---

## 🗄️ Database Schema (Already Created)

We already have the tables from the comprehensive migration:

```sql
-- stock_assessments table
CREATE TABLE stock_assessments (
    id SERIAL PRIMARY KEY,
    sedar_number VARCHAR(50),
    species VARCHAR(200) NOT NULL,
    scientific_name VARCHAR(200),
    stock_name VARCHAR(300),
    assessment_type VARCHAR(100),
    status VARCHAR(50),
    start_date DATE,
    completion_date DATE,
    stock_status VARCHAR(100),
    overfishing_occurring BOOLEAN,
    overfished BOOLEAN,
    biomass_current NUMERIC,
    biomass_msy NUMERIC,
    fishing_mortality_current NUMERIC,
    fishing_mortality_msy NUMERIC,
    overfishing_limit NUMERIC,
    acceptable_biological_catch NUMERIC,
    annual_catch_limit NUMERIC,
    keywords TEXT[],
    fmps_affected TEXT[],
    source_url TEXT,
    document_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- assessment_comments table
CREATE TABLE assessment_comments (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES stock_assessments(id) ON DELETE CASCADE,
    commenter_name VARCHAR(200),
    organization VARCHAR(300),
    comment_date DATE,
    comment_type VARCHAR(100),
    comment_text TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎨 Frontend Features

### 1. Stock Assessments Page (`/assessments`)

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Stock Assessments & Status Tracker                  │
│ [Filter by Species ▼] [Filter by Status ▼] [Search]│
├─────────────────────────────────────────────────────┤
│                                                      │
│  📊 Interactive Dashboard                           │
│  ┌──────────────┬──────────────┬─────────────┐    │
│  │ Total Stocks │  Overfished  │ Overfishing │    │
│  │     128      │      12      │     8       │    │
│  └──────────────┴──────────────┴─────────────┘    │
│                                                      │
│  📈 Kobe Plot (Interactive)                         │
│  [B/BMSY vs F/FMSY quadrant chart]                 │
│                                                      │
│  📋 Assessment List (Table)                         │
│  ┌────────────────────────────────────────────┐    │
│  │ Species │ SEDAR # │ Status │ B/BMSY │ Actions│  │
│  │ Red Snapper│ 73 │ ✓ Healthy│ 1.23 │ View  │  │
│  │ Gag Grouper│ 72 │ ⚠ Watch  │ 0.89 │ View  │  │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

**Interactive Charts:**
1. **Kobe Plot** - B/BMSY vs F/FMSY
   - Quadrant colors: Green (healthy), Yellow (caution), Red (overfished/overfishing)
   - Clickable points → stock detail page
   - Filter by FMP, region, year

2. **Time Series Charts** - Per Stock
   - Biomass over time
   - Fishing mortality over time
   - Catch history
   - Recruitment trends

3. **Assessment Timeline** - Gantt-style
   - Shows all active assessments
   - Data workshops, review workshops, final reports
   - Integrated with calendar

4. **Status Summary Dashboard**
   - Pie charts by status category
   - Trend indicators (↑ improving, ↓ declining, → stable)
   - FMP breakdown

### 2. Stock Detail Page (`/assessments/:sedar_number`)

**Sections:**
- **Stock Information** - Species, scientific name, stock definition
- **Current Status** - B/BMSY, F/FMSY, overfished/overfishing indicators
- **Management Benchmarks** - MSY, OFL, ABC, ACL
- **Assessment History** - Previous assessments, timeline
- **Data Visualizations** - Time series charts
- **Documents** - Reports, data files, presentations
- **Public Comments** - From Google Sheets scraper
- **Related Actions** - FMP amendments tied to this stock

### 3. SEDAR Calendar Integration

Add to existing calendar (`/meetings`):
- **SEDAR Events** - Data workshops, review workshops, webinars
- **Comment Periods** - Public comment deadlines
- **Milestones** - Assessment deliverables
- **Filter Options** - Show/hide SEDAR events

---

## 🕷️ Data Collection Strategy

### 1. SEDAR Scraper (`src/scrapers/sedar_scraper.py`)

```python
class SEDARScraper:
    """
    Scrapes SEDAR website for stock assessments and timeline data
    """

    def scrape_assessments(self):
        """
        Scrape all SEDAR assessment projects
        - Main page: https://sedarweb.org/sedar-assessments/
        - Individual pages: https://sedarweb.org/sedar-[number]/
        """
        # For each SEDAR-1 through SEDAR-106+:
        #   - Species/stock name
        #   - Assessment type (standard, benchmark, update, research track)
        #   - Status (planning, in progress, completed)
        #   - Timeline/schedule
        #   - Documents
        #   - Terms of reference

    def scrape_calendar(self):
        """
        Scrape SEDAR event calendar
        - Workshops (data, assessment, review)
        - Webinars
        - Steering committee meetings
        - Comment period deadlines
        """

    def scrape_public_comments(self, google_sheets_urls):
        """
        Scrape Google Sheets public comment forms
        Examples:
        - https://docs.google.com/spreadsheets/d/e/.../pubhtml?gid=2025235464
        - Parse HTML table or use Google Sheets API

        Expected fields:
        - Commenter name
        - Organization
        - Date submitted
        - Comment text
        - SEDAR project number
        """
```

### 2. StockSMART API/Scraper (`src/scrapers/stocksmart_scraper.py`)

```python
class StockSMARTScraper:
    """
    Scrapes or queries StockSMART for stock status data
    """

    def get_stock_status(self, filters=None):
        """
        Get current stock status for all stocks
        - B/BMSY, F/FMSY ratios
        - Overfished/overfishing flags
        - Jurisdiction, FMP, ecosystem
        """

    def get_time_series(self, stock_name):
        """
        Get historical time series data
        - Catch
        - Abundance/biomass
        - Fishing mortality
        - Recruitment
        """

    def get_assessment_history(self, stock_name):
        """
        Get history of assessments for a stock
        - Assessment years
        - Assessment type
        - Key findings
        """
```

### 3. Integration Strategy

**Frequency:**
- Daily: Check for new SEDAR events, comment submissions
- Weekly: Update stock status from StockSMART
- Monthly: Full assessment document sync

**Data Quality:**
- Cross-reference SEDAR numbers between sources
- Validate species names against FishBase/WoRMS
- Flag mismatches for manual review

---

## 🔍 Queryable Data Features

### AI-Powered Queries (Temperature = 0)

**Example Queries:**
```
"What's the status of red snapper?"
→ Returns: Current B/BMSY, F/FMSY, overfished status, latest assessment

"Show me all overfished stocks in the South Atlantic FMP"
→ Returns: Filtered table with status indicators

"When is the next gag grouper assessment?"
→ Returns: SEDAR timeline, workshop dates, expected completion

"What stocks have assessments scheduled in 2025?"
→ Returns: Timeline view with all 2025 assessments

"Show catch trends for dolphin over the last 10 years"
→ Returns: Time series chart from StockSMART data
```

### Database Query Examples

```sql
-- Overfished stocks
SELECT species, stock_name, biomass_current/biomass_msy as b_ratio
FROM stock_assessments
WHERE overfished = TRUE
ORDER BY b_ratio ASC;

-- Stocks with overfishing occurring
SELECT species, fishing_mortality_current/fishing_mortality_msy as f_ratio
FROM stock_assessments
WHERE overfishing_occurring = TRUE;

-- Assessment timeline
SELECT sedar_number, species, status, start_date, completion_date
FROM stock_assessments
WHERE status IN ('In Progress', 'Planning')
ORDER BY start_date;
```

---

## 📦 Implementation Phases

### Phase 1: Database & Backend (Week 1-2)
- ✅ Database schema (already created)
- [ ] Run migration
- [ ] Build stock assessment routes (`src/routes/stock_assessment_routes.py`)
- [ ] Create SEDAR scraper
- [ ] Create StockSMART scraper
- [ ] Test data collection

### Phase 2: Frontend Tables (Week 3)
- [ ] Create `StockAssessments.jsx` page
- [ ] Build assessment table with sorting/filtering
- [ ] Add search functionality
- [ ] Mirror table UI from interview system
- [ ] Add export capabilities (CSV, Excel)

### Phase 3: Visualizations (Week 4)
- [ ] Implement Kobe plot (D3.js or Recharts)
- [ ] Build time series charts
- [ ] Create status dashboard cards
- [ ] Add assessment timeline view (Gantt-style)

### Phase 4: Calendar Integration (Week 5)
- [ ] Add SEDAR events to calendar
- [ ] Add filter for SEDAR vs Council meetings
- [ ] Color-code event types
- [ ] Add comment period reminders

### Phase 5: AI Queries & Polish (Week 6)
- [ ] Update AI service to temperature=0
- [ ] Train on stock assessment data structure
- [ ] Add context about data sources
- [ ] Test query accuracy
- [ ] Add uncertainty disclaimers

---

## 🎯 Key Design Principles

1. **Minimize Hallucinations**
   - AI temperature = 0 for all queries
   - Always cite data sources
   - Flag when data is missing/uncertain
   - Provide confidence scores

2. **Data Transparency**
   - Show last update time
   - Link to original SEDAR/StockSMART sources
   - Indicate data quality/completeness
   - Track scraper success/failure

3. **Visual Clarity**
   - Color-coded status indicators (green/yellow/red)
   - Consistent icons (✓ healthy, ⚠ caution, ❌ overfished)
   - Accessible charts with screen reader support
   - Export all visualizations as data tables

4. **Interoperability**
   - Link stocks to FMP actions
   - Cross-reference with meeting discussions
   - Connect to public comments
   - Show policy implications

---

## 📊 Chart Library Recommendations

**Recommended: Recharts** (https://recharts.org/)
- React-native, composable charts
- Built-in responsive design
- Good accessibility support
- Extensive chart types (line, area, scatter, composed)

**Alternative: D3.js + React**
- More control for custom Kobe plot
- Steeper learning curve
- Better for complex interactions

**Example Kobe Plot Structure:**
```jsx
<ScatterChart data={stockData}>
  <CartesianGrid />
  <XAxis
    dataKey="b_bmsy"
    domain={[0, 2]}
    label={{ value: 'B/BMSY', position: 'bottom' }}
  />
  <YAxis
    dataKey="f_fmsy"
    domain={[0, 2]}
    label={{ value: 'F/FMSY', angle: -90 }}
  />
  <ReferenceLine x={1} stroke="#666" />
  <ReferenceLine y={1} stroke="#666" />
  <Scatter
    name="Stocks"
    data={stockData}
    fill={d => getQuadrantColor(d.b_bmsy, d.f_fmsy)}
  />
  <Tooltip content={<CustomTooltip />} />
</ScatterChart>
```

---

## 🔐 Data Access & Permissions

- **Public View**: All stock status data, charts, assessment info
- **Admin Only**: Scraper controls, data quality review, manual edits
- **API Endpoints**: Public read-only, rate-limited

---

## Next Steps

1. Run the comprehensive migration to create tables
2. Build `/api/assessments` routes
3. Build SEDAR scraper (start with assessment list)
4. Create basic `StockAssessments.jsx` page with table
5. Add Kobe plot visualization
6. Integrate with calendar

**Estimated Timeline: 6 weeks for full implementation**
**MVP (table + basic charts): 2-3 weeks**
