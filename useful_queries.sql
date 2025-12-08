-- SAFMC FMP Tracker - Useful SQL Queries
-- Run these with: ./connect_db.sh
-- Or: PGPASSWORD='...' psql -h ... -c "query here"

-- ==================== ACTIONS ====================

-- Count all actions
SELECT COUNT(*) as total_actions FROM actions;

-- Actions by stage
SELECT progress_stage, COUNT(*) as count
FROM actions
GROUP BY progress_stage
ORDER BY count DESC;

-- Actions by FMP
SELECT fmp, COUNT(*) as count
FROM actions
GROUP BY fmp
ORDER BY count DESC;

-- Recent actions
SELECT title, progress_stage, progress_percentage, updated_at
FROM actions
ORDER BY updated_at DESC
LIMIT 10;

-- Find actions with specific word
SELECT title, fmp, progress_stage
FROM actions
WHERE title ILIKE '%comprehensive%'
LIMIT 10;

-- Implementation stage actions
SELECT title, progress_percentage
FROM actions
WHERE progress_stage = 'Implementation'
ORDER BY title;

-- ==================== COMMENTS ====================

-- Count comments
SELECT COUNT(*) as total_comments FROM comments;

-- Comments by position
SELECT position, COUNT(*) as count
FROM comments
GROUP BY position
ORDER BY count DESC;

-- Comments by FMP (via action)
SELECT a.fmp, COUNT(c.id) as comment_count
FROM comments c
LEFT JOIN actions a ON c.action_id = a.action_id
GROUP BY a.fmp
ORDER BY comment_count DESC;

-- Recent comments
SELECT name, organization, position, comment_date
FROM comments
ORDER BY comment_date DESC
LIMIT 10;

-- ==================== MEETINGS ====================

-- Count meetings
SELECT COUNT(*) as total_meetings FROM meetings;

-- Meetings by type
SELECT meeting_type, COUNT(*) as count
FROM meetings
GROUP BY meeting_type
ORDER BY count DESC;

-- Upcoming meetings
SELECT title, start_date, council
FROM meetings
WHERE start_date > NOW()
ORDER BY start_date
LIMIT 10;

-- ==================== STOCK ASSESSMENTS ====================

-- Count assessments
SELECT COUNT(*) as total_assessments FROM stock_assessments;

-- Assessments by status
SELECT
    CASE
        WHEN overfished AND overfishing_occurring THEN 'Critical'
        WHEN overfished THEN 'Overfished'
        WHEN overfishing_occurring THEN 'Overfishing'
        ELSE 'Healthy'
    END as status,
    COUNT(*) as count
FROM stock_assessments
GROUP BY status
ORDER BY count DESC;

-- Species with assessments
SELECT species, COUNT(*) as assessment_count
FROM stock_assessments
GROUP BY species
ORDER BY assessment_count DESC;

-- ==================== DATABASE INFO ====================

-- List all tables
\dt

-- Show table structure
\d actions
\d comments
\d meetings
\d stock_assessments

-- Database size
SELECT pg_size_pretty(pg_database_size('safmc_fmp_tracker')) as db_size;

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ==================== UPDATES (BE CAREFUL!) ====================

-- Update action progress (example - we just did this)
UPDATE actions
SET progress_percentage = 100, updated_at = NOW()
WHERE LOWER(progress_stage) LIKE '%implementation%'
  AND progress_percentage != 100;

-- Fix NULL values (example)
UPDATE actions
SET fmp = 'Unknown FMP'
WHERE fmp IS NULL;

-- Always test with SELECT first!
SELECT * FROM actions WHERE condition_here LIMIT 5;
-- Then run UPDATE if results look correct

-- ==================== USEFUL TIPS ====================

-- Always backup before major changes:
-- Use transactions for safety:
BEGIN;
UPDATE actions SET ...;
-- Check results
SELECT * FROM actions WHERE ... LIMIT 5;
-- If good: COMMIT;
-- If bad:  ROLLBACK;

-- Quit psql
\q
