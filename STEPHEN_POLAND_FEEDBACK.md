# Stephen Poland Feedback - November 24, 2025

**From:** Stephen Poland (Cynoscion Environmental Consulting LLC)
**To:** Aaron Kornbluth, Purcie
**Date:** November 24, 2025 8:28 PM

---

## Dashboard Issues

### 1. 'Permit' Showing as Species ⚠️
**Issue:** Permit-related amendments are being categorized as a species when they're actually comprehensive/omnibus amendments.

**Recommendation:** Create a new category for comprehensive/omnibus amendments
- Suggested name: "Multiple FMP Action" or "Comprehensive Amendment"
- This would better represent amendments that affect multiple FMPs

**Priority:** Medium
**Effort:** Low
**Implementation:**
- Add "Comprehensive Amendment" type to Action model
- Update scraper to detect comprehensive amendments
- Add filter option in UI

---

### 2. Recent Activity Links Not Working Correctly ⚠️
**Issue:** Clicking on items in 'Recent Activity' list takes you to the broader page instead of the specific item.

**Expected Behavior:** Direct link to the specific action/amendment

**Priority:** Medium
**Effort:** Low
**Implementation:**
- Update Recent Activity component to use anchor links
- Example: `/actions#action-{id}` or `/actions/{id}`

---

## Actions Page Issues

### 3. Progress Bars Not Populated Correctly ⚠️
**Issue:**
- Most actions showing 0% progress
- Some completed actions showing 95%
- Implemented actions should show 100% or "Completed"

**Root Cause:** SAFMC site shows completed actions at "Implementation" stage, but they're actually finished.

**Recommendations:**
1. Add "Completed" or "Completed and Implemented" status
2. Distinguish between:
   - Active amendments (in progress)
   - Implemented amendments (complete and in effect)
   - Superseded amendments (replaced by newer actions)

**Context from Stephen:**
> "Some of these are old amendments that are 'dead' since later actions superseded these. However, an FMP is a collection of all amendments and some older actions are still in effect while others are moot. Most folks assume that the most recent amendment is the 'current' FMP."

**Priority:** High
**Effort:** Medium
**Implementation:**
- Update progress calculation logic
- Add "Completed" status (100%)
- Add "Superseded" status indicator
- Consider adding "Last Modified Date" to help identify active vs superseded

---

### 4. Dark Mode Text Color Issues ⚠️
**Issue:** 'Public Hearing' status is difficult to see in dark view due to text color.

**Priority:** Medium
**Effort:** Low
**Implementation:**
- Review all status badge colors in dark mode
- Ensure WCAG AA contrast compliance
- Test: Public Hearing, Council Meeting, and other status badges

---

### 5. Add "Comprehensive Amendment" Type ✨
**Enhancement:** Add "Comprehensive Amendment" as a searchable/filterable type

**Priority:** Medium
**Effort:** Low
**Implementation:**
- Add to Action type enum
- Update search filters
- Update scraper to tag comprehensive amendments

---

### 6. Make Description Column Default ✨
**Enhancement:** Set "description" column as visible by default in Actions table

**Priority:** Low
**Effort:** Low
**Implementation:**
- Update default column visibility in Actions.jsx
- Save user preferences in localStorage

---

## Meetings Page Issues

### 7. Dark Mode Calendar Text Issues ⚠️
**Issue:** 'Council Meeting' text is difficult to see in dark view

**Priority:** Medium
**Effort:** Low
**Implementation:**
- Review meeting type colors in dark mode
- Ensure contrast compliance

---

### 8. Missing Organizations in Calendar ⚠️
**Issue:** Not all organizations are showing on the calendar

**Priority:** Medium
**Effort:** Medium
**Investigation Needed:**
- Which organizations are missing?
- Is this a filtering issue or data issue?

---

### 9. Meetings Not Showing in Calendar View ⚠️
**Issue:** Many meetings are not appearing in calendar view

**Priority:** High
**Effort:** Medium
**Investigation Needed:**
- Are they in the database?
- Is this a date parsing issue?
- Are they filtered out?

---

## Comments Page Issues

### 10. All Comments Labeled as "Coral, Shrimp FMP" 🐛
**Issue:** All comments are incorrectly labeled as belonging to Coral and Shrimp FMPs when they're for various other FMPs

**Root Cause:** Likely scraper or FMP detection logic error

**Priority:** High
**Effort:** Medium
**Investigation:**
- Check comments scraper FMP detection
- Review comment-to-action linking logic
- Verify source data mapping

**Files to Check:**
- `src/scrapers/comments_scraper.py`
- Comment-to-Action association logic

---

### 11. Position Detection Inaccurate ⚠️
**Issue:** "By Position" detection is labeling comments as "neutral" when they're clearly not

**Question:** How does the tracker determine position?

