#!/bin/bash
# Cortana Mega Bot - One-Click Startup

cd /Users/cortana/.openclaw/workspace/projects/cortana-mega-bot

# Create .env if missing
if [ ! -f .env ]; then
    cat > .env << EOF
TELEGRAM_BOT_TOKEN=8572628843:AAFFl71Dpj3DRyAYJrCRJ66sYBGKJV3y9PA
ADMIN_ID=8148840480
MOCK_MODE=true
EOF
fi

# Create venv if missing
if [ ! -d venv ]; then
    python3 -m venv venv
fi

# Install and run
source venv/bin/activate
pip install -q -r requirements.txt

echo "⚡ Starting Cortana Mega Bot..."
echo "Commands: /video /dinner /money /leads"
nohup python bot.py > bot.log 2>&1 &
echo $! > bot.pid
echo "✅ Bot started! PID: $(cat bot.pid)"
echo "📋 Logs: tail -f bot.log"
