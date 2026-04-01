"""
Handles the /image command and /summary command.
 
Upload an image to get a caption & tags and Get a short summary of your last image!
"""
import logging

from app.common.utils import safe, caption_image

from telegram import Update
from telegram.ext import ContextTypes
 
logger = logging.getLogger(__name__)

async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply when the command /image is issued or Image is uploaded."""
    photos = update.message.photo
    if not len(photos):
        await update.message.reply_text("Upload any Image!")
        return 
    # await update.message.reply_text("Checking if a caption already exists for this image...")
    if len(photos) > 1:
    # Selecting low res image to save tokens
        photo_id = photos[1].file_id
    else:
        photo_id = photos[-1].file_id
    
    response = context.user_data.get(photo_id)

    if not response:
        await update.message.reply_text("Processing caption... this may take a few seconds.")
        file = await context.bot.get_file(photo_id)
        response = await caption_image(file)
        if response:
            context.user_data[photo_id] = response

    if response:
        context.user_data["last_image_summary"] = response["summary"]

        await update.message.reply_text(
            text=(
                f"*Image Caption:*\n"
                f"`{safe(response['caption'])}`\n\n"
                f"*Tags:*\n" + "\n".join(f"- {safe(tag)}" for tag in response["tags"])
            ),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Caption generation failed... Try again later!")

async def summary_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply when the command /summary is hit."""
    summary = context.user_data.get("last_image_summary")

    if summary:
        await update.message.reply_text(summary)
    else:
        await update.message.reply_text("No image has been processed yet.\nPlease upload an image first or use /help for assistance.")