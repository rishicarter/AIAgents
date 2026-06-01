# tot - Tree of thought
from dotenv import load_dotenv
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openrouter import ChatOpenRouter


def main():
    load_dotenv()

    llm = ChatOpenRouter(model=os.getenv("OPENROUTER_MODEL2"), temperature=0.7, reasoning={"effort": "none"})
    parser = StrOutputParser()

    print("=" * 60)
    print("TREE OF THOUGHT REASONING")
    print("=" * 60)

    # ToT Prompt
    tot_prompt = ChatPromptTemplate.from_template("""
Solve this problem by exploring MULTIPLE different reasoning paths, then compare them.

Problem: {problem}

Instructions:
1. Generate 3 DIFFERENT approaches to solve this problem
2. Label them as Path A, Path B, and Path C
3. For each path, show the reasoning and conclusion
4. Evaluate which path is most effective and why
5. Provide the final answer based on the best path

Solution:

PATH A:
[First approach]

PATH B:
[Second approach]

PATH C:
[Third approach]

EVALUATION:
[Compare the three paths]

FINAL ANSWER:
[Best solution]
""")

    chain = tot_prompt | llm | parser

    problems = [
        "Should a startup prioritize growth or profitability in its first 2 years?",
        "What's the best strategy for a small business to compete against a large corporation?",
        "How should a city balance economic development with environmental protection?",
    ]

    for i, problem in enumerate(problems, 1):
        print(f"\n{'=' * 60}")
        print(f"PROBLEM {i}")
        print("=" * 60)
        print(f"\n{problem}\n")
        print("-" * 60)

        result = chain.invoke({"problem": problem})
        print(result)


if __name__ == "__main__":
    main()