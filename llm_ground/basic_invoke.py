from dotenv import load_dotenv
load_dotenv()

from langchain_openrouter import ChatOpenRouter
from langchain_core.prompts import ChatPromptTemplate

MODEL_NAME="stepfun/step-3.5-flash:free"

llm = ChatOpenRouter(
    model=MODEL_NAME,
    temperature=0,
    max_tokens=128
)

print(llm.invoke("What is the capital of France?").content)

print(llm.invoke("What is the haiku about Football?").content)