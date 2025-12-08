# SAFMC FMP Tracker - Team Feedback & Issue Tracking

**Date Created:** December 8, 2025
**Last Updated:** December 8, 2025 - Phase 1 Implementation
**Status:** Phase 1 Fixes Implemented - Ready for Testing

---

## 🎯 Phase 1 Implementation Status

### ✅ COMPLETED (3 fixes)
1. **C1 - Progress Bar Calculation** - FIXED
   - Updated `_calculate_progress_percentage()` to return 100% for "implemented"/"completed" actions
   - File: `/src/scrapers/amendments_scraper.py:368-369`

2. **I1 - Permit Species Detection** - FIXED
   - Added context-aware detection to distinguish Permit fish from permit systems
   - Checks for 15+ regulatory context phrases and regex patterns
   - File: `/src/services/species_service.py:106-146`

3. **I2 - Comprehensive Amendment Type** - IMPLEMENTED
   - Added "Comprehensive Amendment" as new action type
   - Detects "comprehensive" or "omnibus" in titles
   - Sets FMP to "Multiple FMPs" when multiple FMPs detected
   - Files: `/src/scrapers/amendments_scraper.py:253-254, 279-298`

### 📋 DOCUMENTED (1 issue)
4. **C2 - Comment FMP Labeling** - ROOT CAUSE FOUND
   - Documented root cause and solution in C2 section below
   - Ready for implementation in Phase 2

### 🔄 NEXT STEPS
- Build and test changes locally
- Verify fixes with actual SAFMC data
- Deploy to production
- Monitor for regressions

---

## Overview

This document tracks all issues and recommendations received from the team member review of the SAFMC FMP Tracker tool. Issues are organized by page/feature area with severity ratings, root cause analysis, and implementation plans.

---

## 🔴 CRITICAL ISSUES (High Priority)

### C1. Progress Bars Showing Incorrect Values
**Location:** Actions page, Dashboard
**Severity:** HIGH - Misleading information to users
**Description:** Progress bars showing 0% for most actions and 95% for implemented actions

**Root Cause:**
- File: `/src/scrapers/amendments_scraper.py:359-383`
- The `_calculate_progress_percentage()` function returns 95% for "implementation" stage
- Issue: Actions that are "completed and implemented" should show 100%, not 95%
- Secondary issue: Actions may not have progress data populated correctly from scraping

**Affected Code:**
```python
# Line 372-373
if 'implement' in stage_lower:
    return 95  # Should be 100 for completed/implemented
```

**Solution:**
1. Update progress calculation to return 100% for completed/implemented actions
2. Add new stage detection for "Completed" status
3. Review scraper to ensure progress_stage is being extracted correctly
4. Add logic to distinguish between "In Implementation" (95%) vs "Completed/Implemented" (100%)

**Files to Modify:**
- `/src/scrapers/amendments_scraper.py` - Update `_calculate_progress_percentage()`
- `/src/models/action.py` - Consider adding a `completed` boolean field
- Test with actual SAFMC action tracker data

---

### C2. Comments Labeled with Wrong FMP
**Location:** Comments page
**Severity:** HIGH - Data integrity issue
**Description:** All comments showing as "Coral, Shrimp FMP" when they're for various FMPs

**Root Cause FOUND:**
- File: `/src/utils/entity_matcher.py:280-292`
- When `find_or_create_action()` creates a new Action from comment sheet metadata, it does NOT set the `fmp` field
- The FMP field is left null/empty or defaults incorrectly
- Comment sheets have amendment metadata (title, description) but FMP needs to be extracted from this metadata

**Solution:**
1. Update `/src/utils/entity_matcher.py:280-292` to extract and set FMP from amendment_title
2. Use similar logic to amendments_scraper._extract_fmp()
3. Parse amendment titles like "Comprehensive Amendment Coral 11 and Shrimp 12" to extract FMP(s)
4. May need to store multiple FMPs or use "Multiple FMPs" for comprehensive amendments

**Files to Modify:**
- `/src/utils/entity_matcher.py` - Update `find_or_create_action()` to extract and set FMP
- Consider adding FMP extraction helper function that can be shared between scrapers

---

### C3. AI Features Not Working
**Location:** Comments page
**Severity:** HIGH - Core feature broken
**Description:**
- "By Position" detection showing incorrect classifications (neutral vs actual position)
- AI analyzer not working
- "Detect Species" feature not working

**Root Cause:**
- Missing ANTHROPIC_API_KEY in Render environment variables
- Similar to interview system issue
- May also be issue with prompt engineering for position detection

**Solution - Add Environment Variable to Render:**
1. Go to https://dashboard.render.com
2. Select the safmc-fmp-tracker service
3. Navigate to "Environment" tab
4. Add new environment variable:
   - **Key:** `ANTHROPIC_API_KEY`
   - **Value:** `sk-ant-api03-...` (obtain from Anthropic Console)
5. Save and redeploy

**To Get Anthropic API Key:**
1. Visit https://console.anthropic.com/
2. Go to API Keys section
3. Create new key or copy existing key
4. Add to Render environment

