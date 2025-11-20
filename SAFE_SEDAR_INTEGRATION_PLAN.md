# SAFE Reports & SEDAR Integration Plan

## Overview

Comprehensive plan to integrate Stock Assessment and Fishery Evaluation (SAFE) reports and SEDAR stock assessments into the SAFMC FMP Tracker system.

**Data Sources**:
- SAFE Reports: https://safmc.net/documents/13a_south-atlantic-stock-assessment-and-fishery-evaluation-reports/
- SEDAR Assessments: https://safmc.net/science-sedar/ and sedarweb.org
- Individual report formats: HTML, PDF, RPubs

**Goal**: Provide comprehensive tracking of stock status, catch limits, assessment recommendations, and their connection to FMP amendments and management actions.

---

## 1. Database Schema Design

### 1.1 New Tables

#### `safe_reports`
Tracks SAFE report versions and metadata.

```sql
CREATE TABLE IF NOT EXISTS safe_reports (
    id SERIAL PRIMARY KEY,
    fmp VARCHAR(100) NOT NULL,  -- 'Dolphin Wahoo', 'Shrimp', 'Snapper Grouper'
    report_year INTEGER NOT NULL,
    report_date DATE,
    version VARCHAR(50),
    source_url VARCHAR(500),
    source_format VARCHAR(50),  -- 'html', 'pdf', 'rpubs'
    html_content TEXT,
    pdf_file_path VARCHAR(500),

    -- Metadata
    last_scraped TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    is_current BOOLEAN DEFAULT TRUE,

    UNIQUE(fmp, report_year, version)
);
```

#### `safe_report_stocks`
Individual stock/species data from SAFE reports.

```sql
CREATE TABLE IF NOT EXISTS safe_report_stocks (
    id SERIAL PRIMARY KEY,
    safe_report_id INTEGER REFERENCES safe_reports(id) ON DELETE CASCADE,

    -- Species identification
    species_name VARCHAR(200) NOT NULL,
    common_name VARCHAR(200),
    scientific_name VARCHAR(200),
    stock_id VARCHAR(100),

    -- Stock status
    stock_status VARCHAR(50),  -- 'Not Overfished', 'Overfished', 'Unknown'
    overfishing_status VARCHAR(50),  -- 'No Overfishing', 'Overfishing Occurring', 'Unknown'

    -- Catch limits (in pounds unless specified)
    acl DECIMAL(15,2),  -- Annual Catch Limit
    abc DECIMAL(15,2),  -- Acceptable Biological Catch
    ofl DECIMAL(15,2),  -- Overfishing Limit
    msy DECIMAL(15,2),  -- Maximum Sustainable Yield

    -- Actual landings
    commercial_landings DECIMAL(15,2),
    recreational_landings DECIMAL(15,2),
    total_landings DECIMAL(15,2),
    discards DECIMAL(15,2),

    -- Compliance
    acl_utilization DECIMAL(5,2),  -- Percentage
    acl_exceeded BOOLEAN,

    -- Assessment info
    last_assessment_year INTEGER,
    assessment_type VARCHAR(100),  -- 'SEDAR', 'Data-limited', 'Index-based'

    -- Economic data
    ex_vessel_value DECIMAL(15,2),  -- Commercial value

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_safe_stocks_species ON safe_report_stocks(species_name);
CREATE INDEX idx_safe_stocks_report ON safe_report_stocks(safe_report_id);
```

#### `sedar_assessments`
SEDAR stock assessment tracking.

