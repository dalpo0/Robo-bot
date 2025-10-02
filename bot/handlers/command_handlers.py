from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.rank_system import RankSystem

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        "🤖 <b>Fully Customizable Telegram Bot</b>\n\n"
        "I'm a completely customizable bot with:\n"
        "• 🎮 Games & Ranking System\n"
        "• 🛡️ Auto Moderation\n"  
        "• 🖼️ Media Library\n"
        "• ⚙️ Full Customization\n\n"
        "Use /commands to see all available commands!",
        parse_mode='HTML'
    )

async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available commands"""
    chat_id = update.effective_chat.id
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    is_admin_user = await is_admin(update, context)
    
    categories = {
        '⚙️ Customization': [
            ('settings', 'Bot settings menu'),
            ('toggle', 'Toggle features (admin)'),
            ('set_welcome', 'Set welcome message (admin)'),
            ('add_response', 'Add custom response (admin)'),
            ('add_command', 'Add custom command (admin)')
        ],
        '🖼️ Media': [
            ('add_media', 'Add sticker/GIF/meme/video'),
            ('my_media', 'Show your media library'),
            ('sticker', 'Send random sticker'),
            ('gif', 'Send random GIF'),
            ('meme', 'Send random meme')
        ],
        '🏆 Ranking': [
            ('rank', 'Show your rank card'),
            ('leaderboard', 'Show top users'),
            ('daily', 'Claim daily bonus'),
            ('rankstyle', 'Customize rank card')
        ],
        '🛡️ Moderation': [
            ('warn', 'Warn user (admin)'),
            ('warnings', 'Check your warnings'),
            ('ban_word', 'Add banned word (admin)'),
            ('unban_word', 'Remove banned word (admin)')
        ],
        'ℹ️ Info': [
            ('commands', 'Show this command list'),
            ('start', 'Start the bot'),
            ('dbstats', 'Database stats (admin)')
        ]
    }
    
    response = ["<b>📜 Available Commands</b>\n"]
    
    for category, commands in categories.items():
        response.append(f"\n<b>{category}</b>")
        for cmd, desc in commands:
            if cmd in ['toggle', 'set_welcome', 'add_response', 'add_command', 'dbstats', 'warn', 'ban_word', 'unban_word'] and not is_admin_user:
                continue
            response.append(f"• /{cmd} - {desc}")
    
    custom_commands = await db.get_custom_commands(chat_id)
    if custom_commands:
        response.append("\n<b>💬 Custom Commands</b>")
        for cmd in custom_commands[:5]:
            response.append(f"• /{cmd['command_name']}")
        if len(custom_commands) > 5:
            response.append(f"• ... and {len(custom_commands) - 5} more")
    
    await update.message.reply_html('\n'.join(response))

async def handle_message_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Give XP for messages"""
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    if not await customizer.get_feature_status(chat_id, 'rank_system'):
        return
    
    if update.message.text.startswith('/'):
        return
    
    chat_settings = await db.get_chat_settings(chat_id)
    xp_per_message = chat_settings['settings'].get('xp_per_message', 10)
    
    rank_system = RankSystem(db)
    level_up_info = await rank_system.calculate_level_up(user_id, chat_id, xp_per_message)
    
    if level_up_info['levels_gained'] > 0:
        await update.message.reply_text(
            f"🎉 <b>LEVEL UP!</b> {update.effective_user.first_name} reached level {level_up_info['new_level']}!",
            parse_mode='HTML'
        )

async def handle_custom_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom commands"""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text
    if not text.startswith('/'):
        return
    
    command = text[1:].split()[0].lower()
    chat_id = update.effective_chat.id
    db = context.bot_data['db']
    
    custom_commands = await db.get_custom_commands(chat_id)
    for cmd in custom_commands:
        if cmd['command_name'] == command:
            await update.message.reply_text(cmd['command_response'])
            await db.increment_command_usage(cmd['command_id'])
            return

async def handle_custom_responses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom responses"""
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    text = update.message.text.lower().strip()
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    response = await customizer.get_custom_response(chat_id, text)
    if response:
        await update.message.reply_text(response)
        return
    
    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(greet in text for greet in greetings):
        if await customizer.get_feature_status(chat_id, 'greet_users'):
            import random
            responses = [
                f"Hello {update.effective_user.first_name}! 👋",
                f"Hi there @{update.effective_user.username}!" if update.effective_user.username else "Hi there!",
                "Hey! How are you today?",
            ]
            await update.message.reply_text(random.choice(responses))

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is admin"""
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except:
        return False

def register_command_handlers(application, db, customizer):
    """Register command handlers"""
    application.bot_data['db'] = db
    application.bot_data['customizer'] = customizer
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("commands", show_commands))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_xp))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_responses))
    application.add_handler(MessageHandler(filters.COMMAND, handle_custom_commands))
