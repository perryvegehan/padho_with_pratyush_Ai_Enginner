"""Test scenarios from prompt.md. Run: uv run test_scenarios.py"""

from main import simulate


def tc1():
    print("\n" + "=" * 70 + "\nTC1: unrelated -> partial -> reject & reorder -> unavailable => END (order retries)\n" + "=" * 70)
    s = simulate(["what is the weather today?", "I want 5 burgers", "no, give me 2 pasta instead"])
    assert s["order_retries"] == 0, s
    assert s["final_result"] == "NOT COMPLETED: order attempts exhausted", s["final_result"]


def tc2():
    print("\n" + "=" * 70 + "\nTC2: available -> cook fail, cook ok -> serve fail -> cook ok -> serve ok => SUCCESS\n" + "=" * 70)
    s = simulate(["2 pizzas"], cook_outcomes=[False, True, True], serve_outcomes=[False, True])
    assert s["final_result"] == "COMPLETED", s["final_result"]
    assert s["cook_retries"] == 0 and s["serve_retries"] == 1, s


def tc3():
    print("\n" + "=" * 70 + "\nTC3: partial -> reject -> available -> cook fail, ok -> serve fail -> cook ok -> serve fail => FAIL (cook exhausted)\n" + "=" * 70)
    s = simulate(["5 burgers", "no, give me 1 dosa"], cook_outcomes=[False, True, True], serve_outcomes=[False, False])
    assert s["final_result"] == "NOT COMPLETED: serve failed and cook retries exhausted", s["final_result"]
    assert s["cook_retries"] == 0, s


if __name__ == "__main__":
    results = {}
    for tc in (tc1, tc2, tc3):
        try:
            tc()
            results[tc.__name__] = "PASS"
        except AssertionError as e:
            results[tc.__name__] = f"FAIL: {e}"
    print("\n" + "=" * 70)
    for name, r in results.items():
        print(f"{name.upper()}: {r}")
