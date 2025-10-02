from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu"""
    chat_id = update.effective_chat.id
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    is_admin_user = await is_admin(update, context)
    
    keyboard = [
        [InlineKeyboardButton("🛠️ Feature Toggles", callback_data="settings_features")],
        [InlineKeyboardButton("💬 Custom Responses", callback_data="settings_responses")],
        [InlineKeyboardButton("🎮 Game Settings", callback_data="settings_games")],
        [InlineKeyboardButton("🖼️ Media Settings", callback_data="settings_media")],
    ]
    
    if is_admin_user:
        keyboard.append([InlineKeyboardButton("🔧 Admin Settings", callback_data="settings_admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚙️ <b>Bot Settings Menu</b>\n\n"
        "Customize every aspect of the bot to your liking!",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def feature_toggle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle specific feature"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only admins can toggle features")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /toggle <feature> <on/off>\n\n"
            "Available features:\n"
            "• anti_spam - Anti-spam protection\n"
            "• welcome_message - Welcome new users\n"
            "• ranking_system - XP and level system\n"
            "• truth_or_dare - Truth or Dare game\n"
            "• word_games - Word games\n"
            "• meme - Meme commands\n"
            "• video - Video commands\n"
            "• gif - GIF commands\n"
            "• sticker - Sticker commands\n"
            "• rank_system - Rank system\n"
            "• daily_rewards - Daily bonuses"
        )
        return
    
    feature = context.args[0].lower()
    state = context.args[1].lower()
    
    if state not in ['on', 'off', 'true', 'false', '1', '0']:
        await update.message.reply_text("❌ Invalid state. Use 'on' or 'off'")
        return
    
    enabled = state in ['on', 'true', '1']
    chat_id = update.effective_chat.id
    customizer = context.bot_data['customizer']
    
    await customizer.toggle_feature(chat_id, feature, enabled)
    
    status = "✅ enabled" if enabled else "❌ disabled"
    await update.message.reply_text(f"Feature '{feature}' has been {status}")

async def set_welcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set custom welcome message"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only admins can set welcome messages")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /set_welcome <message>\n\n"
            "Available variables:\n"
            "{name} - User's first name\n"
            "{username} - User's username\n"
            "{chat} - Chat title\n"
            "{mention} - Mention the user\n\n"
            "Example: /set_welcome 👋 Welcome {name} to {chat}! Enjoy your stay! 🎉"
        )
        return
    
    welcome_message = " ".join(context.args)
    chat_id = update.effective_chat.id
    customizer = context.bot_data['customizer']
    
    await customizer.set_welcome_message(chat_id, welcome_message)
    await update.message.reply_text("✅ Welcome message updated!")

async def add_custom_response_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add custom response"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only admins can add custom responses")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /add_response <trigger> <response>\n\n"
            "Example: /add_response hello Hey there! How can I help? 👋"
        )
        return
    
    trigger = context.args[0].lower()
    response = " ".join(context.args[1:])
    chat_id = update.effective_chat.id
    customizer = context.bot_data['customizer']
    
    await customizer.add_custom_response(chat_id, trigger, response)
    await update.message.reply_text(f"✅ Custom response added for '{trigger}'")

async def add_custom_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add custom command"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only admins can add custom commands")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /add_command <command_name> <response>\n\n"
            "Example: /add_command rules Please read our rules in the pinned message! 📜"
        )
        return
    
    command_name = context.args[0].lower()
    response = " ".join(context.args[1:])
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    db = context.bot_data['db']
    
    if command_name.startswith('/'):
        command_name = command_name[1:]
    
    await db.add_custom_command(chat_id, command_name, response, user_id)
    await update.message.reply_text(f"✅ Custom command '/{command_name}' added!")

async def settings_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings callback queries"""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    data = query.data
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    if data == "settings_features":
        await show_feature_settings(query, chat_id, db, customizer)
    elif data.startswith("toggle_"):
        feature = data.replace("toggle_", "")
        await toggle_feature_callback(query, chat_id, feature, db, customizer)
    elif data == "settings_back":
        await settings_command(update, context)

async def show_feature_settings(query, chat_id, db, customizer):
    """Show feature toggle settings"""
    chat_settings = await db.get_chat_settings(chat_id)
    enabled_features = chat_settings['enabled_features']
    
    keyboard = []
    for feature, enabled in enabled_features.items():
        status = "✅" if enabled else "❌"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {feature.replace('_', ' ').title()}",
                callback_data=f"toggle_{feature}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="settings_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🛠️ <b>Feature Settings</b>\n\n"
        "Toggle features on/off by clicking them:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def toggle_feature_callback(query, chat_id, feature, db, customizer):
    """Toggle feature from callback"""
    chat_settings = await db.get_chat_settings(chat_id)
    current_state = chat_settings['enabled_features'].get(feature, True)
    
    await customizer.toggle_feature(chat_id, feature, not current_state)
    
    await show_feature_settings(query, chat_id, db, customizer)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is admin"""
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except:
        return False

def register_settings_handlers(application, db, customizer):
    """Register settings handlers"""
    application.bot_data['db'] = db
    application.bot_data['customizer'] = customizer
    
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("toggle", feature_toggle_command))
    application.add_handler(CommandHandler("set_welcome", set_welcome_command))
    application.add_handler(CommandHandler("add_response", add_custom_response_command))
    application.add_handler(CommandHandler("add_command", add_custom_command_handler))
    
    application.add_handler(CallbackQueryHandler(settings_callback_handler, pattern="^settings_"))
    application.add_handler(CallbackQueryHandler(settings_callback_handler, pattern="^toggle_"))
