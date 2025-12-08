#!/bin/bash
# Quick connect to SAFMC FMP Tracker database

export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
PGPASSWORD='2q7bzxUgJdhCdjaJhKOsfEsVrEpsrvyp' psql -h dpg-d44eeo3uibrs73a2nkhg-a.oregon-postgres.render.com -U safmc_fmp_user -d safmc_fmp_tracker
