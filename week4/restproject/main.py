"""
Restaurant order management agent built with LangGraph.

Flow:
    user_input -> llm -> order_confirm -> llm -> cook -> llm -> serve -> llm -> END

The `llm` node is the "brain": every other node reports back to it by writing
`status`, and the llm reads the state (status + retry counters) to decide what
to say to the user and which node runs next.

uv add langgraph langchain-groq python-dotenv
"""

import difflib
import os
import random
import sys
from typing import Annotated, Literal, Optional, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

load_dotenv()

# Windows console defaults to cp1252 and chokes on fancy quotes the model likes to emit
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODEL = "openai/gpt-oss-120b"
llm = ChatGroq(model=MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)

# ============================================================
# MENU  (dish -> quantity in stock)
# ============================================================

MENU: dict[str, int] = {
    "pizza": 5,
    "burger": 3,
    "biryani": 10,
    "dosa": 2,
    "pasta": 0,  # on the menu but sold out
}

ORDER_RETRIES = 3
COOK_RETRIES = 2
SERVE_RETRIES = 2

COOK_SUCCESS_PROB = 0.6
SERVE_SUCCESS_PROB = 0.6


def find_menu_item(name: str) -> str | None:
    """Fuzzy-match a dish name to a MENU key. Returns the key, or None if nothing is close."""
    name = name.strip().lower()
    if name in MENU:
        return name
    # "margherita pizza" -> "pizza", "biryani rice" -> "biryani"
    for key in MENU:
        if key in name or name in key:
            return key
    # "piza", "burgr" -> closest spelling
    close = difflib.get_close_matches(name, MENU.keys(), n=1, cutoff=0.6)
    return close[0] if close else None


# ============================================================
# STATE
# ============================================================


class OrderDetails(TypedDict):
    dish_name: str
    required_quantity: int
    available_quantity: int  # written by order_confirm; 0 if dish not on menu


# Values `status` can hold. Nodes write the left column, the llm reads it and
# writes the right column to say where the graph goes next.
#
#   written by nodes            written by llm (= routing decision)
#   ---------------------       ----------------------------------
#   new                         awaiting_user   -> user_input
#   confirmed / partial /       placed          -> order_confirm
#     unavailable               cook            -> cook
#   ready / cook_failed         serve           -> serve
#   complete / serve_failed     done / failed   -> END
Status = Literal[
    "new",
    "awaiting_user",
    "placed",
    "confirmed",
    "partial",
    "unavailable",
    "cook",
    "ready",
    "cook_failed",
    "serve",
    "complete",
    "serve_failed",
    "done",
    "failed",
]


class State(TypedDict):
    messages: Annotated[list, add_messages]
    order: OrderDetails
    status: Status
    order_retries: int  # order attempts left (3)
    cook_retries: int  # cook RE-runs left (2); first cook is free, every re-cook costs one, whoever caused it
    serve_retries: int  # serve RE-runs left (2); first serve is free
    final_result: str


def initial_state() -> State:
    return {
        "messages": [],
        "order": {"dish_name": "", "required_quantity": 0, "available_quantity": 0},
        "status": "new",
        "order_retries": ORDER_RETRIES,
        "cook_retries": COOK_RETRIES,
        "serve_retries": SERVE_RETRIES,
        "final_result": "",
    }


# ============================================================
# LLM HELPERS
# ============================================================


class OrderIntent(BaseModel):
    """What the LLM extracts from a user message."""

    intent: Literal["new_order", "accept_partial", "unrelated"] = Field(
        description=(
            "new_order: user is ordering a dish with a quantity. "
            "accept_partial: user agrees to take the smaller available quantity. "
            "unrelated: message has nothing to do with ordering food."
        )
    )
    dish_name: Optional[str] = Field(default=None, description="Dish name, lowercase, singular")
    quantity: Optional[int] = Field(default=None, description="Quantity requested (default 1 if omitted)")


EXTRACT_PROMPT = """You are the order-taking assistant of a restaurant. You ONLY handle food orders.
Read the user's latest message and classify it.

- If they order a dish, return intent=new_order with dish_name (lowercase, singular) and quantity (1 if not stated).
- If they are agreeing to go ahead with the smaller available quantity that was offered to them
  (e.g. "yes", "ok go ahead", "fine, give me what you have"), return intent=accept_partial.
- If the message is not about ordering food (general questions, chit-chat, coding help...), return intent=unrelated.

Menu (dish -> in stock): {menu}
Was the user just offered a partial order? {partial_offer}
"""


def extract_order(state: State) -> OrderIntent:
    """Ask the LLM to pull dish + quantity (or intent) out of the latest user message."""
    partial_offer = "yes" if state["status"] == "awaiting_user" and state["order"]["available_quantity"] > 0 else "no"
    system = EXTRACT_PROMPT.format(menu=MENU, partial_offer=partial_offer)
    structured = llm.with_structured_output(OrderIntent)
    last_user = next(m for m in reversed(state["messages"]) if isinstance(m, HumanMessage))
    return structured.invoke([SystemMessage(system), last_user])


