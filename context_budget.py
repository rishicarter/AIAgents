from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openrouter import ChatOpenRouter

load_dotenv()

def estimate_tokens(text: str) -> int:
    return len(text) // 4

class ContextBudget:
    def __init__(self, total_budget: int = 128000):
        self.total_budget = total_budget
        self.allocations = {
            "system": 0,
            "history": 0,
            "documents": 0,
            "query": 0,
            "reserved_response": 4000,
        }

    def used(self) -> int:
        return sum(self.allocations.values())
    
    def remaining(self) -> int:
        return self.total_budget - self.used()

    def allocate(self, region: str, text: str) -> bool:
        tokens = estimate_tokens(text)
        self.allocations[region] = tokens
        return self.remaining() >= 0
    
    def report(self) -> str:
        lines = ["Context Budget Report:", "-"*40]
        for region, tokens in self.allocations.items():
            pct = (tokens / self.total_budget) * 100
            lines.append(f"{region:20}: {tokens:>6} tokens ({pct:.1f}%)")
            lines.append("-"* 40)
            lines.append(f"{'TOTAL USED':20}: {self.used():>6} tokens")
            lines.append(f"{'REMAINING':20}: {self.remaining():>6} tokens")
        return "\n".join(lines)

def basicInvoke():
    budget = ContextBudget(total_budget=256000)

    system_prompt = """You are a helpful AI assistant. Be concise and accurate."""
    history = """User: What is ML?
    AI: ML is a subset of AI where systems lean from data.
    """
    document = "Document 1: "+ ("ML content. "*500)
    query = "How does a neural network learn?"

    budget.allocate("system", system_prompt)
    budget.allocate("history", history)
    budget.allocate("document", document)
    budget.allocate("query", query)

    print(budget.report())

    if budget.remaining() < 10000:
        print("Low token budget remaining for RESPONSES.")

if __name__ == "__main__":
    basicInvoke()