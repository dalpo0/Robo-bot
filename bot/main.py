import asyncio
import logging
from telegram.ext import Application
from bot.database import BotDatabase
from bot.customization import CustomizationSystem
from bot.handlers import register_all_handlers
from config import Config

logger = logging.getLogger(__name__)

class CustomizableBot:
    def __init__(self):
        self.db = BotDatabase(Config.DATABASE_PATH)
        self.customizer = CustomizationSystem(self.db)
        self.application = None
    
    async def initialize(self):
        """Initialize bot components"""
        await self.db.initialize()
        await self._set_default_settings()
        await self._create_application()
        await register_all_handlers(self.application, self.db, self.customizer)
        logger.info("✅ Bot initialized successfully!")
    
    async def _set_default_settings(self):
        """Set default global settings"""
        default_settings = {
            'max_media_per_user': Config.MAX_MEDIA_PER_USER,
            'max_custom_commands': Config.MAX_CUSTOM_COMMANDS,
            'default_language': 'en',
            'backup_interval_hours': 24
        }
        
        for key, value in default_settings.items():
            current = await self.db.get_global_setting(key)
            if current is None:
                await self.db.set_global_setting(key, value, f"Default {key}")
    
    async def _create_application(self):
        """Create Telegram application"""
        self.application = (
            Application.builder()
            .token(Config.BOT_TOKEN)
            .build()
        )
    
    async def run(self):
        """Start the bot"""
        if not self.application:
            await self.initialize()
        
        logger.info("🤖 Bot is running and ready!")
        await self.application.run_polling()

async def main():
    """Main entry point"""
    try:
        bot = CustomizableBot()
        await bot.initialize()
        logger.info("🚀 Starting Fully Customizable Telegram Bot...")
        await bot.run()
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
