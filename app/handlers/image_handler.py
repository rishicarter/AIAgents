"""
handlers/image_handler.py
Handles the /image command — triggered when a user uploads a photo.

How to use from Telegram:
  1. Attach a photo.
  2. Set the caption to: /image
  3. Send — the bot will reply with a description.

"""

import logging
import os
import tempfile

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def describe_image(image_path: str) -> str:
    """
    TODO: Call vision model.

    Args:
        image_path: Local filesystem path to the downloaded image.

    Returns:
        A human-readable description string.
    """
    logger.info("Describing image at: %s", image_path)
    file_size = os.path.getsize(image_path)
    # ---- Replace with real vision model call ----
    return (
        f"[Vision Placeholder] Received an image ({file_size} bytes). "
        "Replace `describe_image()` with your actual vision model call."
    )


async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Entry point for photo uploads.

    Flow:
      1. Download the highest-resolution version of the photo Telegram provides.
      2. Save it to a temp file.
      3. Pass the path to describe_image().
      4. Reply with the description and clean up the temp file.
    """
    message = update.message

    if not message.photo:
        await message.reply_text(
            "⚠️ Please send a photo.\n"
            "_Usage:_ Attach an image and set the caption to `/image`.",
            parse_mode="Markdown",
        )
        return

    logger.info("User %s sent an image for description.", update.effective_user.id)
    await message.chat.send_action(action="upload_photo")

    # Telegram returns multiple resolutions; pick the largest (last) one
    photo_file = await message.photo[-1].get_file()

    try:
        # Stream the file to a named temp file so describe_image() can read it
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        await photo_file.download_to_drive(tmp_path)
        description = describe_image(tmp_path)

    except Exception as exc:
        logger.exception("Error processing image: %s", exc)
        description = "❌ Sorry, I couldn't process your image. Please try again."

    finally:
        # Clean up the temp file regardless of success/failure
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    await message.reply_text(f"🖼️ *Image Description*\n\n{description}", parse_mode="Markdown")