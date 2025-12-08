# Database Access Guide

## Quick Start

### Option 1: Interactive SQL Shell (Recommended for exploration)
```bash
./connect_db.sh
```

Then run any SQL query:
```sql
SELECT * FROM actions LIMIT 5;
\q
```

### Option 2: Single Query (Quick checks)
```bash
PGPASSWORD='2q7bzxUgJdhCdjaJhKOsfEsVrEpsrvyp' psql \
  -h dpg-d44eeo3uibrs73a2nkhg-a.oregon-postgres.render.com \
  -U safmc_fmp_user \
  -d safmc_fmp_tracker \
  -c "SELECT COUNT(*) FROM actions;"
```

### Option 3: Python Scripts (Recommended for updates)
```bash
python3 quick_fix_progress_auto.py
```

---

## Useful Files

- **connect_db.sh** - Quick connection to database
- **useful_queries.sql** - Cheat sheet of common queries
- **quick_fix_progress_auto.py** - Example Python script
- **fix_progress_percentages.py** - Interactive update script

---

## Common Tasks

### View Actions
```bash
./connect_db.sh
```
```sql
SELECT title, fmp, progress_stage, progress_percentage
FROM actions
ORDER BY updated_at DESC
LIMIT 10;
```

### Count by Stage
```sql
SELECT progress_stage, COUNT(*)
FROM actions
GROUP BY progress_stage
ORDER BY COUNT(*) DESC;
```

### Update Data (Use Python for safety)
See `quick_fix_progress_auto.py` as template

---

## Connection Details

- **Host:** dpg-d44eeo3uibrs73a2nkhg-a.oregon-postgres.render.com
- **Port:** 5432
- **Database:** safmc_fmp_tracker
- **User:** safmc_fmp_user
- **Password:** (in environment/scripts)

---

## Safety Tips

1. **Always test SELECT before UPDATE**
2. **Use transactions for safety:**
   ```sql
   BEGIN;
   UPDATE ...;
   SELECT * FROM ... LIMIT 5;  -- Check results
   COMMIT;  -- or ROLLBACK if wrong
   ```
3. **Python scripts are safer** - they show preview and ask confirmation
4. **Backup before major changes** (Render handles this automatically)

---

## psql Commands

- `\dt` - List tables
- `\d table_name` - Show table structure
- `\q` - Quit
- `\h` - Help
- `\?` - List all commands

---

## Need Help?

Check **useful_queries.sql** for example queries!
