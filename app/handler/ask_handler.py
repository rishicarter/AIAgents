"""
Handles the /ask <query> command.
 
Mini RAG responsible for asking question specific to BYLD - 2026 HR / L&D Trends Survey
"""
import logging
import json
import requests

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
    # await update.message.reply_text(ASK_TEXT, parse_mode="Markdown")

    logger.info("Sending user query")

    payload = {
        # "source": "whatsapp",
        "from": "",
        "message": "Hi",
        # "language": "en-IN",
        "provider_message_id": "1"
    }

    response_dict = send_msgs(payload)

    await update.message.reply_text(str(response_dict), parse_mode="Markdown")



def send_msgs(payload: dict) -> dict:
    try:

        url = "sales-copilot/webhooks/whatsapp"    
        
        headers = {
            "Content-Type": "application/json",
            # "Authorization": "BEAR"
        }
        logging.info(f"{payload=}")
        payload = json.dumps(payload)
        response = requests.request(url=url, method="POST", data=payload, headers=headers)

        response.raise_for_status()
        
        # 2. Parse the JSON body into a Python dictionary
        data = response.json()

        print("Success:", data)
        return {"data": data}

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # e.g., 404 Not Found or 500 Server Error
    except requests.exceptions.JSONDecodeError:
        print("Response was not valid JSON.")       # Handles non-JSON text/HTML responses
    except requests.exceptions.RequestException as err:
        print(f"Network or system error: {err}") 