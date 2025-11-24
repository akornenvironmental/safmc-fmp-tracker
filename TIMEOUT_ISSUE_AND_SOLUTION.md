# Comprehensive Scraper Timeout Issue

## Problem

The comprehensive amendment scraper (`/api/scrape/amendments/comprehensive`) times out when called via HTTP because:

1. **Render Free Tier Limitation**: 30-second timeout for HTTP requests
2. **Scraper Duration**: 10-15 minutes to complete
3. **Result**: 502 Bad Gateway error after ~2 minutes

## Test Results

- Local test: Successfully found **215 amendments**
- Production API test: Failed with 502 after 2 minutes
- Error: HTML error page instead of JSON response

## Solutions (Ranked)

### Option 1: Background Job Processing (RECOMMENDED)

**Implementation:**
- Modify endpoint to start scraper in background thread
- Return immediately with status message
- User checks `/api/logs/scrape` for completion

**Pros:**
- Works on free tier
- No code/infrastructure changes
- Proper long-running task handling

**Code Changes Required:**
```python
# In src/routes/api_routes.py

@bp.route('/scrape/amendments/comprehensive', methods=['POST'])
@require_admin
def scrape_amendments_comprehensive():
    import threading

    def run_scrape():
        # Move all scraping logic here
        # with app.app_context(): for database access
        pass

    # Start background thread
    thread = threading.Thread(target=run_scrape, daemon=True)
    thread.start()

    # Return immediately
    return jsonify({
        'success': True,
        'message': 'Comprehensive scrape started in background',
        'checkStatus': '/api/logs/scrape?source=amendments_comprehensive'
    })
```

**Cons:**
- Slightly more complex
- No immediate feedback on success/failure

---

### Option 2: Batch Processing by FMP

**Implementation:**
- Create 8 separate endpoints (one per FMP)
- Each scrapes single FMP (< 30 seconds)
- Call all 8 endpoints sequentially

**Pros:**
- Simple to implement
- Works on free tier
- Granular control

**Example:**
```bash
# Scrape each FMP separately
curl -X POST .../api/scrape/amendments/fmp?name=Snapper%20Grouper
curl -X POST .../api/scrape/amendments/fmp?name=Dolphin%20Wahoo
# ... repeat for all 8 FMPs
```

**Cons:**
- Requires 8 separate API calls
- More manual orchestration
- Harder to maintain

---

### Option 3: Upgrade Render Plan

**Implementation:**
- Upgrade to paid Render plan ($7/month minimum)
- Removes HTTP timeout limits

**Pros:**
- No code changes needed
- Proper solution for production

**Cons:**
- Monthly cost
- May still hit other limits eventually

---

## Immediate Workaround

Since the scraper code is working (locally found 215 amendments), you can:

1. **Run locally and export data:**
   ```bash
   python3 -c "
   from src.scrapers.amendments_scraper_enhanced import EnhancedAmendmentsScraper
   scraper = EnhancedAmendmentsScraper()
   results = scraper.scrape_all_comprehensive()
   # Save to JSON, then import to production DB
   "
   ```

2. **Manual database import:**
   - Export local results to SQL
   - Import into production database via Render dashboard

---

## Recommended Next Steps

### For Now (Quick Fix):
1. Document the issue (this file) ✅
2. Move forward with Phase 2 planning
3. Let scraper run locally when needed

### For Production (Proper Fix):
1. Implement Option 1 (background jobs)
2. Add progress tracking endpoint
3. Add admin UI to trigger and monitor scrapes

### Timeline Estimate:
- **Background job implementation**: 2-3 hours
- **Testing**: 30 minutes
- **Deployment**: 15 minutes
- **Total**: ~4 hours

---

## Related Files

- **Scraper**: `src/scrapers/amendments_scraper_enhanced.py`
- **API Route**: `src/routes/api_routes.py` (line 510)
- **Documentation**:
  - `COMPREHENSIVE_DATA_IMPORT_GUIDE.md`
  - `PHASE_2_VECTOR_SEARCH_PLAN.md`
  - `FEATURE_ROADMAP.md`

---

## Current Status

✅ Enhanced scraper coded and deployed
✅ Local testing successful (215 amendments found)
❌ Production API call times out
📋 Documented issue and solutions
📋 Phase 2 planning complete
⏳ Awaiting implementation of background job solution

---

## Summary

The comprehensive scraper works perfectly but can't complete via HTTP on Render's free tier due to timeout limits. The recommended solution is to implement background job processing, which will take ~4 hours to implement properly. In the meantime, the scraper can be run locally or we can proceed with Phase 2 (Vector Search) planning and implementation.
