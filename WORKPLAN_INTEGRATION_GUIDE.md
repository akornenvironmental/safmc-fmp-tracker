# SAFMC Workplan Integration Guide

## Overview

The FMP Tracker now includes comprehensive workplan integration that tracks council amendment timelines with full version history. This system automatically or manually imports workplan Excel files released at council meetings and links them to actions, meetings, comments, and documents.

## Key Features

### ✅ Implemented

1. **Version History** - Track how amendments evolve across multiple workplan versions
2. **Complete Data Import** - Status, timeline milestones (S, DOC, PH, A), lead staff, priorities
3. **Automatic Action Matching** - Fuzzy matching to link workplan items to existing actions
4. **Timeline Milestones** - Detailed tracking of Scoping, Public Hearing, Approval, etc.
5. **Excel Parser** - Robust parser for SAFMC workplan file format
6. **Entity Linking** - Connect workplans → actions → meetings → comments

### 🚧 To Be Implemented

7. **Automatic Council Meeting Scraper** - Auto-download workplan files from meeting pages
8. **Admin Upload Interface** - Web UI for manual workplan uploads
9. **Frontend Workplan View** - Interactive timeline visualization
10. **Comment Phase Linking** - Automatically tag comments with milestone phases

---

## Database Schema

### Core Tables

#### `workplan_versions`
Tracks different versions of the workplan (one per council meeting)

```sql
- id: Unique version ID
- version_name: "Q3 2025", "September 2025 Meeting"
- council_meeting_id: Link to meeting (optional)
- source_url: Where file was downloaded
- source_file_name: Original filename
- upload_type: 'auto_scraped' or 'manual_upload'
- quarter, fiscal_year: Metadata
- effective_date: When this version became active
- is_active: TRUE for current version
```

#### `workplan_items`
Individual amendments within each workplan version

```sql
- id: Unique item ID
- workplan_version_id: FK to version
- amendment_id: "SG Reg 37", "Coral 11/Shrimp 12"
- action_id: FK to actions table (linked)
- topic: Amendment description
- status: 'UNDERWAY', 'PLANNED', 'COMPLETED', 'DEFERRED'
- lead_staff: SAFMC staff ("Mike", "Kathleen & Allie")
- sero_priority: 'Primary', 'Secondary'
```

#### `workplan_milestones`
Timeline milestones for each amendment

```sql
- id: Unique milestone ID
- workplan_item_id: FK to workplan item
- milestone_type: 'S', 'DOC', 'PH', 'A', 'AR', 'SUBMIT', 'IMPL'
- scheduled_date: When milestone is scheduled
- scheduled_meeting: "Dec 2025", "March 2026"
- meeting_id: FK to actual meeting (when linked)
- is_completed: Completion status
- completed_date: When it was completed
```

#### `milestone_types`
Reference table for milestone codes

| Code | Name | Description |
|------|------|-------------|
| AR | Assessment Report | Stock assessment presented |
| S | Scoping | Public scoping approved |
| DOC | Document Review | Review actions/alternatives |
| PH | Public Hearing | Public hearings |
| A | Approval | Final approval for submission |
| SUBMIT | Submitted | Submitted to NMFS |
| IMPL | Implementation | Rule implemented |

---

## Usage

### 1. Import a Workplan File (Python)

```python
from src.services.workplan_service import WorkplanService

# Manual upload
result = WorkplanService.import_workplan_file(
    file_path='/path/to/workplan.xlsx',
    version_name='September 2025 Council Meeting',
    upload_type='manual_upload',
    user_id=1,
    source_url='https://safmc.net/events/september-2025-council-meeting/'
)

print(f"Imported {result['items_created']} items")
print(f"Created {result['milestones_created']} milestones")
```

### 2. Get Current Workplan

```python
current = WorkplanService.get_current_workplan()

print(f"Version: {current['version']['versionName']}")
print(f"Items: {len(current['items'])}")

for item in current['items']:
    print(f"{item['amendmentId']}: {item['topic']}")
    print(f"  Status: {item['status']}")
    print(f"  Milestones: {len(item['milestones'])}")
```