```sql
CREATE TABLE IF NOT EXISTS sedar_assessments (
    id SERIAL PRIMARY KEY,

    -- SEDAR identification
    sedar_number VARCHAR(50) NOT NULL UNIQUE,  -- 'SEDAR 80', 'SEDAR 81'
    full_title TEXT,

    -- Species
    species_name VARCHAR(200),
    common_name VARCHAR(200),
    scientific_name VARCHAR(200),
    fmp VARCHAR(100),  -- Associated FMP

    -- Status
    assessment_status VARCHAR(50),  -- 'Completed', 'In Progress', 'Scheduled', 'Cancelled'
    assessment_type VARCHAR(100),  -- 'Standard', 'Update', 'Benchmark', 'Operational'

    -- Dates
    kickoff_date DATE,
    completion_date DATE,
    expected_completion DATE,
    council_review_date DATE,

    -- URLs
    sedar_url VARCHAR(500),
    final_report_url VARCHAR(500),

    -- Key findings (extracted via AI or manual)
    stock_status VARCHAR(50),
    overfishing_status VARCHAR(50),
    abc_recommendation DECIMAL(15,2),
    rebuilding_required BOOLEAN,
    rebuilding_timeline VARCHAR(100),

    -- Extracted text content
    executive_summary TEXT,
    key_recommendations TEXT,
    management_implications TEXT,

    -- Metadata
    last_scraped TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sedar_species ON sedar_assessments(species_name);
CREATE INDEX idx_sedar_status ON sedar_assessments(assessment_status);
```

#### `assessment_action_links`
Links assessments to management actions/amendments.

```sql
CREATE TABLE IF NOT EXISTS assessment_action_links (
    id SERIAL PRIMARY KEY,
    sedar_assessment_id INTEGER REFERENCES sedar_assessments(id),
    action_id VARCHAR(100) REFERENCES actions(action_id),

    link_type VARCHAR(50),  -- 'basis_for_action', 'referenced_in', 'implements_recommendation'
    notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),

    UNIQUE(sedar_assessment_id, action_id, link_type)
);
```

#### `safe_report_sections`
Stores extracted sections from SAFE reports for search/analysis.

```sql
CREATE TABLE IF NOT EXISTS safe_report_sections (
    id SERIAL PRIMARY KEY,
    safe_report_id INTEGER REFERENCES safe_reports(id) ON DELETE CASCADE,

    section_type VARCHAR(100),  -- 'stock_status', 'economics', 'social', 'ecosystem', 'methodology'
    section_title TEXT,
    section_number VARCHAR(50),
    content TEXT,

    -- AI analysis
    summary TEXT,
    key_points JSONB,
    entities_mentioned JSONB,  -- Species, locations, regulations mentioned

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_safe_sections_report ON safe_report_sections(safe_report_id);
CREATE INDEX idx_safe_sections_type ON safe_report_sections(section_type);
```

### 1.2 Link to Existing Tables

#### Enhance `stock_assessments` table
```sql
-- Add SEDAR reference
ALTER TABLE stock_assessments ADD COLUMN IF NOT EXISTS sedar_assessment_id INTEGER REFERENCES sedar_assessments(id);
ALTER TABLE stock_assessments ADD COLUMN IF NOT EXISTS safe_report_id INTEGER REFERENCES safe_reports(id);

CREATE INDEX idx_stock_assessments_sedar ON stock_assessments(sedar_assessment_id);
CREATE INDEX idx_stock_assessments_safe ON stock_assessments(safe_report_id);
```

#### Enhance `actions` table
```sql
-- Add assessment references
ALTER TABLE actions ADD COLUMN IF NOT EXISTS based_on_assessment_id INTEGER REFERENCES sedar_assessments(id);
ALTER TABLE actions ADD COLUMN IF NOT EXISTS safe_report_reference VARCHAR(100);

CREATE INDEX idx_actions_assessment ON actions(based_on_assessment_id);
```

---

## 2. Scraping Architecture

### 2.1 SAFE Reports Scraper

**Component**: `src/scrapers/safe_report_scraper.py`

**Approach**:
1. **Discovery Phase**: Scrape SAFE reports landing page to find all available reports
2. **Download Phase**: Download HTML/PDF versions of each report
3. **Extraction Phase**: Extract structured data from reports
4. **AI Analysis Phase**: Use Claude to extract key data points and summaries

