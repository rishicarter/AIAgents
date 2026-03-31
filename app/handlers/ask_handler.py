"""
Code for Ask Handler
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
 
logger = logging.getLogger(__name__)

async def ask_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)