### 3. View Amendment History

```python
# See how an amendment evolved across versions
history = WorkplanService.get_workplan_history('Coral 11/Shrimp 12')

for entry in history:
    version = entry['version']
    item = entry['item']
    print(f"{version['versionName']}: Status={item['status']}")
```

### 4. Link Milestones to Meetings

```python
# Connect a workplan milestone to an actual meeting record
WorkplanService.link_milestone_to_meeting(
    milestone_id=123,
    meeting_id='council-sept-2025'
)
```

### 5. Mark Milestone Completed

```python
WorkplanService.mark_milestone_completed(milestone_id=123)
```

---

## Excel File Format

### Expected Structure

The parser expects SAFMC workplan Excel files with this structure:

**Sheet: "2025 - 2027 WorkPlan"** (or similar name containing "WorkPlan")

| Row | Content |
|-----|---------|
| 1 | Title row |
| 2 | (blank) |
| 3 | **Headers**: Col 2="Amendment #", Col 3="Topic", Col 4="SAFMC Lead", Col 5="SERO Priority", Cols 6+= Meeting dates |
| 4+ | **Data rows**: Status sections ("UNDERWAY", "PLANNED") followed by amendment rows |

### Example Data Row

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 | Col 7 | Col 8 |
|-------|-------|-------|-------|-------|-------|-------|-------|
| UNDERWAY | Coral 11/Shrimp 12 | SFAA in Oculina HAPC | Kathleen & Allie | Secondary | A | | |

Timeline columns (6+) contain milestone codes:
- **S** = Scoping
- **DOC** = Document Review
- **PH** = Public Hearing
- **A** = Approval
- **PH/A** = Combined (both PH and A at that meeting)

---

## API Endpoints (To Be Created)

### Upload Workplan

```
POST /api/workplan/upload
Content-Type: multipart/form-data

{
  "file": <Excel file>,
  "versionName": "September 2025 Council Meeting",
  "councilMeetingId": "council-sept-2025" (optional)
}

Response:
{
  "success": true,
  "versionId": 123,
  "itemsCreated": 34,
  "milestonesCreated": 156
}
```

### Get Current Workplan

```
GET /api/workplan/current

Response:
{
  "version": {
    "id": 123,
    "versionName": "Q3 2025",
    "effectiveDate": "2025-09-15"
  },
  "items": [
    {
      "id": 456,
      "amendmentId": "Coral 11/Shrimp 12",
      "actionId": "coral-11-shrimp-12",
      "topic": "SFAA in Oculina HAPC",
      "status": "UNDERWAY",
      "leadStaff": "Kathleen & Allie",
      "milestones": [
        {
          "type": "A",
          "scheduledDate": "2025-12-01",
          "scheduledMeeting": "Dec 2025",
          "isCompleted": false
        }
      ]
    }
  ]
}
```

### Get Workplan History

```
GET /api/workplan/history/:amendmentId

Response:
{
  "amendmentId": "Coral 11/Shrimp 12",
  "history": [
    {
      "version": { "versionName": "Q3 2025", "effectiveDate": "2025-09-15" },
      "item": { "status": "UNDERWAY", "milestones": [...] }
    },
    {
      "version": { "versionName": "Q2 2025", "effectiveDate": "2025-06-10" },
      "item": { "status": "PLANNED", "milestones": [...] }
    }
  ]
}
```

### Get All Versions

```
GET /api/workplan/versions

Response:
{
  "versions": [
    {
      "id": 123,
      "versionName": "September 2025 Council Meeting",
      "effectiveDate": "2025-09-15",
      "isActive": true,
      "itemCount": 34
    }
  ]
}
```

---

## Database Migration

Run the migration to create the workplan tables:

```bash
# Using psql
psql $DATABASE_URL -f migrations/create_workplan_system.sql

# Or using Python migration script (to be created)
python run_migration.py create_workplan_system
```

