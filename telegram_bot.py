import logging
from dotenv import load_dotenv
import os
load_dotenv()

from app.handlers.ask_handler import ask_handler
from app.handlers import image_handler
from llm_ground.image_describe import structure_describe_wt_photo

from telegram import ForceReply, Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Upload any Image!")

async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    photos = update.message.photo
    if not len(photos):
        await update.message.reply_text("Upload any Image!")
    
    # Selecting low res image to save tokens
    photo_id = photos[1].file_id
    file = await context.bot.get_file(photo_id)
    response = await structure_describe_wt_photo(file)
    # response = {
    #     'caption': "BYLD's Core Values: Building Leadership Through Inclusivity, Customer Centricity, and Agility",
    #     'tags': ['BYLD Leadership', 'Core Values', 'Inclusive Culture']
    # }
    if bool(response):
        await update.message.reply_html(
            text=(
                f"<b>Image Caption:</b>\n<code>{response["caption"]}</code>.\n\n"
                f"<b>Tags:</b>\n" + "\n".join(f"~ {tag}" for tag in response["tags"])
            )
        )
    else:
        await update.message.reply_text("Caption generation issue... Try again later!")

    
    
# async def images(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send a message when the command /start is issued."""
#     photos = update.message.photo

#     if not len(photos):
#         await update.message.reply_text("No Images uploaded!")
#     for p in photos:
#         await update.message.reply_photo(p.file_id, caption=)
#         await update.message.reply_text(p.file_id)
#         await update.message.reply_text(p.file_size)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, image_handler))
    # application.add_handler(MessageHandler(filters.PHOTO, images))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
