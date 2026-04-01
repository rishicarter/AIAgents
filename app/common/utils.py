"""
Utility Functions - Helper functions + LLM calling functions
"""
import logging
import base64
import time

from app.models.imageModel import ImageInfo
from app.common.config import ENV

from telegram import File
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

MODEL_NAME="gpt-5-nano"
SYSTEM_PROMPT="""
You are a creative image caption writer.

Write:
- A catchy, engaging caption (<=15 words)
- Not a literal description - add emotion, tone, or personality
- Avoid phrases like "image shows" or "a picture of"

Also return:
- 3 short relevant tags
- A short natural summary (<=40 words)

Be natural, and expressive.
"""


def safe(text: str) -> str:
    return text.replace("`", "'")

async def caption_image(image_file: File) -> dict:
    """Describe uploaded Image with Structured JSON output"""
    try:
        logger.info("Starting image captioning pipeline...")
        llm = ChatOpenAI(
            model=MODEL_NAME,
            temperature=0.7,
            reasoning_effort="minimal",
            api_key=ENV.OPENAI_API_KEY
        )
        image_bytes = await image_file.download_as_bytearray()
        base64_string = base64.b64encode(image_bytes).decode("utf-8")

        msgs = [
            SystemMessage(SYSTEM_PROMPT),
            HumanMessage(content=[
                {"type": "text", "text": "Extract engaging details from the image."},
                {"type": "image", "base64": base64_string, "mime_type": "image/jpeg"}
            ])
        ]

        chain = llm.with_structured_output(schema=ImageInfo, method="json_schema", include_raw=False, strict=True)

        # chain = llm | parser
        logger.info("Generating Structured Response....")
        start = time.time()
        response = chain.invoke(msgs)
        logger.info(f"LLM latency: {time.time() - start:.2f}s")
        if response:
            logger.info("Caption generated successfully")
            return dict(response)
        else:
            logger.warning("Empty response from model")
            return None
    except Exception as ex:
        logger.error(f"Error occured during captioning!", exc_info=True)
        return None