**Files to Review (for prompt engineering improvements):**
- `/src/services/` - Look for AI service files
- `/src/routes/` - Comment analysis endpoints
- Check prompt accuracy for position detection once key is added

**Status:** Documented - Requires Anthropic API key from user

---

## 🟡 IMPORTANT ISSUES (Medium Priority)

### I1. 'Permit' Recognized as Species
**Location:** Dashboard, Stock Assessments
**Severity:** MEDIUM - Data categorization error
**Description:** "Permit" (the fish) is being confused with permit-type FMP actions

**Root Cause Found:**
- File: `/src/services/species_service.py:37`
- Line 37: `'Permit'` is listed in KNOWN_SPECIES array under Jacks category
- This is actually correct - Permit IS a fish species (Trachinotus falcatus)
- The issue is that comprehensive/omnibus amendments about "permits" are being tagged as Permit species

**Solution:**
1. Improve context detection in species extraction
2. Check for keywords like "permit system", "permitting", "permit requirements"
3. If "permit" appears with these context words, don't tag as species
4. Add "Comprehensive Amendment" as a separate category/type

**Files to Modify:**
- `/src/services/species_service.py` - Update `extract_species_from_text()` with context checking
- `/src/models/action.py` - Add `is_comprehensive` boolean or update `type` field options

**Implementation:**
```python
# In species_service.py
def extract_species_from_text(text: str) -> List[str]:
    # Add context checking
    if 'permit' in text.lower():
        # Check for non-species permit contexts
        permit_contexts = ['permit system', 'permitting', 'permit requirements',
                          'permit application', 'limited access permit']
        if any(ctx in text.lower() for ctx in permit_contexts):
            # Skip 'Permit' as species
            continue
```

---

### I2. Comprehensive Amendments Need Category
**Location:** Dashboard, Actions page
**Severity:** MEDIUM - UX improvement
**Description:** Need "Comprehensive Amendment" or "Multiple FMP action" category for omnibus amendments

**Solution:**
1. Add new action type "Comprehensive Amendment"
2. Update action type filter to include this option
3. Update scraper to detect comprehensive amendments

**Files to Modify:**
- `/src/models/action.py` - Update type field validation/options
- `/src/scrapers/amendments_scraper.py` - Add detection logic
- `/client/src/pages/Actions.jsx` - Add filter button for comprehensive amendments
- `/client/src/pages/Dashboard.jsx` - Display comprehensive amendments appropriately

---

### I3. Description Column Not Default on Actions Page
**Location:** Actions page
**Severity:** LOW-MEDIUM - UX improvement
**Description:** Team member wants description column shown by default

**Solution:**
- Update Actions page to show description column by default
- May need to add column visibility toggle if not already present

**Files to Modify:**
- `/client/src/pages/Actions.jsx` or `/client/src/pages/ActionsEnhanced.jsx`
- Consider adding column visibility preferences to user settings

---

### I4. Recent Activity Navigation
**Location:** Dashboard
**Severity:** MEDIUM - UX issue
**Description:** Clicking on Recent Activity items takes you to broader page, not specific item

**Current Behavior:**
- Dashboard shows recent actions
- Clicking navigates to Actions page (general)

**Expected Behavior:**
- Clicking should scroll to or highlight specific action
- Or open action detail modal/page

**Solution:**
1. Add deep linking support with action ID in URL
2. Update Dashboard to link to `/actions?id=<action_id>` or `/actions/<action_id>`
3. Update Actions page to detect URL parameter and highlight/scroll to item

**Files to Modify:**
- `/client/src/pages/Dashboard.jsx` - Update link href
- `/client/src/pages/Actions.jsx` - Add URL parameter detection and scrolling logic
- May need to add action detail modal or expand row on load

---

## 🟢 MINOR ISSUES (Low Priority)

### M1. Dark Mode Text Visibility Issues
**Location:** Actions page, Meetings page
**Severity:** LOW - Accessibility
**Description:**
- "Public Hearing" label difficult to see in dark mode
- "Council Meeting" label difficult to see in dark mode

**Root Cause:**
- Dark mode styles need better contrast
- Files: `/client/src/pages/Actions.jsx` (lines 62-65), `/client/src/pages/Meetings.jsx` (lines 51-59)

**Solution:**
Update color schemes for dark mode:

**Files to Modify:**
```jsx
// In Actions.jsx - getStageColor()
const getStageColor = (stage) => {
  if (!stage) return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';

  const stageLower = stage.toLowerCase();
  if (stageLower.includes('scoping')) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
  if (stageLower.includes('hearing')) return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
  // etc...
}
```

---

### M2. Missing Organizations on Meeting Calendar
**Location:** Meetings page (calendar view)
**Severity:** LOW-MEDIUM - Feature incomplete
**Description:** Not all organizations showing on calendar, some meetings not displaying

**Investigation Needed:**
- Check if calendar view filtering is excluding some meetings
- Verify meeting scraper is capturing all organizations
- Check if there's a display limit on calendar

