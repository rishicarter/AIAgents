"""
Handles the /ask <query> command.
 
Mini RAG responsible for asking question specific to BYLD - 2026 HR / L&D Trends Survey
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
 
logger = logging.getLogger(__name__)

ASK_TEXT = """
### Note ###
Text-based queries and Q&A are **not supported yet**.

A **Mini-RAG feature for the BYLD - 2026 HR / L&D Trends Survey** will be introduced soon.

Stay tuned for updates!
"""

async def ask_handler(update: Update, context: ContextTypes):
    """Ask a Query"""
    logger.info("Query Handler")
    await update.message.reply_text(ASK_TEXT, parse_mode="Markdown")
