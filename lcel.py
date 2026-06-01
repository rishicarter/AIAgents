from dotenv import load_dotenv
import os

from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda, ConfigurableFieldMultiOption
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openrouter import ChatOpenRouter
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODEL_NAME=os.getenv("OPENROUTER_MODEL2")

LLM_OPTION = ConfigurableFieldMultiOption(
    id="model_choice",
    options={
        "nvidia": ChatOpenRouter(model=os.getenv("OPENROUTER_MODEL2"), temperature=0, reasoning={"effort": "none"}),
        "owl": ChatOpenRouter(model=os.getenv("OPENROUTER_MODEL1"), temperature=0, reasoning={"effort": "none"}),
        "google": ChatGoogleGenerativeAI(model=os.getenv('GOOGLE_MODEL_NAME', ""))
    },
    default="nvidia"
)

def getLLM(model, temperature=0, reasoning=False):
    if reasoning:
        return ChatOpenRouter(model=model, temperature=temperature, reasoning={"effort": "low"})
    else:
        return ChatOpenRouter(model=model, temperature=temperature, reasoning={"effort": "none"})

def passThrough():
    llm = getLLM(model=os.getenv("OPENROUTER_MODEL2"))
    parser = StrOutputParser()
    draft_prompt = ChatPromptTemplate.from_template(
        """Write one-paragraph summary of: {topic}"""
    )
    draft_chain = draft_prompt | llm | parser

    Critique_prompt = ChatPromptTemplate.from_template(
        """
        Topic: {topic}
        Draft: {draft}

        Critique this draft. List 3 specific improvements.
        """
    )
    critique_chain = Critique_prompt | llm | parser

    full_chain = RunnablePassthrough.assign(draft=draft_chain) | critique_chain

    result = full_chain.invoke({"topic": "quantum computing"})

    print(f"{result=}")

def passThroughParallel():
    llm = getLLM(model=MODEL_NAME)
    parser = StrOutputParser()

    sentiment_chain = ChatPromptTemplate.from_template(
        """Classify sentiment as POSTIVE/NEGATIVE/NEUTRAL: {text}"""
    ) | llm | parser

    summary_chain = ChatPromptTemplate.from_template(
        """Sumarize in one sentence: {text}"""
    ) | llm | parser

    language_chain = ChatPromptTemplate.from_template(
        """What language is this text written in? Answer with just the language name: {text}"""
    ) | llm | parser

    parallel_chain = RunnableParallel({
        "sentiment": sentiment_chain,
        "summary": summary_chain,
        "language": language_chain
    })

    text = "Thoda kum shabdo me LLM kya hota hai batao aur kaha istemaal kr sakte hai batao."
    res = parallel_chain.invoke({"text": text})

    print(f"{text=}")
    print(f"{res['sentiment']=}")
    print(f"{res['summary']=}")
    print(f"{res['language']=}")

    try:
        print(f"{res.usage_metadata=}")
    except:
        print("No Metadata")

def passthroughLambda():
    llm = getLLM(model=MODEL_NAME)
    parser = StrOutputParser()

    def preprocess(text: str)->dict:
        cleaned = text.strip().lower()
        return {"text": cleaned}
    def format_output(result: str)->str:
        return f"Analysis result: \n{'-'*20}\n{result}"
    
    lambda_prompt = ChatPromptTemplate.from_template(
        """Analysis this text: {text}"""
    )

    lambda_chain = RunnableLambda(preprocess) | lambda_prompt | llm | parser | RunnableLambda(format_output)

    result = lambda_chain.invoke("THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG   ")
    print(result)

def streamOutput():
    llm = getLLM(model=os.getenv("OPENROUTER_MODEL2"))
    parser = StrOutputParser()
    draft_prompt = ChatPromptTemplate.from_template(
        """Write one-paragraph summary of: {topic}"""
    )
    draft_chain = draft_prompt | llm | parser

    Critique_prompt = ChatPromptTemplate.from_template(
        """
        Topic: {topic}
        Draft: {draft}

        Critique this draft. List 3 specific improvements.
        """
    )
    critique_chain = Critique_prompt | llm | parser

    full_chain = RunnablePassthrough.assign(draft=draft_chain) | critique_chain

    # result = full_chain.invoke({"topic": "quantum computing"})
    for chunk in full_chain.stream({"topic": "Machine Learning"}):
        print(chunk, end="", flush=True)
        print()

    # print(f"{result=}")

def multiOption():
    parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_template(
        """What are LLMs?"""
    )
    chain = prompt | LLM_OPTION | parser
    res = chain.with_config(configurable={"model_choice": "google"}).invoke()

if __name__ == "__main__":
    streamOutput()