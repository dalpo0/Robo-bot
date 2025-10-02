import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Token from @BotFather (REQUIRED)
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Database Configuration
    DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_database.db")
    
    # Bot Settings
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
    
    # Feature Defaults
    DEFAULT_FEATURES = {
        'anti_spam': True,
        'welcome_message': True,
        'ranking_system': True,
        'truth_or_dare': True,
        'word_games': True,
        'meme': True,
        'video': True,
        'gif': True,
        'sticker': True,
        'greet_users': True,
        'report_system': True,
        'message_counter': True,
        'auto_detect_admins': True,
        'owner_controls': True,
        'rank_system': True,
        'daily_rewards': True
    }
    
    # Media Limits
    MAX_MEDIA_PER_USER = int(os.getenv("MAX_MEDIA_PER_USER", "100"))
    MAX_CUSTOM_COMMANDS = int(os.getenv("MAX_CUSTOM_COMMANDS", "50"))

# Validate required settings
if not Config.BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable is required! Get it from @BotFather")
