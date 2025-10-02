from typing import Dict, Any, Optional, List
from bot.database import BotDatabase

class CustomizationSystem:
    def __init__(self, database: BotDatabase):
        self.db = database
    
    async def get_feature_status(self, chat_id: int, feature: str) -> bool:
        """Check if feature is enabled"""
        chat_settings = await self.db.get_chat_settings(chat_id)
        return chat_settings['enabled_features'].get(feature, True)
    
    async def toggle_feature(self, chat_id: int, feature: str, enabled: bool):
        """Toggle feature on/off"""
        chat_settings = await self.db.get_chat_settings(chat_id)
        chat_settings['enabled_features'][feature] = enabled
        await self.db.save_chat_settings(chat_id, chat_settings)
    
    async def set_chat_setting(self, chat_id: int, setting_key: str, setting_value: Any):
        """Set chat setting"""
        chat_settings = await self.db.get_chat_settings(chat_id)
        chat_settings['settings'][setting_key] = setting_value
        await self.db.save_chat_settings(chat_id, chat_settings)
    
    async def get_chat_setting(self, chat_id: int, setting_key: str, default: Any = None):
        """Get chat setting"""
        chat_settings = await self.db.get_chat_settings(chat_id)
        return chat_settings['settings'].get(setting_key, default)
    
    async def add_custom_response(self, chat_id: int, trigger: str, response: str):
        """Add custom response"""
        chat_settings = await self.db.get_chat_settings(chat_id)
        chat_settings['custom_responses'][trigger.lower()] = response
        await self.db.save_chat_settings(chat_id, chat_settings)
    
    async def get_custom_response(self, chat_id: int, trigger: str) -> Optional[str]:
        """Get custom response"""
        chat_settings = await self.db.get_chat_settings(chat_id)
        return chat_settings['custom_responses'].get(trigger.lower())
    
    async def add_banned_word(self, chat_id: int, word: str):
        """Add banned word"""
        chat_settings = await self.db.get_chat_settings(chat_id)
        if word.lower() not in chat_settings['banned_words']:
            chat_settings['banned_words'].append(word.lower())
            await self.db.save_chat_settings(chat_id, chat_settings)
    
    async def remove_banned_word(self, chat_id: int, word: str):
        """Remove banned word"""
        chat_settings = await self.db.get_chat_settings(chat_id)
        if word.lower() in chat_settings['banned_words']:
            chat_settings['banned_words'].remove(word.lower())
            await self.db.save_chat_settings(chat_id, chat_settings)
    
    async def get_banned_words(self, chat_id: int) -> List[str]:
        """Get all banned words"""
        chat_settings = await self.db.get_chat_settings(chat_id)
        return chat_settings['banned_words']
    
    async def is_word_banned(self, chat_id: int, word: str) -> bool:
        """Check if word is banned"""
        banned_words = await self.get_banned_words(chat_id)
        return word.lower() in banned_words
    
    async def set_welcome_message(self, chat_id: int, message: str):
        """Set welcome message"""
        await self.set_chat_setting(chat_id, 'welcome_message', message)
    
    async def set_goodbye_message(self, chat_id: int, message: str):
        """Set goodbye message"""
        await self.set_chat_setting(chat_id, 'goodbye_message', message)
    
    async def set_rules(self, chat_id: int, rules: str):
        """Set group rules"""
        await self.set_chat_setting(chat_id, 'rules', rules)