**Files to Check:**
- `/client/src/pages/MeetingCalendar.jsx`
- `/src/scrapers/meetings_scraper.py`
- Calendar component filtering logic

---

### M3. Stock Assessment Status Labels
**Location:** Stock Assessments page
**Severity:** LOW - Terminology preference
**Description:** Team prefers official designations over "Healthy"

**Current:** "Healthy" label
**Preferred:** "Not Overfished/Not Overfishing" or "Not Overfished/No Overfishing"

**Also keep:** "Unassessed" status

**Solution:**
Update getStatusLabel() function in StockAssessments.jsx

**Files to Modify:**
- `/client/src/pages/StockAssessments.jsx:196-206`

```jsx
const getStatusLabel = (assessment) => {
  if (assessment.overfished && assessment.overfishing_occurring) {
    return 'Overfished/Overfishing';
  } else if (assessment.overfished) {
    return 'Overfished';
  } else if (assessment.overfishing_occurring) {
    return 'Overfishing Occurring';
  } else if (assessment.status === 'Unassessed') {
    return 'Unassessed';
  } else {
    return 'Not Overfished/No Overfishing';  // Changed from 'Healthy'
  }
};
```

---

## ✨ FEATURE REQUESTS

### F1. Gantt Chart View for Work Plan
**Location:** Work Plan page
**Severity:** ENHANCEMENT
**Description:** Add option to view work plan as Gantt chart

**Implementation Considerations:**
- Need to evaluate Gantt chart libraries for React
- Options: `react-gantt-chart`, `dhtmlx-gantt`, `frappe-gantt`
- Will need start/end dates for all work plan items
- Should be a toggle view option alongside existing view

**Files to Modify:**
- `/client/src/pages/Workplan.jsx`
- Add new component: `/client/src/components/GanttChart.jsx`
- May need to update work plan data model to ensure date fields

---

### F2. AI Comment Summarization
**Location:** Comments page
**Severity:** ENHANCEMENT
**Description:** Provide AI summary of comments (like Amazon product reviews)

**Use Case:**
- For actions with many comments, show aggregate summary
- Highlight common themes, concerns, support/opposition breakdown
- Executive summary for council members

**Implementation:**
- Use Anthropic API (Claude)
- Batch comments by action
- Generate summary showing:
  - Overall sentiment distribution
  - Top 3-5 themes/concerns
  - Representative quotes
  - Geographic patterns
  - Stakeholder type breakdown

**Files to Create:**
- `/src/services/comment_analyzer.py`
- Add endpoint: `/api/comments/analyze/:action_id`
- Update Comments page with summary view

---

## 📋 IMPLEMENTATION PRIORITY

### Phase 1 - Critical Fixes (Week 1)
1. **C1:** Fix progress bar calculations
2. **C2:** Fix comment FMP labeling
3. **I1:** Fix Permit species detection with comprehensive amendment handling

### Phase 2 - Important Issues (Week 2)
4. **C3:** Fix AI features (position detection, species detection, analyzer)
5. **I2:** Add Comprehensive Amendment category
6. **I4:** Fix Recent Activity navigation

### Phase 3 - UI Polish (Week 3)
7. **M1:** Fix dark mode visibility issues
8. **I3:** Make description column default
9. **M3:** Update stock assessment status labels
10. **M2:** Fix missing organizations on calendar

### Phase 4 - Enhancements (Week 4+)
11. **F1:** Gantt chart view for work plan
12. **F2:** AI comment summarization

---

## 🧪 TESTING CHECKLIST

After implementing each fix:

- [ ] Test on actual SAFMC data (not just mock data)
- [ ] Verify fix in both light and dark modes
- [ ] Test on mobile/responsive views
- [ ] Check database migrations work on production
- [ ] Verify no regression in related features
- [ ] Update documentation if needed

---

## 📝 NOTES FOR IMPLEMENTATION

### Environment Setup Needed
- Confirm ANTHROPIC_API_KEY is set in Render environment
- Test AI features locally before deploying

### Database Considerations
- Some fixes may require database migrations
- Test migrations on staging before production
- Backup production database before major schema changes

### Communication
- Update team member after each phase completion
- Request testing/validation from team
- Document any design decisions or trade-offs

---

## 🔗 Related Files Reference

### Frontend (React)
- `/client/src/pages/Dashboard.jsx`
- `/client/src/pages/Actions.jsx`
- `/client/src/pages/ActionsEnhanced.jsx`
- `/client/src/pages/Meetings.jsx`
- `/client/src/pages/Comments.jsx`
- `/client/src/pages/StockAssessments.jsx`
- `/client/src/pages/Workplan.jsx`
- `/client/src/context/ThemeContext.jsx`

### Backend (Python)
- `/src/scrapers/amendments_scraper.py`
- `/src/services/species_service.py`
- `/src/models/action.py`
- `/src/routes/api_routes.py`
- `/src/routes/stock_assessment_routes.py`

### Configuration
- `/app.py` - Main Flask app
- `/.env` - Environment variables
- Render environment settings

---

**Last Updated:** December 8, 2025
**Next Review:** After Phase 1 completion
