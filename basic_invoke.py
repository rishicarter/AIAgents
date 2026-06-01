import os
import time
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openrouter import ChatOpenRouter

load_dotenv()
def main():

    prompt = ChatPromptTemplate.from_template("Translate to French: {text}")
    model = ChatGoogleGenerativeAI(model=os.getenv('GOOGLE_MODEL_NAME', ""))

    chain = prompt | model

    response = chain.invoke({
        "text": "Good morning"
    })

    print(f"Content: {response.content[0]['text']}")
    print(f"Usage metadata: {response.usage_metadata}")

def main1():
    prompt = ChatPromptTemplate.from_template("Translate to French: {text}")
    model = ChatOpenRouter(model=os.getenv('OPENROUTER_MODEL1'))

    chain = prompt | model

    response = chain.invoke({
        "text": "Good morning"
    })

    print(f"Content: {response.content}")
    print(f"Usage metadata: {response.usage_metadata}")

def chatprompt():
    llm = ChatOpenRouter(
        model=os.getenv("OPENROUTER_MODEL1"),
        temperature=0,
        max_tokens=128
    )

    res = llm.invoke("What is the capital of France?")
    print(f"{res.content=}")
    print(f"{res.usage_metadata=}")

    short_model = ChatOpenRouter(
        model=os.getenv("OPENROUTER_MODEL2"),
        temperature=0,
        max_tokens=10
    )
    # ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_MODEL_NAME"), max_tokens=10)
    short_res = short_model.invoke("Tell a very long story about the history of the universe.")
    print(f"{short_res.content=}")
    print(f"{short_res.usage_metadata=}")

def temp_changes():
    llm = ChatOpenRouter(
        model=os.getenv("OPENROUTER_MODEL2"),
        temperature=0,
        max_tokens=10,
        reasoning={"effort": "none"}
    )
    print("-------- WITH TEMPERATURE 0 ---------")
    for i in range(5):
        res = llm.invoke("What is the population of France? Only give the number.")
        print(f"{res.content=}")
        print(f"{res.usage_metadata=}")
        time.sleep(3)
    
    llm = ChatOpenRouter(
        model=os.getenv("OPENROUTER_MODEL2"),
        temperature=0.7,
        max_tokens=10,
        reasoning={"effort": "none"}
    )
    print("-------- WITH TEMPERATURE 0.7 ---------")
    for i in range(5):
        res = llm.invoke("What is the population of France? Only give the number.")
        print(f"{res.content=}")
        print(f"{res.usage_metadata=}")
        time.sleep(3)
        
if __name__ == "__main__":
    temp_changes()