**Key Functions**:
```python
class SAFEReportScraper:
    def discover_reports(self) -> List[Dict]:
        """Scrape landing page to find all SAFE report links"""

    def download_report(self, url: str, format: str) -> str:
        """Download HTML or PDF report"""

    def parse_html_report(self, html_content: str) -> Dict:
        """Extract sections, tables, and text from HTML report"""

    def parse_pdf_report(self, pdf_path: str) -> Dict:
        """Extract text and tables from PDF using PyPDF2/pdfplumber"""

    def extract_stock_data(self, report_content: Dict) -> List[Dict]:
        """Use AI to extract stock-specific data (ACLs, landings, status)"""

    def extract_economic_data(self, report_content: Dict) -> Dict:
        """Extract economic and social data sections"""
```

**Data Extraction Strategy**:
- **Tables**: Use pandas/BeautifulSoup for HTML tables, pdfplumber for PDF tables
- **Text sections**: Split by headings, store in `safe_report_sections`
- **Stock data**: Use Claude API with structured prompts to extract ACL, ABC, landings
- **Economic data**: Extract ex-vessel values, employment figures, economic impacts

### 2.2 SEDAR Assessments Scraper

**Component**: `src/scrapers/sedar_scraper.py`

**Approach**:
1. **Scrape SAFMC SEDAR page**: Get high-level SEDAR references
2. **Scrape sedarweb.org**: Get detailed SEDAR assessment listings
3. **Download assessment reports**: Get final reports, executive summaries
4. **AI extraction**: Extract stock status, recommendations, rebuilding plans

**Key Functions**:
```python
class SEDARScraper:
    def scrape_sedar_listings(self) -> List[Dict]:
        """Scrape sedarweb.org for all SEDAR assessments"""

    def scrape_assessment_details(self, sedar_number: str) -> Dict:
        """Get detailed info for specific SEDAR (dates, species, status)"""

    def download_final_report(self, sedar_number: str) -> str:
        """Download final assessment report PDF"""

    def extract_executive_summary(self, report_path: str) -> str:
        """Extract executive summary from PDF"""

    def extract_recommendations(self, report_text: str) -> List[str]:
        """Use AI to extract management recommendations"""

    def extract_stock_status(self, report_text: str) -> Dict:
        """Extract stock status determination (overfished, overfishing)"""
```

**SEDAR Data Extraction**:
- **Metadata**: SEDAR number, species, dates from sedarweb.org listings
- **Status**: Completed, In Progress, Scheduled
- **Key findings**: Use Claude to extract ABC recommendations, stock status, rebuilding needs
- **Full text**: Store executive summaries for search

### 2.3 Entity Linking

**Component**: `src/services/assessment_linking_service.py`

**Approach**:
- Fuzzy match species names between SAFE reports, SEDAR assessments, and stock_assessments table
- Link SEDAR assessments to actions/amendments that reference them
- Track which SAFE report years are current vs. historical

**Key Functions**:
```python
class AssessmentLinkingService:
    def link_safe_to_stocks(self, safe_report_id: int):
        """Link SAFE report species to stock_assessments table"""

    def link_sedar_to_actions(self, sedar_id: int):
        """Find actions that reference this SEDAR assessment"""

    def find_assessment_for_action(self, action_id: str) -> Optional[int]:
        """Determine which assessment an action is based on"""

    def update_stock_assessment_links(self):
        """Update all stock_assessments records with SEDAR/SAFE links"""
```

---

## 3. API Routes

### 3.1 SAFE Reports API

**File**: `src/routes/safe_report_routes.py`

```python
@bp.route('/api/safe-reports', methods=['GET'])
def get_safe_reports():
    """Get all SAFE reports with filters"""
    # Query params: fmp, year, current_only

@bp.route('/api/safe-reports/<int:report_id>', methods=['GET'])
def get_safe_report(report_id):
    """Get specific SAFE report with all stock data"""

@bp.route('/api/safe-reports/<int:report_id>/stocks', methods=['GET'])
def get_safe_report_stocks(report_id):
    """Get stock data from specific SAFE report"""

@bp.route('/api/safe-reports/stocks/<species_name>', methods=['GET'])
def get_stock_history(species_name):
    """Get historical SAFE data for a species across multiple years"""

@bp.route('/api/safe-reports/acl-compliance', methods=['GET'])
def get_acl_compliance():
    """Get ACL compliance summary across all stocks"""

@bp.route('/api/safe-reports/scrape', methods=['POST'])
def trigger_safe_scrape():
    """Trigger SAFE reports scraping (admin only)"""
```

