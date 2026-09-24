import json
from pathlib import Path

from tools import groq, MODEL, SEARCH_TOOL, CALC_TOOL, TokenTracker
from single_agent import ask_llm


# ============================================================
# MULTI AGENT (no LangGraph)
#
#   manager LLM  --decides-->  ask_search_llm  (web_search only)
#                         \->  ask_maths_llm   (calculate only)
#
# The manager never sees raw tool output. It only reads its
# notes file, where every helper's answer gets written down.
# ============================================================

NOTES_FILE = Path(__file__).parent / "notes.md"
MAX_MANAGER_ROUNDS = 5


# ============================================================
# HELPER 1 — SEARCH LLM
# ============================================================

SEARCH_PROMPT = """
You are a search specialist. You only have the web_search tool.
Search each fact ONCE and take the first reasonable number; do not re-verify.
Reply with just those facts,
their exact numbers, and the source URLs. Do not do any maths.
"""


def ask_search_llm(task: str, tracker: TokenTracker) -> str:
    return ask_llm(task, tracker, SEARCH_PROMPT, [SEARCH_TOOL], label="search_llm")


# ============================================================
# HELPER 2 — MATHS LLM
# ============================================================

MATHS_PROMPT = """
You are a maths specialist. You only have the calculate tool.
Use calculate for every step, never compute in your head.
Reply with each step's result and the final number.
"""


def ask_maths_llm(task: str, tracker: TokenTracker) -> str:
    return ask_llm(task, tracker, MATHS_PROMPT, [CALC_TOOL], label="maths_llm")


HELPERS = {
    "ask_search_llm": ask_search_llm,
    "ask_maths_llm": ask_maths_llm,
}


# ============================================================
# MANAGER — its tools are the helper LLMs
# ============================================================

MANAGER_PROMPT = """
You are a manager. You do NOT search or calculate yourself.
Your only job is to decide which helper to send work to:

- ask_search_llm: finds facts on the web.
- ask_maths_llm: does calculations. It cannot search, so always
  put the actual numbers from your notes into its task.

You will be shown your notes file, which contains every helper answer so far.
Send clear, self-contained tasks. You only get 5 rounds, so send independent tasks in the same round.
When your notes contain everything needed, write the final answer to the user
with the numbers and source URLs, and do not call any helper.
"""

HELPER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "A complete, self-contained instruction for the helper."}
                },
                "required": ["task"],
            },
        },
    }
    for name, desc in [
        ("ask_search_llm", "Send a fact-finding task to the web search specialist."),
        ("ask_maths_llm", "Send a calculation task (with all numbers included) to the maths specialist."),
    ]
]


def write_note(round_no: int, helper: str, task: str, answer: str):
    with NOTES_FILE.open("a", encoding="utf-8") as f:
        f.write(f"## Round {round_no} — {helper}\n**Task:** {task}\n\n**Answer:**\n{answer}\n\n")


def ask_manager_llm(question: str, tracker: TokenTracker) -> str:

    NOTES_FILE.write_text(f"# Notes for: {question}\n\n", encoding="utf-8")

    def manager_messages():
        # the manager's memory is the notes file, rebuilt fresh every round
        return [
            {"role": "system", "content": MANAGER_PROMPT},
            {"role": "user", "content": f"Question: {question}\n\nYour notes file:\n{NOTES_FILE.read_text(encoding='utf-8')}"},
        ]

    for round_no in range(1, MAX_MANAGER_ROUNDS + 1):

        print(f"\n[manager] round {round_no}")

        response = groq.chat.completions.create(
            model=MODEL, messages=manager_messages(), tools=HELPER_TOOLS, tool_choice="auto"
        )
        tracker.add("manager", response.usage)

        message = response.choices[0].message

        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            helper = tool_call.function.name
            task = json.loads(tool_call.function.arguments)["task"]
            print(f"[manager] -> {helper}: {task}")

            answer = HELPERS[helper](task, tracker)
            write_note(round_no, helper, task, answer)

    # out of rounds: answer from the notes with no helpers available
    print("\n[manager] round limit reached, forcing final answer")
    messages = manager_messages()
    messages.append({"role": "user", "content": "You can no longer use helpers. Answer now using only your notes."})
    response = groq.chat.completions.create(model=MODEL, messages=messages)
    tracker.add("manager", response.usage)
    return response.choices[0].message.content


if __name__ == "__main__":
    tracker = TokenTracker()
    answer = ask_manager_llm(input("Ask me anything: "), tracker)
    print("\nFINAL ANSWER:\n" + answer)
    tracker.report("multi agent")
