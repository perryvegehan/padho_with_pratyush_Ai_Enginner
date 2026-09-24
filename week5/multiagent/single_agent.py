import json

from groq import BadRequestError

from tools import groq, MODEL, SEARCH_TOOL, CALC_TOOL, AVAILABLE_TOOLS, TokenTracker


# ============================================================
# SINGLE AGENT: one LLM, two tools, max 5 attempts
# ============================================================

SYSTEM_PROMPT = """
You are a research assistant with two tools.

Rules:
1. Use web_search for facts you are not sure about. Search each fact ONCE; take the first
   reasonable number you find and do not re-verify it.
2. Use calculate for EVERY piece of arithmetic. Never do maths in your head.
3. You only get 5 turns, so call several tools at once when they don't depend on each other.
4. When you have everything, give a short final answer with the numbers and source URLs.
"""

MAX_ATTEMPTS = 5


def ask_llm(
    question: str,
    tracker: TokenTracker,
    system_prompt: str = SYSTEM_PROMPT,
    tools: list = [SEARCH_TOOL, CALC_TOOL],
    label: str = "agent",
) -> str:
    """The LLM decides which tools to use and how many times (up to MAX_ATTEMPTS tool rounds)."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    allowed = {t["function"]["name"] for t in tools}
    findings = []  # every tool call + result, used for the wrap-up if we run out of attempts

    for attempt in range(1, MAX_ATTEMPTS + 1):

        print(f"  [{label}] attempt {attempt}")

        try:
            response = groq.chat.completions.create(model=MODEL, messages=messages, tools=tools, tool_choice="auto")
        except BadRequestError:
            # gpt-oss sometimes invents a malformed tool call; groq rejects it. Count it as a used attempt.
            print(f"  [{label}]   malformed tool call rejected by groq, retrying")
            continue
        tracker.add(label, response.usage)

        message = response.choices[0].message

        # no tool call -> final answer
        if not message.tool_calls:
            return message.content

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [tc.model_dump() for tc in message.tool_calls],
        })

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if name in allowed:
                result = AVAILABLE_TOOLS[name](**args)
            else:
                result = f"Tool '{name}' is not available to you."

            print(f"  [{label}]   -> {name}({args}) = {result[:80]!r}")
            findings.append(f"{name}({args}) returned:\n{result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    # Out of attempts: one last call with NO tools to force an answer.
    # We flatten the tool results into plain text, but gpt-oss may still
    # try to call a tool, which groq rejects -- then we give up honestly.
    print(f"  [{label}] attempt limit reached, forcing final answer")
    notes = "\n\n".join(findings)
    try:
        response = groq.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Answer the question in plain text. You have no tools."},
                {"role": "user", "content": f"{question}\n\nTool results so far:\n\n{notes}\n\nAnswer now using only this."},
            ],
        )
    except BadRequestError:
        return f"Could not finish within {MAX_ATTEMPTS} attempts. Partial findings:\n\n{notes}"
    tracker.add(label, response.usage)
    return response.choices[0].message.content


if __name__ == "__main__":
    tracker = TokenTracker()
    answer = ask_llm(input("Ask me anything: "), tracker)
    print("\nFINAL ANSWER:\n" + answer)
    tracker.report("single agent")