### 3.2 SEDAR Assessments API

**File**: `src/routes/sedar_routes.py`

```python
@bp.route('/api/sedar', methods=['GET'])
def get_sedar_assessments():
    """Get all SEDAR assessments with filters"""
    # Query params: status, species, year

@bp.route('/api/sedar/<sedar_number>', methods=['GET'])
def get_sedar_assessment(sedar_number):
    """Get specific SEDAR assessment details"""

@bp.route('/api/sedar/<sedar_number>/actions', methods=['GET'])
def get_sedar_linked_actions(sedar_number):
    """Get actions that reference this SEDAR"""

@bp.route('/api/sedar/species/<species_name>', methods=['GET'])
def get_species_assessments(species_name):
    """Get all SEDAR assessments for a species"""

@bp.route('/api/sedar/scrape', methods=['POST'])
def trigger_sedar_scrape():
    """Trigger SEDAR assessments scraping (admin only)"""

@bp.route('/api/sedar/<int:sedar_id>/link-action', methods=['POST'])
def link_sedar_to_action(sedar_id):
    """Manually link SEDAR to an action"""
    # Body: { action_id, link_type, notes }
```

### 3.3 Combined Stock Status API

**File**: `src/routes/stock_status_routes.py`

```python
@bp.route('/api/stock-status', methods=['GET'])
def get_stock_status_dashboard():
    """Get comprehensive stock status across all sources"""
    # Combines: stock_assessments + SAFE reports + SEDAR

@bp.route('/api/stock-status/<species_name>', methods=['GET'])
def get_species_status_timeline(species_name):
    """Get timeline of stock status changes for a species"""
    # Includes: SEDAR assessments, SAFE reports, actions taken

@bp.route('/api/stock-status/acl-tracking', methods=['GET'])
def get_acl_tracking():
    """Track ACL vs. actual landings over time"""
```

---

## 4. AI Analysis Integration

### 4.1 SAFE Report Analysis Prompts

**Extract Stock Data**:
```python
SAFE_STOCK_EXTRACTION_PROMPT = """
Analyze this SAFE report section and extract stock data.

Section Content:
{section_content}

Extract the following for EACH species mentioned:
1. Species name (common and scientific)
2. Stock status (Overfished/Not Overfished/Unknown)
3. Overfishing status (Occurring/Not Occurring/Unknown)
4. ACL (Annual Catch Limit) in pounds
5. ABC (Acceptable Biological Catch) in pounds
6. Total landings (commercial + recreational) in pounds
7. ACL utilization percentage
8. Ex-vessel value (commercial value)

Return as structured JSON.
"""
```

**Extract Economic Data**:
```python
SAFE_ECONOMIC_EXTRACTION_PROMPT = """
Analyze this SAFE report economic section.

Content:
{section_content}

Extract:
1. Total fishery value (ex-vessel)
2. Number of commercial vessels
3. Number of dealers
4. Employment figures
5. Economic impacts described
6. Social/community impacts
7. Key economic trends

Return as structured JSON.
"""
```

### 4.2 SEDAR Report Analysis Prompts

**Extract Recommendations**:
```python
SEDAR_RECOMMENDATION_PROMPT = """
Analyze this SEDAR assessment executive summary.

Summary:
{executive_summary}

Extract:
1. Recommended ABC (Acceptable Biological Catch)
2. Stock status determination (Overfished? Yes/No/Unknown)
3. Overfishing status (Occurring? Yes/No/Unknown)
4. Is rebuilding required? Yes/No
5. If rebuilding required, what is the timeline?
6. List all management recommendations
7. Key uncertainties or data gaps mentioned

Return as structured JSON.
"""
```

---

## 5. Frontend UI Components

### 5.1 SAFE Reports Dashboard

**Component**: `client/src/pages/SAFEReports.jsx`

**Features**:
- Filter by FMP (Dolphin Wahoo, Shrimp, Snapper Grouper)
- View current vs. historical reports
- ACL compliance summary chart
- Stock-by-stock status grid
- Downloadable reports (HTML/PDF)

