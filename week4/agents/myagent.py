import os
import json

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient


# ============================================================
# SETUP
# ============================================================

# uv add groq python-dotenv tavily
load_dotenv()

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# ============================================================
# TOOL 1 — WEB SEARCH
# ============================================================

def web_search(query: str) -> str:
    """Search the web for current information."""

    try:
        response = tavily.search(
            query=query,
            max_results=3,
            search_depth="basic"
        )

        results = []

        for result in response["results"]:
            results.append(
                f"Title: {result['title']}\n"
                f"URL: {result['url']}\n"
                f"Content: {result['content']}"
            )

        return "\n\n".join(results)

    except Exception as e:
        return f"Search failed: {e}"


# ============================================================
# TOOL 2 — CALCULATOR
# ============================================================

def calculate(expression: str) -> str:
    """Perform a mathematical calculation."""

    try:
        return str(
            eval(
                expression,
                {"__builtins__": {}},
                {}
            )
        )
    except Exception as e:
        return f"Calculation failed: {e}"


# ============================================================
# TOOL REGISTRY
# ============================================================

AVAILABLE_TOOLS = {
    "web_search": web_search,
    "calculate": calculate,
}


# ============================================================
# TOOL DEFINITIONS FOR THE LLM
# ============================================================

tools = [

    {
        "type": "function",  # what is this tool. it is a python function
        "function": {   #actual definition 
            "name": "web_search",  # name llm will use while calling the tool

            "description": (  # when should this function be used. this is for llm
                "Search the web for current information, "
                "news, recent events, prices, statistics, "
                "or facts that may have changed."
            ),

            "parameters": {  # what does the function take as agruements
                "type": "object",  # arguements should be json object

                "properties": {  #actual arguement that function expects
                    "query": {
                        "type": "string",  #data type of the query
                        "description": (
                            "A specific and concise "
                            "web search query."
                        )
                    }
                },

                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "calculate",

            "description": (
                "Perform mathematical calculations "
                "such as percentages, multiplication, "
                "division, or arithmetic."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "A mathematical expression "
                            "such as '2500 * 0.15'."
                        )
                    }
                },

                "required": ["expression"]
            }
        }
    }
]


# ============================================================
# AGENT INSTRUCTIONS
# ============================================================

SYSTEM_PROMPT = """
You are a research assistant.

Rules:

1. Use web_search for current or changing information.
2. Use calculate for mathematical calculations.
3. You may use tools multiple times.
4. When you have enough information, answer the user.
5. Include useful source URLs from web search results.
"""


# ============================================================
# AGENT LOOP
# ============================================================

def run_agent(question: str, max_iterations: int = 5):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": question
        }
    ]

    for iteration in range(max_iterations):

        print(f"\n--- Iteration {iteration + 1} ---")

        response = groq.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # Keep the LLM response in conversation history
        messages.append(message)

        # ====================================================
        # NO TOOL → FINAL ANSWER
        # ====================================================

        if not message.tool_calls:

            print("\nFINAL ANSWER:")
            print(message.content)

            return message.content

        # ====================================================
        # TOOL CALL(S)
        # ====================================================

        print(
            f"LLM requested "
            f"{len(message.tool_calls)} tool(s)"
        )

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(f"Tool: {tool_name}")
            print(f"Arguments: {arguments}")

            # Find the actual Python function
            if tool_name not in AVAILABLE_TOOLS:

                result = (
                    f"Unknown tool: {tool_name}"
                )

            else:

                result = AVAILABLE_TOOLS[
                    tool_name
                ](**arguments)

            print("Tool result received.")

            # Send result back to the LLM
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    print("\nMaximum iterations reached.")

    return (
        "I couldn't complete the task "
        "within the iteration limit."
    )


# ============================================================
# RUN THE AGENT
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI RESEARCH AGENT")
    print("=" * 60)

    question = input("\nAsk me anything: ")

    run_agent(question)