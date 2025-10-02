import math
from typing import Dict, Any
from datetime import datetime

class RankSystem:
    def __init__(self, database):
        self.db = database
    
    def generate_progress_bar(self, current: int, total: int, length: int = 20) -> str:
        """Generate visual progress bar"""
        percentage = min(100, (current / total) * 100)
        filled = round(percentage / 100 * length)
        return f"┃{'█' * filled}{'━' * (length - filled)}┃ {percentage:.1f}%"
    
    def get_level_requirements(self, level: int) -> int:
        """Calculate XP needed for level"""
        return level * 1000
    
    def get_prestige_icon(self, prestige: int) -> str:
        """Get prestige icon"""
        icons = ["⭐", "🌟", "💫", "✨", "🔥", "⚡", "🎯", "🏆", "👑", "💎"]
        return icons[min(prestige, len(icons) - 1)]
    
    def generate_rank_card(self, user_data: Dict, rank_data: Dict, rank_position: int, 
                          chat_settings: Dict) -> str:
        """Generate beautiful rank card"""
        
        username = user_data.get('username', 'Unknown')
        name = user_data.get('first_name', 'User')
        level = rank_data['level']
        xp = rank_data['xp']
        prestige = rank_data.get('prestige', 0)
        daily_streak = rank_data.get('daily_streak', 0)
        messages_count = rank_data.get('messages_count', 0)
        
        xp_needed = self.get_level_requirements(level)
        xp_current = xp
        xp_next = xp_needed
        
        progress_percentage = min(100, (xp_current / xp_next) * 100)
        progress_bar = self.generate_progress_bar(xp_current, xp_next)
        
        prestige_icon = self.get_prestige_icon(prestige)
        
        card_style = rank_data.get('rank_card_style', 'default')
        
        if card_style == 'minimal':
            return self._minimal_rank_card(name, username, level, rank_position, xp_current, xp_next, 
                                         progress_bar, prestige_icon, daily_streak)
        elif card_style == 'detailed':
            return self._detailed_rank_card(name, username, level, rank_position, xp_current, xp_next,
                                          progress_bar, prestige_icon, daily_streak, messages_count)
        else:
            return self._default_rank_card(name, username, level, rank_position, xp_current, xp_next,
                                         progress_bar, prestige_icon, daily_streak, messages_count)
    
    def _default_rank_card(self, name: str, username: str, level: int, rank: int, 
                          xp_current: int, xp_next: int, progress_bar: str,
                          prestige_icon: str, daily_streak: int, messages_count: int) -> str:
        return f"""
{prestige_icon} <b>LEVEL {level}</b> {prestige_icon}

🏆 <b>RANK #{rank}</b>

<b>{name}</b>
@{username}

📊 <b>PROGRESS</b>
{xp_current} / {xp_next} XP
{progress_bar}

🔥 <b>Daily Streak:</b> {daily_streak} days
💬 <b>Messages:</b> {messages_count}

⏰ <i>Last active: {datetime.now().strftime('%H:%M')}</i>
"""
    
    def _minimal_rank_card(self, name: str, username: str, level: int, rank: int,
                          xp_current: int, xp_next: int, progress_bar: str,
                          prestige_icon: str, daily_streak: int) -> str:
        return f"""
{prestige_icon} <b>LEVEL {level}</b> • <b>RANK #{rank}</b> {prestige_icon}

<b>{name}</b> • @{username}

{progress_bar}
{xp_current}/{xp_next} XP

🔥 {daily_streak} days
"""
    
    def _detailed_rank_card(self, name: str, username: str, level: int, rank: int,
                           xp_current: int, xp_next: int, progress_bar: str,
                           prestige_icon: str, daily_streak: int, messages_count: int) -> str:
        return f"""
┌────────────────────────┐
│    {prestige_icon} <b>RANK CARD</b> {prestige_icon}    │
├────────────────────────┤
│ <b>LEVEL</b> {level:>15} │
│ <b>RANK</b> #{rank:>16} │
├────────────────────────┤
│ <b>{name}</b> │
│ @{username:>19} │
├────────────────────────┤
│ {progress_bar:>22} │
│ {xp_current:>6} / {xp_next:>6} XP │
├────────────────────────┤
│ 🔥 Streak: {daily_streak:>11} │
│ 💬 Msgs: {messages_count:>12} │
└────────────────────────┘
"""
    
    async def calculate_level_up(self, user_id: int, chat_id: int, xp_to_add: int) -> Dict[str, Any]:
        """Calculate level up and return results"""
        rank_data = await self.db.get_user_rank(user_id, chat_id)
        old_level = rank_data['level']
        
        rank_data['xp'] += xp_to_add
        
        levels_gained = 0
        xp_needed = self.get_level_requirements(rank_data['level'])
        
        while rank_data['xp'] >= xp_needed:
            rank_data['level'] += 1
            rank_data['xp'] -= xp_needed
            levels_gained += 1
            xp_needed = self.get_level_requirements(rank_data['level'])
        
        if levels_gained > 0:
            await self.db.save_user_rank(user_id, chat_id, rank_data)
        
        return {
            'levels_gained': levels_gained,
            'new_level': rank_data['level'],
            'old_level': old_level,
            'current_xp': rank_data['xp'],
            'next_level_xp': self.get_level_requirements(rank_data['level'])
  }
