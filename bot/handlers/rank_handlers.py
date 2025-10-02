from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.rank_system import RankSystem

async def rank_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's rank card"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    if not await customizer.get_feature_status(chat_id, 'rank_system'):
        await update.message.reply_text("❌ Rank system is disabled in this chat!")
        return
    
    rank_data = await db.get_user_rank(user_id, chat_id)
    rank_position = await db.get_user_rank_position(user_id, chat_id)
    chat_settings = await db.get_chat_settings(chat_id)
    
    rank_system = RankSystem(db)
    user_info = {
        'username': update.effective_user.username or "Unknown",
        'first_name': update.effective_user.first_name
    }
    
    rank_card = rank_system.generate_rank_card(
        user_info, rank_data, rank_position, chat_settings
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="show_leaderboard"),
            InlineKeyboardButton("🎨 Customize", callback_data="rank_customize")
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="show_stats"),
            InlineKeyboardButton("🎯 Daily Bonus", callback_data="daily_bonus")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(rank_card, reply_markup=reply_markup, parse_mode='HTML')

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show chat leaderboard"""
    chat_id = update.effective_chat.id
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    if not await customizer.get_feature_status(chat_id, 'rank_system'):
        await update.message.reply_text("❌ Rank system is disabled in this chat!")
        return
    
    leaderboard = await db.get_leaderboard(chat_id, 10)
    
    if not leaderboard:
        await update.message.reply_text("📊 No rank data available yet!")
        return
    
    leaderboard_text = "🏆 <b>TOP 10 USERS</b> 🏆\n\n"
    
    for idx, user_data in enumerate(leaderboard, 1):
        try:
            user = await context.bot.get_chat_member(chat_id, user_data['user_id'])
            username = user.user.username or user.user.first_name
            level = user_data['level']
            xp = user_data['xp']
            
            medal = ["🥇", "🥈", "🥉"][idx-1] if idx <= 3 else f"{idx}."
            leaderboard_text += f"{medal} {username} - Level {level} ({xp} XP)\n"
        except:
            continue
    
    await update.message.reply_text(leaderboard_text, parse_mode='HTML')

async def daily_bonus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Claim daily bonus"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    if not await customizer.get_feature_status(chat_id, 'daily_rewards'):
        await update.message.reply_text("❌ Daily rewards are disabled in this chat!")
        return
    
    streak = await db.update_daily_streak(user_id, chat_id)
    chat_settings = await db.get_chat_settings(chat_id)
    bonus_xp = chat_settings['settings'].get('daily_bonus_xp', 50)
    
    streak_bonus = 0
    if streak >= 7:
        streak_bonus = 100
    elif streak >= 3:
        streak_bonus = 50
    
    total_xp = bonus_xp + streak_bonus
    
    level_up_info = await RankSystem(db).calculate_level_up(user_id, chat_id, total_xp)
    
    bonus_text = f"""
🎁 <b>DAILY BONUS CLAIMED!</b> 🎁

💰 <b>Base XP:</b> {bonus_xp}
🔥 <b>Streak Bonus:</b> {streak_bonus}
💎 <b>Total XP:</b> {total_xp}

📈 <b>Current Streak:</b> {streak} days
"""
    
    if level_up_info['levels_gained'] > 0:
        bonus_text += f"\n🎉 <b>LEVEL UP!</b> Reached level {level_up_info['new_level']}!"
    
    await update.message.reply_text(bonus_text, parse_mode='HTML')

async def rank_customize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Customize rank card appearance"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    db = context.bot_data['db']
    
    keyboard = [
        [
            InlineKeyboardButton("🎨 Default", callback_data="rank_style_default"),
            InlineKeyboardButton("📱 Minimal", callback_data="rank_style_minimal")
        ],
        [
            InlineKeyboardButton("📊 Detailed", callback_data="rank_style_detailed"),
            InlineKeyboardButton("🌈 Colorful", callback_data="rank_style_colorful")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="rank_back")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎨 <b>Rank Card Customization</b>\n\n"
        "Choose your preferred rank card style:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def rank_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle rank callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    db = context.bot_data['db']
    
    if data == "show_leaderboard":
        await leaderboard_command(update, context)
    elif data == "rank_customize":
        await rank_customize_command(update, context)
    elif data == "daily_bonus":
        await daily_bonus_command(update, context)
    elif data.startswith("rank_style_"):
        style = data.replace("rank_style_", "")
        await set_rank_style(user_id, chat_id, style, query, db)
    elif data == "rank_back":
        await rank_command(update, context)

async def set_rank_style(user_id: int, chat_id: int, style: str, query, db):
    """Set user's rank card style"""
    rank_data = await db.get_user_rank(user_id, chat_id)
    rank_data['rank_card_style'] = style
    await db.save_user_rank(user_id, chat_id, rank_data)
    
    await query.edit_message_text(
        f"✅ Rank card style set to: <b>{style.title()}</b>",
        parse_mode='HTML'
    )

def register_rank_handlers(application, db, customizer):
    """Register rank system handlers"""
    application.bot_data['db'] = db
    application.bot_data['customizer'] = customizer
    
    application.add_handler(CommandHandler("rank", rank_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(CommandHandler("daily", daily_bonus_command))
    application.add_handler(CommandHandler("rankstyle", rank_customize_command))
    application.add_handler(CallbackQueryHandler(rank_callback_handler, pattern="^(show_leaderboard|rank_customize|daily_bonus|rank_style_|rank_back)"))
