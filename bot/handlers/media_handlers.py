from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import aiosqlite

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is admin - AUTO DETECT"""
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except:
        return False

async def is_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is owner/creator"""
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status == 'creator'
    except:
        return False

async def add_media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add media to bot"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /add_media <type> <category> [tags...]\n\n"
            "Types: sticker, gif, meme, video\n"
            "Reply to a media message with this command\n\n"
            "Example: /add_media gif funny happy celebration"
        )
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Please reply to a media message")
        return
    
    media_type = context.args[0].lower()
    category = context.args[1] if len(context.args) > 1 else "general"
    tags = context.args[2:] if len(context.args) > 2 else []
    
    file_id = None
    replied_message = update.message.reply_to_message
    
    if media_type == 'sticker' and replied_message.sticker:
        file_id = replied_message.sticker.file_id
    elif media_type == 'gif' and replied_message.animation:
        file_id = replied_message.animation.file_id
    elif media_type == 'meme' and replied_message.photo:
        file_id = replied_message.photo[-1].file_id
    elif media_type == 'video' and replied_message.video:
        file_id = replied_message.video.file_id
    else:
        await update.message.reply_text("❌ Unsupported media type or no media found")
        return
    
    await db.add_media(user_id, media_type, file_id, tags, category)
    
    tag_text = f" with tags: {', '.join(tags)}" if tags else ""
    await update.message.reply_text(f"✅ {media_type.title()} added to {category} category{tag_text}")

async def send_sticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send random sticker"""
    chat_id = update.effective_chat.id
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    if not await customizer.get_feature_status(chat_id, 'sticker'):
        await update.message.reply_text("❌ Sticker feature is disabled")
        return
    
    category = context.args[0] if context.args else None
    tags = context.args[1:] if context.args else None
    
    sticker = await db.get_random_media('sticker', category, tags)
    
    if sticker:
        await update.message.reply_sticker(sticker['file_id'])
        async with aiosqlite.connect(db.db_path) as conn:
            await conn.execute(
                'UPDATE media_storage SET usage_count = usage_count + 1 WHERE media_id = ?',
                (sticker['media_id'],)
            )
            await conn.commit()
    else:
        await update.message.reply_text("❌ No stickers found with those filters")

async def send_gif_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send random GIF"""
    chat_id = update.effective_chat.id
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    if not await customizer.get_feature_status(chat_id, 'gif'):
        await update.message.reply_text("❌ GIF feature is disabled")
        return
    
    category = context.args[0] if context.args else None
    tags = context.args[1:] if context.args else None
    
    gif = await db.get_random_media('gif', category, tags)
    
    if gif:
        await update.message.reply_animation(gif['file_id'])
        async with aiosqlite.connect(db.db_path) as conn:
            await conn.execute(
                'UPDATE media_storage SET usage_count = usage_count + 1 WHERE media_id = ?',
                (gif['media_id'],)
            )
            await conn.commit()
    else:
        await update.message.reply_text("❌ No GIFs found with those filters")

async def send_meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send random meme"""
    chat_id = update.effective_chat.id
    db = context.bot_data['db']
    customizer = context.bot_data['customizer']
    
    if not await customizer.get_feature_status(chat_id, 'meme'):
        await update.message.reply_text("❌ Meme feature is disabled")
        return
    
    category = context.args[0] if context.args else None
    tags = context.args[1:] if context.args else None
    
    meme = await db.get_random_media('meme', category, tags)
    
    if meme:
        await update.message.reply_photo(meme['file_id'])
        async with aiosqlite.connect(db.db_path) as conn:
            await conn.execute(
                'UPDATE media_storage SET usage_count = usage_count + 1 WHERE media_id = ?',
                (meme['media_id'],)
            )
            await conn.commit()
    else:
        await update.message.reply_text("❌ No memes found with those filters")

async def my_media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's media"""
    user_id = update.effective_user.id
    db = context.bot_data['db']
    media_type = context.args[0] if context.args else None
    
    media_list = await db.get_user_media(user_id, media_type)
    
    if not media_list:
        type_text = f" {media_type}" if media_type else ""
        await update.message.reply_text(f"📭 You haven't added any{type_text} media yet!")
        return
    
    media_by_type = {}
    for media in media_list:
        if media['media_type'] not in media_by_type:
            media_by_type[media['media_type']] = {}
        if media['category'] not in media_by_type[media['media_type']]:
            media_by_type[media['media_type']][media['category']] = 0
        media_by_type[media['media_type']][media['category']] += 1
    
    response = ["📁 <b>Your Media Library</b>\n"]
    for media_type, categories in media_by_type.items():
        response.append(f"\n{media_type.upper()}:")
        for category, count in categories.items():
            response.append(f"  • {category}: {count} items")
    
    response.append("\nUse /sticker, /gif, or /meme to get random media")
    await update.message.reply_text("\n".join(response), parse_mode='HTML')

def register_media_handlers(application, db, customizer):
    """Register media handlers"""
    application.bot_data['db'] = db
    application.bot_data['customizer'] = customizer
    
    application.add_handler(CommandHandler("add_media", add_media_command))
    application.add_handler(CommandHandler("sticker", send_sticker_command))
    application.add_handler(CommandHandler("gif", send_gif_command))
    application.add_handler(CommandHandler("meme", send_meme_command))
    application.add_handler(CommandHandler("my_media", my_media_command))