def say(instruction: str, state: State) -> str:
    """Ask the LLM to phrase a short message to the customer given the current state."""
    system = (
        "You are the friendly assistant of a restaurant's order system. "
        "Write ONE or TWO short sentences to the customer. No markdown.\n"
        f"Current order: {state['order']}\n"
        f"Retries left -> order: {state['order_retries']}, cook: {state['cook_retries']}, serve: {state['serve_retries']}\n"
        f"What to tell the customer: {instruction}"
    )
    return llm.invoke([SystemMessage(system)]).content.strip()


# ============================================================
# NODES
# ============================================================


def user_input(state: State, config: RunnableConfig) -> dict:
    """Read the next order from the user. Tests can inject `input_fn` via config."""
    read = config.get("configurable", {}).get("input_fn", input)
    text = read("\nYou: ")
    return {"messages": [HumanMessage(text)]}


def llm_node(state: State) -> dict:
    """The brain. Reads status + counters, talks to the user, and decides the next status."""
    status = state["status"]
    order = dict(state["order"])

    # ---- waiting on the user: parse what they typed ----------------------
    if status in ("new", "awaiting_user"):
        parsed = extract_order(state)

        if parsed.intent == "accept_partial" and status == "awaiting_user" and order["available_quantity"] > 0:
            order["required_quantity"] = order["available_quantity"]
            msg = say(f"Confirm we are going ahead with {order['required_quantity']} x {order['dish_name']} and sending it to the kitchen.", {**state, "order": order})
            return {"messages": [AIMessage(msg)], "order": order, "status": "cook"}

        if parsed.intent == "new_order" and parsed.dish_name:
            order = {
                "dish_name": parsed.dish_name.strip().lower(),
                "required_quantity": max(1, parsed.quantity or 1),
                "available_quantity": 0,
            }
            return {"order": order, "status": "placed"}

        # unrelated / could not extract -> costs one order attempt
        retries = state["order_retries"] - 1
        if retries <= 0:
            msg = say("Politely say you are a food-ordering assistant only, and since no valid order was placed after 3 attempts you are closing the session.", state)
            return {"messages": [AIMessage(msg)], "order_retries": 0, "status": "failed", "final_result": "NOT COMPLETED: no valid order after 3 attempts"}
        msg = say("Politely say you are an AI agent for food ordering only, not a general-purpose assistant, and ask them to place a food order (dish + quantity).", state)
        return {"messages": [AIMessage(msg)], "order_retries": retries, "status": "awaiting_user"}

    # ---- order_confirm reported back ------------------------------------
    if status == "confirmed":
        msg = say(f"Confirm the order of {order['required_quantity']} x {order['dish_name']} is available and is being sent to the kitchen.", state)
        return {"messages": [AIMessage(msg)], "status": "cook"}

    if status in ("partial", "unavailable"):
        retries = state["order_retries"] - 1
        if retries <= 0:
            msg = say("Apologize: the order could not be fulfilled and all 3 order attempts are used up, so the session is closing.", state)
            return {"messages": [AIMessage(msg)], "order_retries": 0, "status": "failed", "final_result": "NOT COMPLETED: order attempts exhausted"}
        if status == "partial":
            instruction = (
                f"Only {order['available_quantity']} of the {order['required_quantity']} {order['dish_name']} requested are available. "
                f"Ask if they want to go ahead with {order['available_quantity']} or place a different order. Mention {retries} attempt(s) left."
            )
        else:
            instruction = f"'{order['dish_name']}' is not available at all. Ask them to place a different order. Mention the menu and {retries} attempt(s) left."
        msg = say(instruction, state)
        return {"messages": [AIMessage(msg)], "order_retries": retries, "status": "awaiting_user"}

    # ---- cook reported back ---------------------------------------------
    if status == "ready":
        msg = say("Say the food is ready and is now being served.", state)
        return {"messages": [AIMessage(msg)], "status": "serve"}

    if status == "cook_failed":
        if state["cook_retries"] > 0:
            print(f"[llm] cook failed -> retry cook (cook retries left: {state['cook_retries'] - 1})")
            msg = say("Say there was a problem in the kitchen and the dish is being cooked again.", state)
            return {"messages": [AIMessage(msg)], "status": "cook", "cook_retries": state["cook_retries"] - 1}
        msg = say("Apologize sincerely: the kitchen failed to prepare the dish even after retrying, so the order is cancelled.", state)
        return {"messages": [AIMessage(msg)], "status": "failed", "final_result": "NOT COMPLETED: cook failed"}

    # ---- serve reported back --------------------------------------------
    if status == "complete":
        msg = say("Tell the customer their order is complete and enjoy the meal.", state)
        return {"messages": [AIMessage(msg)], "status": "done", "final_result": "COMPLETED"}

    if status == "serve_failed":
        # a re-serve needs a re-cook first, so this spends one retry of each
        if state["serve_retries"] > 0 and state["cook_retries"] > 0:
            print(f"[llm] serve failed -> retry cook+serve (cook retries left: {state['cook_retries'] - 1}, serve retries left: {state['serve_retries'] - 1})")
            msg = say("Say serving went wrong, the dish is being cooked once more and will be served again.", state)
            return {"messages": [AIMessage(msg)], "status": "cook", "cook_retries": state["cook_retries"] - 1, "serve_retries": state["serve_retries"] - 1}
        reason = "serve failed" if state["serve_retries"] <= 0 else "serve failed and cook retries exhausted"
        msg = say(f"Apologize sincerely: {reason}, so the order is cancelled.", state)
        return {"messages": [AIMessage(msg)], "status": "failed", "final_result": f"NOT COMPLETED: {reason}"}

    raise ValueError(f"llm node got unexpected status {status!r}")


