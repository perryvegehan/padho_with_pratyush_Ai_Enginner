import ast
import json
import operator as op
import os

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

MODEL = "openai/gpt-oss-120b"

# --- Tool implementations -----------------------------------------------

def web_search(query: str) -> str:
    result = tavily.search(query=query)
    results = result.get("results", [])
    if not results:
        return "No results found."
    lines = [f"{r['title']}: {r['content']} ({r['url']})" for r in results]
    return "\n".join(lines)


_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsupported expression")


def calculate(expression: str) -> str:
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval_node(tree.body))
    except Exception as exc:
        return f"Error evaluating expression: {exc}"


# --- Tool schema for the LLM ---------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for up-to-date information and return a summary of results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the web.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a basic math expression (addition, subtraction, multiplication, division, exponents) and return the result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A math expression to evaluate, e.g. '2*2' or '(3+5)/4'.",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]

available_functions = {
    "web_search": web_search,
    "calculate": calculate,
}


# --- Agent loop ------------------------------------------------------------

def run_agent(user_query: str) -> str:
    messages = [{"role": "user", "content": user_query}]

    response = groq.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if not tool_calls:
        return response_message.content

    messages.append(response_message)

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)

        function_response = function_to_call(**function_args)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": function_response,
            }
        )

    second_response = groq.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    return second_response.choices[0].message.content


if __name__ == "__main__":
    query = input("Ask something: ")
    answer = run_agent(query)
    print(answer)