**Priority:** Medium
**Effort:** High (if using AI) / Medium (if rule-based)
**Investigation:**
- Review sentiment analysis logic
- Consider:
  - Using Claude AI for better sentiment detection
  - Manual review and correction interface
  - Confidence scores for positions

---

### 12. AI Comment Summary Feature Request ✨
**Enhancement:** Provide AI-generated summary of comments (similar to Amazon product review summaries)

**Use Case:** "For actions that have a lot of comments I would have found that useful as a council member"

**Note:** "I assume this is what the AI analyzer does but it is currently not working"

**Priority:** High (for Phase 2)
**Effort:** Medium
**Implementation:**
- This aligns with Phase 2: Vector Search plan
- Would use Claude AI to summarize key themes
- Could show:
  - Common concerns
  - Support vs opposition ratio
  - Key stakeholder positions
  - Frequently mentioned topics

**Related:** See `PHASE_2_IMPLEMENTATION_CHECKLIST.md`

---

### 13. Species Detection Not Working 🐛
**Issue:** 'Detect Species' feature is not functional

**Priority:** Medium
**Effort:** Medium
**Investigation:**
- Check species detection logic
- Test with sample comments
- Verify species list is comprehensive

---

## Stock Assessment Page Issues

### 14. 'Permit' Showing as Species ⚠️
**Issue:** Same as Dashboard issue #1 - comprehensive amendments being categorized incorrectly

**Priority:** Medium
**Effort:** Low
**See:** Dashboard Issue #1

---

### 15. Stock Status Terminology ⚠️
**Issue:** "Healthy" status may not be completely accurate

**Recommendation:** Use official designations:
- "Not Overfished/Not Overfishing"
- "Overfished"
- "Experiencing Overfishing"
- "Unassessed"

**Stephen's Note:**
> "I like 'Healthy' but not sure it is completely accurate. It is probably best to keep to the official designations here."

**Priority:** Medium
**Effort:** Low
**Implementation:**
- Update stock status display logic
- Map scraped data to official terms
- Add tooltip explaining what each status means

---

### 16. Biomass/Removals Ratios - Positive Feedback ✅
**Feedback:** "I really like the inclusion of the biomass and removals ratios and the associated SEDARs"

**Action:** No changes needed - feature is working well!

---

## Work Plan Page Issues

### 17. Gantt Chart View Request ✨
**Enhancement:** Add option to view work plan as a Gantt chart

**Priority:** Medium
**Effort:** High
**Implementation:**
- Research Gantt chart libraries (e.g., dhtmlxGantt, Frappe Gantt)
- Map work plan data to Gantt format
- Add view toggle (Table / Timeline / Gantt)

**Benefits:**
- Better visualization of project timelines
- See dependencies and milestones
- Standard project management view

---

## Summary Statistics

**Total Issues:** 17
- 🐛 Critical Bugs: 2 (Comments FMP labeling, meetings not showing)
- ⚠️ Medium Priority: 11
- ✨ Enhancements: 4
- ✅ Positive Feedback: 1

**By Category:**
- Dashboard: 2 issues
- Actions: 4 issues
- Meetings: 3 issues
- Comments: 4 issues
- Stock Assessment: 3 issues
- Work Plan: 1 enhancement

---

## Recommended Priority Order

### Immediate (Next Sprint)
1. Fix Comments FMP labeling (Bug #10)
2. Fix meetings not showing in calendar (Bug #9)
3. Fix progress bars showing incorrect percentages (Issue #3)
4. Add "Comprehensive Amendment" type (Issues #1, #5, #14)

### Short Term (Following Sprint)
5. Fix dark mode contrast issues (#4, #7)
6. Fix Recent Activity links (#2)
7. Investigate missing organizations in calendar (#8)
8. Review stock status terminology (#15)

### Medium Term (Phase 2)
9. Implement AI comment summaries (#12) - Part of Vector Search phase
10. Improve position detection (#11)
11. Fix species detection (#13)
12. Make description column default (#6)

### Future Enhancements
13. Gantt chart view for work plan (#17)
14. Superseded amendment tracking (part of #3)

---

## Notes for Implementation

### Data Quality Issues
Several issues stem from scraper/data quality:
- Comments FMP detection
- Progress percentage calculation
- Species detection (Permit showing as species)

**Recommendation:** Review and enhance scrapers as part of comprehensive data audit.

### UI/UX Consistency
Dark mode contrast issues appear across multiple components:
- Standardize color palette
- Run accessibility audit (WCAG AA)
- Create component library with tested dark/light variants

### Phase 2 Alignment
Issues #11 and #12 align well with Phase 2 (Vector Search):
- AI-powered comment analysis
- Sentiment detection improvements
- Topic extraction

---

## Contact

**Stephen Poland**
Cynoscion Environmental Consulting LLC
📧 Steve.Poland@cynoscionenvironmental.com
📱 (252) 452-5067

---

*Document created: November 25, 2025*
*Last updated: November 25, 2025*
