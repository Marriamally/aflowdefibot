import os
import logging
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration - UPDATE THESE WITH YOUR SOCIAL LINKS
CHANNEL_USERNAME = "@your_channel"  # Add @ prefix
GROUP_USERNAME = "@your_group"      # Add @ prefix
TWITTER_USERNAME = "your_twitter"   # Without @

# Your bot token (will be revoked later)
BOT_TOKEN = "7842425835:AAEsA64jHw3-tDecba9mdVB8pZ1eZV7_xYI"

# Conversation states
WALLET, CONFIRMATION = range(2)

# Generate fake Solscan transaction URL
def generate_random_solscan_url():
    """Create a fake Solscan transaction URL with random ID"""
    transaction_id = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    return f"https://solscan.io/tx/{transaction_id}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send instructions with social buttons"""
    keyboard = [
        [InlineKeyboardButton("📢 Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("👥 Group", url=f"https://t.me/{GROUP_USERNAME[1:]}")],
        [InlineKeyboardButton("🐦 Twitter", url=f"https://twitter.com/{TWITTER_USERNAME}")],
        [InlineKeyboardButton("✅ I've Joined", callback_data="joined")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎉 *Welcome to the SOL Airdrop Bot!*\n\n"
        "To claim your 1000 SOL:\n"
        "1️⃣ Join our channel\n"
        "2️⃣ Join our group\n"
        "3️⃣ Follow us on Twitter\n"
        "4️⃣ Submit your SOL wallet address\n\n"
        "Click ✅ after joining:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt for wallet address after joining"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💰 *Please send your SOL wallet address:*\n\n"
        "_(Any text will be accepted for testing)_",
        parse_mode="Markdown"
    )
    return WALLET

async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive wallet and send fake transaction"""
    wallet = update.message.text
    solscan_url = generate_random_solscan_url()
    
    await update.message.reply_text(
        f"🎉 *CONGRATULATIONS!*\n\n"
        "1000 SOL has been sent to your wallet!\n"
        "This is a test - no actual tokens were sent.\n\n"
        f"🔗 Transaction: [View on Solscan]({solscan_url})\n"
        "⏱ Estimated confirmation: 2 seconds\n\n"
        "Thank you for participating in our test airdrop!",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    
    # Log user data
    user = update.effective_user
    logger.info(
        f"New claim:\n"
        f"User: {user.full_name} (@{user.username})\n"
        f"Wallet: {wallet}\n"
        f"Solscan: {solscan_url}\n"
        f"---\n"
    )
    
    return CONFIRMATION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text("❌ Airdrop claim cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    """Run the bot"""
    # Create Application with hardcoded token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_join, pattern="^joined$"))

    # Deployment configuration for Render.com
    port = int(os.environ.get("PORT", 5000))
    render_external_host = os.getenv('RENDER_EXTERNAL_HOSTNAME')
    
    if render_external_host:
        # Running on Render - use webhook
        webhook_url = f"https://{render_external_host}/webhook"
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url,
            url_path="/webhook"
        )
        logger.info(f"Bot running in webhook mode: {webhook_url}")
    else:
        # Running locally - use polling
        application.run_polling()
        logger.info("Bot running in polling mode")

if __name__ == "__main__":
    main()