**UI Sections**:
1. **Report Selector**: Dropdown for FMP and year
2. **Compliance Dashboard**:
   - Total stocks tracked
   - Stocks exceeding ACL
   - Stocks under ACL
   - Overfished stocks count
3. **Stock Table**: All species with ACL, landings, utilization, status
4. **Economic Summary**: Total fishery value, trends
5. **Report Sections**: Browseable sections with AI summaries

### 5.2 SEDAR Assessments Page

**Component**: `client/src/pages/SEDARAssessments.jsx`

**Features**:
- Timeline view of assessments (completed, ongoing, scheduled)
- Filter by species, status, year
- Link to actions that use each assessment
- View executive summaries
- Track ABC adoption in management

**UI Sections**:
1. **Assessment Timeline**: Visual timeline of SEDAR assessments
2. **Status Grid**:
   - Completed assessments
   - In progress assessments
   - Scheduled assessments
3. **Assessment Detail View**:
   - SEDAR number, species, dates
   - Stock status findings
   - ABC recommendations
   - Linked actions/amendments
   - Executive summary
4. **Search**: Search across assessment text

### 5.3 Stock Status Dashboard

**Component**: `client/src/pages/StockStatus.jsx`

**Features**:
- Comprehensive view combining SAFE + SEDAR + stock_assessments
- Species-by-species detailed view
- ACL tracking charts over time
- Stock status changes timeline
- Management action effectiveness

**UI Sections**:
1. **Overview Cards**:
   - Total stocks tracked
   - Overfished stocks
   - Stocks with overfishing
   - Recent assessments
2. **Species Grid**: All species with current status
3. **ACL Compliance Chart**: Line chart showing ACL vs. landings over years
4. **Species Detail View**:
   - Status history timeline
   - All SEDAR assessments
   - SAFE report data by year
   - Actions taken for this species
   - Current regulations

### 5.4 Enhanced Existing Pages

**Actions Page** (`ActionsEnhanced.jsx`):
- Add "Based on Assessment" badge showing SEDAR number
- Link to assessment details
- Show ABC recommendations that action implements

**Stock Assessments Page** (existing):
- Link to SEDAR assessments
- Link to SAFE reports
- Show historical status from SAFE data

---

## 6. Implementation Phases

### Phase 1: Database & Models (Week 1)
- [ ] Create database migration for all new tables
- [ ] Create SQLAlchemy models for SAFE reports, SEDAR assessments
- [ ] Create linking models
- [ ] Test database schema

### Phase 2: SAFE Reports Scraper (Week 1-2)
- [ ] Build SAFE landing page scraper
- [ ] Implement HTML report parser
- [ ] Implement PDF report parser (pdfplumber)
- [ ] Build AI extraction service for stock data
- [ ] Build AI extraction service for economic data
- [ ] Create SAFE report import script
- [ ] Test with all three FMPs

### Phase 3: SEDAR Scraper (Week 2)
- [ ] Build sedarweb.org scraper
- [ ] Build assessment detail scraper
- [ ] Implement PDF download and text extraction
- [ ] Build AI extraction for recommendations
- [ ] Create SEDAR import script
- [ ] Test with sample assessments

### Phase 4: Entity Linking (Week 2)
- [ ] Build species name fuzzy matching
- [ ] Link SAFE stocks to stock_assessments table
- [ ] Link SEDAR to actions (automatic detection)
- [ ] Manual linking UI for corrections
- [ ] Test linking accuracy

### Phase 5: API Routes (Week 3)
- [ ] Implement SAFE reports API
- [ ] Implement SEDAR API
- [ ] Implement stock status combined API
- [ ] Test all endpoints
- [ ] Add authentication/authorization

### Phase 6: Frontend UI (Week 3-4)
- [ ] Build SAFE Reports dashboard
- [ ] Build SEDAR Assessments page
- [ ] Build Stock Status dashboard
- [ ] Enhance Actions page with assessment links
- [ ] Add search functionality
- [ ] Testing and refinement

---

## 7. Technical Dependencies

