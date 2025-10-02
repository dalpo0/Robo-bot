from telegram.ext import CommandHandler, MessageHandler, filters
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from datetime import datetime, timedelta

async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Warn a user"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only admins can warn users")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /warn @username reason\n\n"
            "Example: /warn @john Spamming the chat"
        )
        return
    
    target_username = context.args[0].replace('@', '')
    reason = " ".join(context.args[1:])
    chat_id = update.effective_chat.id
    warner_id = update.effective_user.id
    db = context.bot_data['db']
    
    try:
        # Find user by username
        chat_member = None
        async for member in update.effective_chat.get_members():
            if member.user.username and member.user.username.lower() == target_username.lower():
                chat_member = member
                break
        
        if not chat_member:
            await update.message.reply_text("❌ User not found in this chat")
            return
        
        target_user_id = chat_member.user.id
        
        # Add warning
        await db.add_warning(chat_id, target_user_id, reason, warner_id)
        
        # Check warning count
        warnings = await db.get_user_warnings(chat_id, target_user_id)
        chat_settings = await db.get_chat_settings(chat_id)
        max_warnings = chat_settings['settings'].get('max_warnings', 3)
        
        await update.message.reply_text(
            f"⚠️ {chat_member.user.first_name} has been warned!\n"
            f"Reason: {reason}\n"
            f"Warnings: {len(warnings)}/{max_warnings}"
        )
        
        # Auto-mute if reached max warnings
        if len(warnings) >= max_warnings:
            mute_duration = chat_settings['settings'].get('mute_duration', 5)
            until_date = datetime.now() + timedelta(minutes=mute_duration)
            
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=target_user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            
            await update.message.reply_text(
                f"🔇 {chat_member.user.first_name} has been muted for {mute_duration} minutes "
                f"(reached {max_warnings} warnings)"
            )
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def warnings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check user warnings"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    db = context.bot_data['db']
    
    warnings = await db.get_user_warnings(chat_id, user_id)
    chat_settings = await db.get_chat_settings(chat_id)
    max_warnings = chat_settings['settings'].get('max_warnings', 3)
    
    if not warnings:
        await update.message.reply_text("✅ You have no warnings!")
        return
    
    warnings_text = f"⚠️ <b>Your Warnings</b> ({len(warnings)}/{max_warnings})\n\n"
    
    for i, warning in enumerate(warnings, 1):
        warnings_text += f"{i}. {warning['reason']}\n"
    
    await update.message.reply_text(warnings_text, parse_mode='HTML')

async def ban_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add banned word"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only admins can ban words")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban_word <word>")
        return
    
    word = context.args[0].lower()
    chat_id = update.effective_chat.id
    customizer = context.bot_data['customizer']
    
    await customizer.add_banned_word(chat_id, word)
    await update.message.reply_text(f"✅ Word '{word}' has been banned")

async def unban_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove banned word"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only admins can unban words")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban_word <word>")
        return
    
    word = context.args[0].lower()
    chat_id = update.effective_chat.id
    customizer = context.bot_data['customizer']
    
    await customizer.remove_banned_word(chat_id, word)
    await update.message.reply_text(f"✅ Word '{word}' has been unbanned")

async def handle_banned_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check for banned words in messages"""
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    if not await customizer.get_feature_status(chat_id, 'keyword_filter'):
        return
    
    if await is_admin(update, context):
        return
    
    text = update.message.text.lower()
    banned_words = await customizer.get_banned_words(chat_id)
    
    for banned_word in banned_words:
        if banned_word in text:
            try:
                await update.message.delete()
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⚠️ Message from {update.effective_user.first_name} contained banned content"
                )
                
                # Add warning
                await db.add_warning(chat_id, user_id, f"Used banned word: {banned_word}", context.bot.id)
                return
            except Exception as e:
                print(f"Error handling banned word: {e}")
            break

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is admin"""
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except:
        return False

def register_moderation_handlers(application, db, customizer):
    """Register moderation handlers"""
    application.bot_data['db'] = db
    application.bot_data['customizer'] = customizer
    
    application.add_handler(CommandHandler("warn", warn_command))
    application.add_handler(CommandHandler("warnings", warnings_command))
    application.add_handler(CommandHandler("ban_word", ban_word_command))
    application.add_handler(CommandHandler("unban_word", unban_word_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_banned_words))
