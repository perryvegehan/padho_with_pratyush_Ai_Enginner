from tools import TokenTracker
from single_agent import ask_llm
from multi_agent import ask_manager_llm


# small on purpose (groq free tier = 8000 tokens/min): 2 facts to search, 2 calculations
TEST_QUERY = (
    "Search the height in metres of the Eiffel Tower and of the Burj Khalifa. "
    "Then calculate (1) what percentage of the Burj Khalifa's height the Eiffel Tower is, "
    "and (2) how many Eiffel Towers stacked on top of each other would reach the Burj Khalifa's height."
)


def main():
    print("=" * 60)
    print("QUERY:", TEST_QUERY)

    print("\n" + "=" * 60)
    print("SINGLE AGENT")
    print("=" * 60)
    single = TokenTracker()
    single_answer = ask_llm(TEST_QUERY, single)
    print("\nFINAL ANSWER:\n" + single_answer)

    print("\n" + "=" * 60)
    print("MULTI AGENT")
    print("=" * 60)
    multi = TokenTracker()
    multi_answer = ask_manager_llm(TEST_QUERY, multi)
    print("\nFINAL ANSWER:\n" + multi_answer)

    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    single.report("single agent")
    multi.report("multi agent")

    diff = multi.total - single.total
    winner = "single agent" if diff > 0 else "multi agent"
    print(f"\nSingle: {single.total} tokens over {single.calls} LLM calls")
    print(f"Multi:  {multi.total} tokens over {multi.calls} LLM calls")
    print(f"The {winner} used fewer tokens (by {abs(diff)}, {abs(diff) / max(single.total, 1):.0%} of single).")


if __name__ == "__main__":
    main()
