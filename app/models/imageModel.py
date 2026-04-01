"""
Structured Model for Vision Model response parsing
"""
import logging
from pydantic import Field, BaseModel

logger = logging.getLogger(__name__)

class ImageInfo(BaseModel):
    caption: str = Field(description="Catchy, engaging caption for social media.")
    tags: list[str] = Field(description="List of 3 Keywords that describe the Image.")
    summary: str = Field(description="Short engaging Summary describing the Image.")