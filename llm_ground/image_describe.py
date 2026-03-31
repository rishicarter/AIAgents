"""
LLM Testing ground to implement the Image description Technique
"""
import base64
from dotenv import load_dotenv
load_dotenv()

from app.common.utils import DATA_DIR

from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage, SystemMessage
# from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import ImageCaptionLoader
from pydantic import Field, BaseModel
from telegram import File

MODEL_NAME="nvidia/nemotron-nano-12b-v2-vl:free"
IMAGE_PATH= DATA_DIR / "BYLD-values.png"

def vanilla_describe():
    """Describe Image as plain text Output"""
    llm = ChatOpenRouter(
        model=MODEL_NAME,
        temperature=0.7
    )

    with open(IMAGE_PATH, "rb") as f:
        image_data=f.read()
        base64_string = base64.b64encode(image_data).decode('utf-8')

    msgs = [
        SystemMessage(content=f"You are an Image Analyser Assistant. "),
        HumanMessage(content=[
            {"type": "text", "text": "Describe the image using one caption in under 15 words and three keywords or tags"},
            {"type": "image", "base64": base64_string, "mime_type": "image/png"}
        ])
    ]

    response = llm.invoke(msgs)
    print(response.content)

class ImageInfo(BaseModel):
    caption: str = Field(description="Brief caption describing the Image.")
    tags: list[str] = Field(description="List of 3 Keywords that describe the Image.")

def structured_describe():
    """Describe Image as Structured JSON output"""
    llm = ChatOpenRouter(
        model=MODEL_NAME,
        temperature=0.7
    )

    with open(IMAGE_PATH, "rb") as f:
        image_data=f.read()
        base64_string = base64.b64encode(image_data).decode('utf-8')

    msgs = [
        SystemMessage(content=f"You are an Image Analyser Assistant. "),
        HumanMessage(content=[
            {"type": "text", "text": "Provide one caption and three keywords or tags to describe the image"},
            {"type": "image", "base64": base64_string, "mime_type": "image/png"}
        ])
    ]

    chain = llm.with_structured_output(schema=ImageInfo, method="json_schema", include_raw=False, strict=True)

    # chain = llm | parser

    response = chain.invoke(msgs)

    print(response)

async def structure_describe_wt_photo(image_file: File) -> dict:
    """Describe uploaded Image with Structured JSON output"""
    llm = ChatOpenRouter(
        model=MODEL_NAME,
        temperature=0.7
    )

    image_bytes = await image_file.download_as_bytearray()
    base64_string = base64.b64encode(image_bytes).decode("utf-8")

    msgs = [
        SystemMessage(content=f"You are an Image Analyser Assistant. "),
        HumanMessage(content=[
            {"type": "text", "text": "Provide one caption and three keywords or tags to describe the image"},
            {"type": "image", "base64": base64_string, "mime_type": "image/png"}
        ])
    ]

    chain = llm.with_structured_output(schema=ImageInfo, method="json_schema", include_raw=False, strict=True)

    # chain = llm | parser

    response = chain.invoke(msgs)

    print(response)
    return dict(response) if response else {}

def caption_using_blip():
    pass

# if __name__ == "__main__":
#     # print("Image Description in Plain Text")
#     # vanilla_describe()
#     print("="*50)
#     print("Image Description in JSON")
#     structured_describe()
