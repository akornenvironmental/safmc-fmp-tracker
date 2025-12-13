#!/bin/bash
echo -ne "\033]0;SAFMC-FMP\007"
echo -ne "\033]1;SAFMC-FMP\007"
cd ~/Desktop/SAFMC-FMP

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📋 SAFMC-FMP Development Environment"
echo "  📍 Location: $(pwd)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".env" ]; then
    source .env
    echo "  ✅ Environment variables loaded"
    
    if [ "$(uname)" = "Darwin" ]; then
        last_modified=$(stat -f %m ".env")
    else
        last_modified=$(stat -c %Y ".env")
    fi
    current_time=$(date +%s)
    days_old=$(((current_time - last_modified) / 86400))
    
    if [ $days_old -gt 7 ]; then
        echo "  ⚠️  .env file is $days_old days old"
        echo "  💡 Sync: render services env-get safmc-fmp-tracker-backend > .env"
    fi
else
    echo "  ⚠️  No .env file found"
    echo "  💡 Create: render services env-get safmc-fmp-tracker-backend > .env"
fi

echo "  🤖 Starting Claude Code (Sonnet 4.5)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Unset API keys so Claude Code uses your claude.ai login instead
export ANTHROPIC_API_KEY=""
export CLAUDE_API_KEY=""
claude --model sonnet
