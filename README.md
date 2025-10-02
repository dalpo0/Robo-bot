# Robo-bot
# 🤖 Fully Customizable Telegram Bot

A completely customizable Telegram bot where users can control every feature!

## ✨ Features

- ✅ **Complete Customization** - Users control every feature
- 🏆 **Advanced Rank System** - XP, levels, leaderboards with beautiful cards
- 🖼️ **Media Library** - Add your own stickers, GIFs, memes, videos
- 💬 **Custom Commands & Responses** - Create your own bot behavior
- 🛡️ **Auto Moderation** - Banned words, warnings, auto-mute
- 🎮 **Games** - Truth or Dare, Word Games
- ⚙️ **Feature Toggles** - Enable/disable any functionality
- 💾 **SQLite Database** - Easy deployment & data persistence

## 🚀 Quick Start

### 1. Get Bot Token
- Message [@BotFather](https://t.me/BotFather) on Telegram
- Use `/newbot` command
- Copy your bot token

### 2. Setup & Run
```bash
# Clone or create the project structure
cd telegram-custom-bot

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Edit .env file with your bot token
nano .env  # Add: BOT_TOKEN=your_actual_token_here

# Run the bot
python scripts/run_all.py
