from telegram.ext import CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
import random

async def truth_or_dare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start Truth or Dare game"""
    chat_id = update.effective_chat.id
    customizer = context.bot_data['customizer']
    
    if not await customizer.get_feature_status(chat_id, 'truth_or_dare'):
        await update.message.reply_text("❌ Truth or Dare is disabled in this chat!")
        return
    
    truths = [
        "What's your most embarrassing moment?",
        "Have you ever cheated in an exam?",
        "What's the weirdest thing you've ever eaten?",
        "What's your biggest fear?",
        "What's the most trouble you've ever been in?",
        "What's something you're glad your parents never found out about?",
        "What's the biggest lie you've ever told?",
        "What's the most embarrassing thing in your search history?"
    ]
    
    dares = [
        "Send a voice message singing for 30 seconds",
        "Post a childhood photo in this chat",
        "Text your crush right now and screenshot it",
        "Do 20 pushups right now",
        "Send the last photo in your gallery",
        "Call a random contact and sing happy birthday",
        "Wear your clothes inside out for 1 hour",
        "Speak in an accent for the next 10 messages"
    ]
    
    choice = random.choice(['truth', 'dare'])
    
    if choice == 'truth':
        question = random.choice(truths)
        await update.message.reply_text(
            f"🔮 <b>TRUTH for {update.effective_user.first_name}:</b>\n\n"
            f"{question}\n\n"
            f"Reply with your answer! ✅",
            parse_mode='HTML'
        )
    else:
        dare = random.choice(dares)
        await update.message.reply_text(
            f"🎯 <b>DARE for {update.effective_user.first_name}:</b>\n\n"
            f"{dare}\n\n"
            f"Complete the dare and send proof! 📸",
            parse_mode='HTML'
        )

async def word_game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start word game"""
    chat_id = update.effective_chat.id
    customizer = context.bot_data['customizer']
    
    if not await customizer.get_feature_status(chat_id, 'word_games'):
        await update.message.reply_text("❌ Word games are disabled in this chat!")
        return
    
    word_bank = [
        {'word': 'algorithm', 'hint': 'A step-by-step procedure for calculations'},
        {'word': 'blockchain', 'hint': 'Decentralized digital ledger technology'},
        {'word': 'nebulous', 'hint': 'Vague or ill-defined'},
        {'word': 'quantum', 'hint': 'Relating to quantum mechanics'},
        {'word': 'symphony', 'hint': 'An elaborate musical composition'},
        {'word': 'kaleidoscope', 'hint': 'A constantly changing pattern'},
        {'word': 'pneumonia', 'hint': 'A lung inflammation condition'}
    ]
    
    word_data = random.choice(word_bank)
    scrambled = ''.join(random.sample(word_data['word'], len(word_data['word'])))
    
    await update.message.reply_text(
        "🧩 <b>New Word Game Started!</b>\n\n"
        f"<b>Scrambled:</b> {scrambled}\n"
        f"<b>Hint:</b> {word_data['hint']}\n\n"
        "Type the correct word in chat! 🎯",
        parse_mode='HTML'
    )

def register_game_handlers(application, db, customizer):
    """Register game handlers"""
    application.bot_data['db'] = db
    application.bot_data['customizer'] = customizer
    
    application.add_handler(CommandHandler("truthordare", truth_or_dare_command))
    application.add_handler(CommandHandler("wordgame", word_game_command))
