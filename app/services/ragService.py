"""
RAG service to guide the answers for LLM.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from app.services.chatService import ContextAwareChatApp