def order_confirm(state: State) -> dict:
    """Check the order against the MENU and write available_quantity + status."""
    order = dict(state["order"])
    match = find_menu_item(order["dish_name"])
    if match:
        order["dish_name"] = match
    available = MENU[match] if match else 0
    order["available_quantity"] = available

    if available == 0:
        status = "unavailable"
    elif available < order["required_quantity"]:
        status = "partial"
    else:
        status = "confirmed"

    print(f"[order_confirm] {order['dish_name']}: need {order['required_quantity']}, have {available} -> {status}")
    return {"order": order, "status": status}


def _outcome(config: RunnableConfig, key: str, prob: float) -> bool:
    """60/40 coin flip. Tests can pre-script results with config['configurable'][key] = [True, False, ...]."""
    scripted = config.get("configurable", {}).get(key)
    if scripted:
        return bool(scripted.pop(0))
    return random.random() < prob


def cook(state: State, config: RunnableConfig) -> dict:
    """60/40 coin flip. The llm decides (and pays for) any retry."""
    if _outcome(config, "cook_outcomes", COOK_SUCCESS_PROB):
        print("[cook] success -> ready")
        return {"status": "ready"}
    print("[cook] FAILED")
    return {"status": "cook_failed"}


def serve(state: State, config: RunnableConfig) -> dict:
    """60/40 coin flip. The llm decides (and pays for) any retry."""
    if _outcome(config, "serve_outcomes", SERVE_SUCCESS_PROB):
        print("[serve] success -> complete")
        return {"status": "complete"}
    print("[serve] FAILED")
    return {"status": "serve_failed"}


# ============================================================
# EDGES
# ============================================================


def route_after_llm(state: State) -> str:
    status = state["status"]
    if status == "awaiting_user":
        return "user_input"
    if status == "placed":
        return "order_confirm"
    if status in ("cook", "serve"):
        return status
    return END  # done / failed


# ============================================================
# GRAPH
# ============================================================

builder = StateGraph(State)
builder.add_node("user_input", user_input)
builder.add_node("llm", llm_node)
builder.add_node("order_confirm", order_confirm)
builder.add_node("cook", cook)
builder.add_node("serve", serve)

builder.add_edge(START, "user_input")
builder.add_edge("user_input", "llm")
builder.add_edge("order_confirm", "llm")
builder.add_edge("cook", "llm")
builder.add_edge("serve", "llm")
builder.add_conditional_edges(
    "llm",
    route_after_llm,
    {"user_input": "user_input", "order_confirm": "order_confirm", "cook": "cook", "serve": "serve", END: END},
)

graph = builder.compile()


# ============================================================
# RUN
# ============================================================


def run(config: RunnableConfig | None = None) -> State:
    """Run one ordering session. Prints every AI message as it is produced."""
    config = {"recursion_limit": 100, **(config or {})}
    seen = 0
    final = None
    for final in graph.stream(initial_state(), config=config, stream_mode="values"):
        for m in final["messages"][seen:]:
            if isinstance(m, AIMessage):
                print(f"Agent: {m.content}")
        seen = len(final["messages"])
    print(f"\nFINAL RESULT: {final['final_result']}")
    return final


def simulate(user_inputs: list[str], cook_outcomes: list[bool] | None = None, serve_outcomes: list[bool] | None = None) -> State:
    """Run a scripted scenario: canned user replies and pre-decided cook/serve results."""
    inputs = list(user_inputs)

    def fake_input(prompt: str) -> str:
        text = inputs.pop(0) if inputs else "bye"
        print(f"{prompt}{text}")
        return text

    return run({"configurable": {"input_fn": fake_input, "cook_outcomes": list(cook_outcomes or []), "serve_outcomes": list(serve_outcomes or [])}})


if __name__ == "__main__":
    print(f"Welcome! Menu: {MENU}")
    print("Tell me what you'd like to order (one dish + quantity).")
    run()
