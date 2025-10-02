from .media_handlers import register_media_handlers
from .command_handlers import register_command_handlers
from .settings_handlers import register_settings_handlers
from .moderation_handlers import register_moderation_handlers
from .game_handlers import register_game_handlers
from .rank_handlers import register_rank_handlers

def register_all_handlers(application, db, customizer):
    """Register all handlers"""
    register_media_handlers(application, db, customizer)
    register_command_handlers(application, db, customizer)
    register_settings_handlers(application, db, customizer)
    register_moderation_handlers(application, db, customizer)
    register_game_handlers(application, db, customizer)
    register_rank_handlers(application, db, customizer)
