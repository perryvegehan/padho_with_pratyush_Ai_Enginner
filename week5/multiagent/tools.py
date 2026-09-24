import os
import math

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient


# ============================================================
# SETUP  (keys come from the .env at the repo root)
# ============================================================

load_dotenv()

# free tier is only 8000 tokens/min, so let the SDK wait and retry on 429s
groq = Groq(api_key=os.getenv("GROQ_API_KEY"), max_retries=10)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

MODEL = "openai/gpt-oss-120b"


# ============================================================
# TOOL 1 — WEB SEARCH
# ============================================================

def web_search(query: str) -> str:
    """Search the web for current information."""

    try:
        response = tavily.search(query=query, max_results=2, search_depth="basic")

        results = []
        for result in response["results"]:
            results.append(
                f"Title: {result['title']}\n"
                f"URL: {result['url']}\n"
                f"Content: {result['content'][:400]}"  # trimmed to save tokens
            )

        return "\n\n".join(results)

    except Exception as e:
        return f"Search failed: {e}"


# ============================================================
# TOOL 2 — PYTHON CALCULATOR
# ============================================================

# only math functions are allowed inside eval, nothing else
SAFE_MATH = {name: getattr(math, name) for name in dir(math) if not name.startswith("_")}
SAFE_MATH.update({"abs": abs, "round": round, "min": min, "max": max})


def calculate(expression: str) -> str:
    """Evaluate a python math expression, e.g. 'sqrt(2) * 10'."""

    try:
        return str(eval(expression, {"__builtins__": {}}, SAFE_MATH))
    except Exception as e:
        return f"Calculation failed: {e}"


# ============================================================
# TOOL DEFINITIONS FOR THE LLM
# ============================================================

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the web for current information, news, facts, "
            "statistics, prices or anything that may have changed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "A specific, concise web search query."}
            },
            "required": ["query"],
        },
    },
}

CALC_TOOL = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": (
            "Evaluate a Python math expression. Supports + - * / ** and "
            "math functions like sqrt, log, pow, floor, ceil, round."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "e.g. '(330 / 8849) * 100'"}
            },
            "required": ["expression"],
        },
    },
}

AVAILABLE_TOOLS = {
    "web_search": web_search,
    "calculate": calculate,
}


# ============================================================
# TOKEN TRACKER
# ============================================================

class TokenTracker:
    """Adds up token usage across every LLM call, grouped by a label."""

    def __init__(self):
        self.by_label = {}

    def add(self, label: str, usage):
        entry = self.by_label.setdefault(label, {"calls": 0, "prompt": 0, "completion": 0, "total": 0})
        entry["calls"] += 1
        entry["prompt"] += usage.prompt_tokens
        entry["completion"] += usage.completion_tokens
        entry["total"] += usage.total_tokens

    @property
    def total(self) -> int:
        return sum(e["total"] for e in self.by_label.values())

    @property
    def calls(self) -> int:
        return sum(e["calls"] for e in self.by_label.values())

    def report(self, title: str):
        print(f"\n--- Token usage: {title} ---")
        print(f"{'LLM':<14}{'calls':>6}{'prompt':>10}{'completion':>12}{'total':>10}")
        for label, e in self.by_label.items():
            print(f"{label:<14}{e['calls']:>6}{e['prompt']:>10}{e['completion']:>12}{e['total']:>10}")
        print(f"{'TOTAL':<14}{self.calls:>6}{'':>10}{'':>12}{self.total:>10}")
