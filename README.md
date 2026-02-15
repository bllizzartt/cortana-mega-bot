# 🤖 Cortana Mega Bot

Your all-in-one Telegram AI assistant. Handles video generation, meal planning, money tracking, lead generation, and more.

## 🚀 Features

- **🎥 Video Generation** — AI videos from photos (Seedance integration)
- **🍳 Meal Bot** — Daily dinner suggestions (Italian & Asian)
- **💰 Money Tracker** — Income, expenses, wealth projections
- **📊 Lead Scraper** — Find business leads
- **🧠 Berman Strategies** — Memory, calendar, Polymarket

## 📱 Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome menu |
| `/video` | Generate AI video |
| `/dinner` | Get dinner suggestion |
| `/money` | Financial dashboard |
| `/leads` | Lead generation |
| `/memory` | Memory management |
| `/calendar` | Smart scheduling |
| `/trade` | Polymarket bot |

## 🛠️ Setup

```bash
# Clone repo
git clone https://github.com/bllizzartt/cortana-mega-bot.git
cd cortana-mega-bot

# Run
./start.sh
```

## 📁 Structure

```
cortana-mega-bot/
├── bot.py                 # Main bot
├── modules/
│   ├── video_gen.py      # Video generation
│   ├── meal_bot.py       # Meal suggestions
│   ├── money_tracker.py  # Finance tracking
│   └── lead_scraper.py   # Lead generation
├── requirements.txt
└── start.sh
```

## ⚙️ Configuration

Edit `.env`:
```
TELEGRAM_BOT_TOKEN=your_token
ADMIN_ID=your_telegram_id
MOCK_MODE=true  # Set false after Feb 24 for real videos
```

## 🎯 Next Steps

1. **Feb 24, 2026** — Flip `MOCK_MODE=false` for real Seedance videos
2. Add more meal recipes (expand beyond 6)
3. Connect real calendar APIs
4. Add Polymarket API key for trading

## 💡 Usage

Message `@Cortana738468373_bot` on Telegram:
- Send `/start` to see menu
- Upload photos + prompt for videos
- Get daily dinner at 4 PM

---
Built by Chase + Cortana ⚡
