#!/usr/bin/env python3
"""
Script to run the Telegram bot
"""

import asyncio
import logging
from bot.main import main as bot_main

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def run_bot():
    """Run the Telegram bot"""
    try:
        await bot_main()
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Telegram Bot...")
    asyncio.run(run_bot())