### Python Libraries
```python
# Add to requirements.txt
pdfplumber==0.10.3      # PDF table extraction
beautifulsoup4==4.12.2  # Already installed
anthropic==0.18.1       # Already installed (Claude API)
```

### Data Processing
- **HTML parsing**: BeautifulSoup (existing)
- **PDF text extraction**: PyPDF2 (existing) + pdfplumber (new)
- **Table extraction**: pandas (existing) + pdfplumber
- **AI analysis**: Claude API (existing)
- **Fuzzy matching**: rapidfuzz (existing)

---

## 8. Data Quality & Validation

### Validation Rules
1. **ACL values**: Must be positive numbers, typically 100K-10M+ pounds
2. **Stock status**: Must be one of valid statuses
3. **Species names**: Must match existing species in database or be new
4. **Dates**: SEDAR completion dates must be logical (kickoff < completion)
5. **Utilization**: ACL utilization must be calculated correctly (landings/ACL * 100)

### Quality Checks
- Flag when ACL exceeded (utilization > 100%)
- Flag stocks with "Overfished" or "Overfishing" status
- Alert when SAFE report data missing for expected year
- Validate all AI extractions with confidence scores

---

## 9. Search & Analytics

### Full-Text Search
- Index SAFE report sections in PostgreSQL TSVECTOR
- Index SEDAR executive summaries
- Enable search across all assessment text

### Analytics Queries
1. **ACL Compliance Rate**: Percentage of stocks staying under ACL
2. **Stock Status Trends**: How many stocks improving vs. declining
3. **Assessment Currency**: How old is the most recent assessment per species?
4. **Management Responsiveness**: Time from assessment to management action
5. **Economic Trends**: Total fishery value changes over time

---

## 10. Deployment Considerations

### Scraping Schedule
- **SAFE reports**: Run annually after each report release (typically Q1)
- **SEDAR assessments**: Run monthly to catch new assessments
- **Manual triggers**: Admin can trigger immediate scraping

### Storage
- **HTML content**: Store in database (typically <1MB per report)
- **PDFs**: Store file paths, actual files in cloud storage or local disk
- **Extracted data**: All in database tables

### Performance
- SAFE reports: ~3 reports × multiple years = manageable volume
- SEDAR assessments: ~100+ assessments total, ~10-20 new per year
- Full-text search: Add indexes, consider PostgreSQL full-text search

---

## 11. Success Metrics

### Functional Metrics
- [ ] All current SAFE reports imported
- [ ] All historical SAFE reports imported (back to 2010)
- [ ] All completed SEDAR assessments imported
- [ ] 90%+ of species names successfully linked
- [ ] 80%+ of SEDAR-action links automatically detected

### User Value Metrics
- [ ] Users can view current stock status for all species
- [ ] Users can track ACL compliance over time
- [ ] Users can see which assessments informed which actions
- [ ] Users can search across all assessment documents
- [ ] Users can export stock status reports

---

## 12. Next Steps

### Immediate (This Session)
1. Create database migration SQL file
2. Create SQLAlchemy models
3. Build basic SAFE report scraper framework

### Short-term (Next Session)
1. Test SAFE scraper with one FMP (Snapper Grouper)
2. Build AI extraction prompts and test
3. Import first SAFE report successfully

### Medium-term (This Week)
1. Complete SAFE scraper for all FMPs
2. Build SEDAR scraper
3. Implement entity linking
4. Create API routes

### Long-term (Next Week)
1. Build frontend UI components
2. Deploy to production
3. User testing and refinement

---

## 13. Questions for User

Before proceeding with implementation:

1. **Priority**: Should we start with SAFE reports or SEDAR assessments first?
2. **Historical data**: How far back should we scrape SAFE reports? (All available vs. last 5 years)
3. **SEDAR coverage**: Focus on South Atlantic SEDARs only, or include all SEDARs?
4. **Manual linking**: Should admins be able to manually link assessments to actions?
5. **Alerts**: Should system alert when ACL exceeded or stock becomes overfished?

---

**Document Status**: Draft architecture plan
**Created**: November 20, 2025
**Next**: Begin implementation with database schema