---

## Integration Points

### 1. Actions Table Enhanced
The `actions` table now includes workplan fields:
- `current_workplan_status` - Latest status from active workplan
- `lead_staff` - SAFMC lead staff
- `sero_priority` - SERO priority level
- `next_milestone_type` - Next upcoming milestone
- `next_milestone_date` - When next milestone is scheduled

### 2. Comments Table Enhanced
The `comments` table can now track which milestone phase a comment was from:
- `milestone_type` - 'S' (Scoping), 'PH' (Public Hearing), etc.
- `workplan_item_id` - Link to specific workplan item

### 3. Meetings Linkage
Workplan milestones can be linked to actual meeting records via `meeting_id` FK.

---

## Example: Full Workflow

### Step 1: Council releases new workplan
September 2025 council meeting happens, new workplan Excel file is published.

### Step 2: Import workplan
```python
result = WorkplanService.import_workplan_file(
    file_path='/tmp/downloaded_workplan.xlsx',
    version_name='September 2025 Council Meeting',
    upload_type='auto_scraped',
    source_url='https://safmc.net/events/september-2025-council-meeting/'
)
```

### Step 3: System matches amendments to actions
- "Coral 11/Shrimp 12" → Matches existing action `coral-11-shrimp-12`
- "SG Reg 37" → Creates new action `sg-reg-37`
- Updates action statuses and next milestones

### Step 4: Timeline is displayed
Frontend shows interactive timeline for each amendment with milestones color-coded by type.

### Step 5: Comments are linked
When users submit comments during Public Hearing phase, they're automatically tagged with `milestone_type='PH'`.

### Step 6: Version history
Next quarter's workplan is imported, previous version is archived (is_active=FALSE), allowing comparison of how timelines changed.

---

## Next Steps

1. ✅ **Create migration** - `migrations/create_workplan_system.sql`
2. ✅ **Create models** - `src/models/workplan.py`
3. ✅ **Create parser** - `src/scrapers/workplan_parser.py`
4. ✅ **Create service** - `src/services/workplan_service.py`
5. 🚧 **Create API routes** - `/api/workplan/*` endpoints
6. 🚧 **Create frontend UI** - Workplan timeline view
7. 🚧 **Create scraper** - Auto-download from council meeting pages
8. 🚧 **Test with production data** - Import historical workplans

---

## Files Created

```
migrations/
  └── create_workplan_system.sql          - Database schema

src/models/
  └── workplan.py                         - SQLAlchemy models

src/scrapers/
  └── workplan_parser.py                  - Excel parser

src/services/
  └── workplan_service.py                 - Business logic

WORKPLAN_INTEGRATION_GUIDE.md             - This file
```

---

## Testing

Test the parser:

```bash
cd /Users/akorn/safmc-fmp-tracker

python3 << 'EOF'
from src.scrapers.workplan_parser import parse_workplan_file

result = parse_workplan_file('/Users/akorn/Desktop/fc2_a1_safmc_workplanq3_202509-xlsx.xlsx')

print(f"Amendments: {len(result['amendments'])}")
print(f"Timeline columns: {len(result['timeline_headers'])}")

for amend in result['amendments'][:3]:
    print(f"\n{amend['amendment_id']}: {amend['status']}")
    print(f"  Milestones: {len(amend['milestones'])}")
EOF
```

Test the import service (after running migration):

```bash
python3 << 'EOF'
from app import app
from src.services.workplan_service import WorkplanService

with app.app_context():
    result = WorkplanService.import_workplan_file(
        file_path='/Users/akorn/Desktop/fc2_a1_safmc_workplanq3_202509-xlsx.xlsx',
        version_name='Q3 2025 - September 2025 Meeting'
    )

    print(f"Success: {result['success']}")
    print(f"Items created: {result.get('items_created')}")
    print(f"Milestones created: {result.get('milestones_created')}")
EOF
```

---

## Support

For questions or issues with the workplan integration, contact the development team or file an issue in the project repository.
