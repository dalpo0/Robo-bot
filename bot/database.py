import json
import aiosqlite
from typing import Dict, List, Any, Optional
from datetime import datetime

class BotDatabase:
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        
    async def initialize(self):
        """Initialize database tables with ALL features"""
        async with aiosqlite.connect(self.db_path) as db:
            # User settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    preferred_language TEXT DEFAULT 'en',
                    custom_commands TEXT DEFAULT '{}',
                    theme TEXT DEFAULT 'default',
                    notification_preferences TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Chat settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS chat_settings (
                    chat_id INTEGER PRIMARY KEY,
                    chat_title TEXT,
                    settings TEXT DEFAULT '{}',
                    custom_responses TEXT DEFAULT '{}',
                    enabled_features TEXT DEFAULT '{}',
                    banned_words TEXT DEFAULT '[]',
                    welcome_message TEXT DEFAULT '👋 Welcome {name} to {chat}!',
                    goodbye_message TEXT DEFAULT '👋 Goodbye {name}! We''ll miss you!',
                    rules TEXT DEFAULT 'Be respectful to everyone!',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Global settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS global_settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Media storage table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS media_storage (
                    media_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    media_type TEXT,
                    file_id TEXT,
                    tags TEXT,
                    category TEXT,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Custom commands table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS custom_commands (
                    command_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    command_name TEXT,
                    command_response TEXT,
                    created_by INTEGER,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Warnings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    warning_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    user_id INTEGER,
                    reason TEXT,
                    warned_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User data table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_data (
                    user_id INTEGER,
                    chat_id INTEGER,
                    data_type TEXT,
                    data_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, chat_id, data_type)
                )
            ''')
            
            # Game data table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS game_data (
                    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    game_type TEXT,
                    game_state TEXT,
                    players TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Rank system table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_ranks (
                    user_id INTEGER,
                    chat_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    messages_count INTEGER DEFAULT 0,
                    daily_streak INTEGER DEFAULT 0,
                    last_active DATE,
                    rank_card_style TEXT DEFAULT 'default',
                    prestige INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, chat_id)
                )
            ''')
            
            await db.commit()
    
    # User settings methods
    async def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            
            if row:
                settings = dict(row)
                for key in ['custom_commands', 'notification_preferences']:
                    if settings[key]:
                        settings[key] = json.loads(settings[key])
                return settings
            else:
                default_settings = {
                    'user_id': user_id,
                    'username': '',
                    'preferred_language': 'en',
                    'custom_commands': {},
                    'theme': 'default',
                    'notification_preferences': {
                        'game_notifications': True,
                        'rank_updates': True,
                        'daily_rewards': True
                    }
                }
                await self.save_user_settings(user_id, default_settings)
                return default_settings
    
    async def save_user_settings(self, user_id: int, settings: Dict[str, Any]):
        async with aiosqlite.connect(self.db_path) as db:
            settings_copy = settings.copy()
            for key in ['custom_commands', 'notification_preferences']:
                if key in settings_copy:
                    settings_copy[key] = json.dumps(settings_copy[key])
            
            await db.execute('''
                INSERT OR REPLACE INTO user_settings 
                (user_id, username, preferred_language, custom_commands, theme, notification_preferences)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                settings_copy.get('username', ''),
                settings_copy.get('preferred_language', 'en'),
                settings_copy.get('custom_commands', '{}'),
                settings_copy.get('theme', 'default'),
                settings_copy.get('notification_preferences', '{}')
            ))
            await db.commit()
    
    # Chat settings methods
    async def get_chat_settings(self, chat_id: int) -> Dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM chat_settings WHERE chat_id = ?', (chat_id,))
            row = await cursor.fetchone()
            
            if row:
                settings = dict(row)
                for key in ['settings', 'custom_responses', 'enabled_features', 'banned_words']:
                    if settings[key]:
                        settings[key] = json.loads(settings[key])
                return settings
            else:
                default_settings = {
                    'chat_id': chat_id,
                    'chat_title': '',
                    'settings': {
                        'welcome_message': "👋 Welcome {name} to {chat}!",
                        'goodbye_message': "👋 Goodbye {name}! We'll miss you!",
                        'rules': "Be respectful to everyone!",
                        'max_warnings': 3,
                        'flood_limit': 5,
                        'flood_window': 10,
                        'mute_duration': 5,
                        'xp_per_message': 10,
                        'xp_per_level': 1000,
                        'daily_bonus_xp': 50
                    },
                    'custom_responses': {},
                    'enabled_features': {
                        'anti_spam': True, 'auto_mute': True, 'keyword_filter': True,
                        'flood_control': True, 'welcome_message': True, 'meme': True,
                        'video': True, 'greet_users': True, 'anti_link': True,
                        'report_system': True, 'message_counter': True, 'random_emoji': True,
                        'ranking_system': True, 'truth_or_dare': True, 'word_games': True,
                        'sticker_packs': True, 'gif_sharing': True, 'custom_commands': True,
                        'auto_detect_admins': True, 'owner_controls': True,
                        'rank_system': True, 'daily_rewards': True
                    },
                    'banned_words': ["badword1", "badword2", "spam"]
                }
                await self.save_chat_settings(chat_id, default_settings)
                return default_settings
    
    async def save_chat_settings(self, chat_id: int, settings: Dict[str, Any]):
        async with aiosqlite.connect(self.db_path) as db:
            settings_copy = settings.copy()
            for key in ['settings', 'custom_responses', 'enabled_features', 'banned_words']:
                if key in settings_copy:
                    settings_copy[key] = json.dumps(settings_copy[key])
            
            await db.execute('''
                INSERT OR REPLACE INTO chat_settings 
                (chat_id, chat_title, settings, custom_responses, enabled_features, banned_words, welcome_message, goodbye_message, rules)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                chat_id,
                settings_copy.get('chat_title', ''),
                settings_copy.get('settings', '{}'),
                settings_copy.get('custom_responses', '{}'),
                settings_copy.get('enabled_features', '{}'),
                settings_copy.get('banned_words', '[]'),
                settings_copy.get('welcome_message', '👋 Welcome {name} to {chat}!'),
                settings_copy.get('goodbye_message', '👋 Goodbye {name}! We\'ll miss you!'),
                settings_copy.get('rules', 'Be respectful to everyone!')
            ))
            await db.commit()
    
    # Rank system methods
    async def get_user_rank(self, user_id: int, chat_id: int) -> Dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM user_ranks WHERE user_id = ? AND chat_id = ?',
                (user_id, chat_id)
            )
            row = await cursor.fetchone()
            
            if row:
                return dict(row)
            else:
                default_rank = {
                    'user_id': user_id,
                    'chat_id': chat_id,
                    'xp': 0,
                    'level': 1,
                    'messages_count': 0,
                    'daily_streak': 0,
                    'last_active': datetime.now().date().isoformat(),
                    'rank_card_style': 'default',
                    'prestige': 0
                }
                await self.save_user_rank(user_id, chat_id, default_rank)
                return default_rank
    
    async def save_user_rank(self, user_id: int, chat_id: int, rank_data: Dict[str, Any]):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO user_ranks 
                (user_id, chat_id, xp, level, messages_count, daily_streak, last_active, rank_card_style, prestige)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                chat_id,
                rank_data['xp'],
                rank_data['level'],
                rank_data['messages_count'],
                rank_data['daily_streak'],
                rank_data['last_active'],
                rank_data['rank_card_style'],
                rank_data['prestige']
            ))
            await db.commit()
    
    async def add_user_xp(self, user_id: int, chat_id: int, xp: int):
        rank_data = await self.get_user_rank(user_id, chat_id)
        rank_data['xp'] += xp
        rank_data['messages_count'] += 1
        rank_data['last_active'] = datetime.now().date().isoformat()
        
        xp_needed = rank_data['level'] * 1000
        if rank_data['xp'] >= xp_needed:
            rank_data['level'] += 1
            rank_data['xp'] = rank_data['xp'] - xp_needed
        
        await self.save_user_rank(user_id, chat_id, rank_data)
        return rank_data
    
    async def get_leaderboard(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT * FROM user_ranks 
                WHERE chat_id = ? 
                ORDER BY level DESC, xp DESC, messages_count DESC
                LIMIT ?
            ''', (chat_id, limit))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_user_rank_position(self, user_id: int, chat_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT COUNT(*) + 1 as position
                FROM user_ranks 
                WHERE chat_id = ? AND (level > (SELECT level FROM user_ranks WHERE user_id = ? AND chat_id = ?)
                    OR (level = (SELECT level FROM user_ranks WHERE user_id = ? AND chat_id = ?) 
                    AND xp > (SELECT xp FROM user_ranks WHERE user_id = ? AND chat_id = ?)))
            ''', (chat_id, user_id, chat_id, user_id, chat_id, user_id, chat_id))
            
            row = await cursor.fetchone()
            return row[0] if row else 1
    
    async def update_daily_streak(self, user_id: int, chat_id: int):
        rank_data = await self.get_user_rank(user_id, chat_id)
        today = datetime.now().date()
        last_active = datetime.fromisoformat(rank_data['last_active']).date()
        
        if last_active == today:
            return rank_data['daily_streak']
        
        if (today - last_active).days == 1:
            rank_data['daily_streak'] += 1
        else:
            rank_data['daily_streak'] = 1
        
        rank_data['last_active'] = today.isoformat()
        await self.save_user_rank(user_id, chat_id, rank_data)
        return rank_data['daily_streak']
    
    # Media methods
    async def add_media(self, user_id: int, media_type: str, file_id: str, 
                       tags: List[str] = None, category: str = "general"):
        async with aiosqlite.connect(self.db_path) as db:
            tags_json = json.dumps(tags or [])
            await db.execute('''
                INSERT INTO media_storage 
                (user_id, media_type, file_id, tags, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, media_type, file_id, tags_json, category))
            await db.commit()
    
    async def get_random_media(self, media_type: str, category: str = None, 
                              tags: List[str] = None) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT * FROM media_storage WHERE media_type = ?'
            params = [media_type]
            
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            if tags:
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append('tags LIKE ?')
                    params.append(f'%"{tag}"%')
                query += ' AND (' + ' OR '.join(tag_conditions) + ')'
            
            query += ' ORDER BY RANDOM() LIMIT 1'
            cursor = await db.execute(query, params)
            row = await cursor.fetchone()
            
            if row:
                media = dict(row)
                media['tags'] = json.loads(media['tags']) if media['tags'] else []
                return media
            return None
    
    async def get_user_media(self, user_id: int, media_type: str = None) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if media_type:
                cursor = await db.execute(
                    'SELECT * FROM media_storage WHERE user_id = ? AND media_type = ?',
                    (user_id, media_type)
                )
            else:
                cursor = await db.execute(
                    'SELECT * FROM media_storage WHERE user_id = ?',
                    (user_id,)
                )
            
            rows = await cursor.fetchall()
            media_list = []
            for row in rows:
                media = dict(row)
                media['tags'] = json.loads(media['tags']) if media['tags'] else []
                media_list.append(media)
            return media_list
    
    # Custom commands methods
    async def add_custom_command(self, chat_id: int, command_name: str, 
                               command_response: str, created_by: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO custom_commands 
                (chat_id, command_name, command_response, created_by)
                VALUES (?, ?, ?, ?)
            ''', (chat_id, command_name, command_response, created_by))
            await db.commit()
    
    async def get_custom_commands(self, chat_id: int) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM custom_commands WHERE chat_id = ?',
                (chat_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def increment_command_usage(self, command_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE custom_commands SET usage_count = usage_count + 1 WHERE command_id = ?',
                (command_id,)
            )
            await db.commit()
    
    # Warnings methods
    async def add_warning(self, chat_id: int, user_id: int, reason: str, warned_by: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO warnings (chat_id, user_id, reason, warned_by)
                VALUES (?, ?, ?, ?)
            ''', (chat_id, user_id, reason, warned_by))
            await db.commit()
    
    async def get_user_warnings(self, chat_id: int, user_id: int) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM warnings WHERE chat_id = ? AND user_id = ? ORDER BY created_at DESC',
                (chat_id, user_id)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def clear_warnings(self, chat_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'DELETE FROM warnings WHERE chat_id = ? AND user_id = ?',
                (chat_id, user_id)
            )
            await db.commit()
    
    # Global settings methods
    async def get_global_setting(self, setting_key: str, default: Any = None) -> Any:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT setting_value FROM global_settings WHERE setting_key = ?',
                (setting_key,)
            )
            row = await cursor.fetchone()
            if row and row[0]:
                try:
                    return json.loads(row[0])
                except:
                    return row[0]
            return default
    
    async def set_global_setting(self, setting_key: str, setting_value: Any, description: str = ""):
        async with aiosqlite.connect(self.db_path) as db:
            value_json = json.dumps(setting_value) if not isinstance(setting_value, str) else setting_value
            await db.execute('''
                INSERT OR REPLACE INTO global_settings 
                (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            ''', (setting_key, value_json, description))
            await db.commit()
