"""
Vision Captioning Telegram Bot:
Bot will accept user uploaded images and provide a description for the uploaded image
"""
import logging

from app.common.config import ENV
from app.handler.ask_handler import ask_handler
from app.handler.image_handler import image_handler, summary_handler

from telegram import Update, BotCommand
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes):
    """Start the bot"""
    await update.message.reply_text(
        "*Vision Captioning Bot*\n\n"
        "Welcome! I can analyze images and generate captions, tags, and summaries for you.\n\n"
        "*What you can do:*\n"
        "- 📷 /image — Upload an image to get a caption & 3 tags describing that image\n"
        "- 📝 /summary — Get a short summary of your last image\n"
        "- ❓ /help — Get assistance\n\n"
        "Just send an image or use /image to get started 🚀",
        parse_mode="Markdown"
    )

async def help(update: Update, context: ContextTypes):
    """Assistance using the bot"""
    await update.message.reply_text(
        "*Vision Captioning Bot*\n\n"
        "Welcome! I can analyze images and generate captions, tags, and summaries for you.\n\n"
        "*What you can do:*\n"
        "- 📷 /image — Upload an image to get a caption & 3 tags describing that image\n"
        "- 📝 /summary — Get a short summary of your last image\n"
        "- ❓ /help — Get assistance\n\n"
        "Just send an image or use /image to get started 🚀",
        parse_mode="Markdown"
    )

async def post_init(application):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get Assistance"),
        # BotCommand("query", "Ask Questions about the 2026 HR Trends Survey!"),
        BotCommand("image", "Upload Image to get a Description!"),
        BotCommand("summary", "Short Summary of the last uploaded Image!")
    ]
    await application.bot.set_my_commands(commands)

def main() -> None:
    """Vision Captioning bot."""
    logger.info("Bot Started... Polling for new Msgs!")
    application = Application.builder().token(ENV.BOT_TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_handler))
    application.add_handler(CommandHandler("image", image_handler))
    application.add_handler(CommandHandler("summary", summary_handler))
 
    # /image — triggered when a photo is sent (with or without caption)
    application.add_handler(
        MessageHandler(
            filters.PHOTO & filters.CaptionRegex(r"^/image"),
            image_handler,
        )
    )
    # Fallback: any photo upload without the caption command still routes here
    application.add_handler(MessageHandler(filters.PHOTO, image_handler))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()