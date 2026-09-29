"""
Poori class ka scan -- offline, free (koi LLM call nahi).

Har student ke liye saare cheap checks chalao, aur batao kisko agent ke paas bhejna hai.
Agent (agent.py) mehenga hai, isliye sirf suspicious logon pe chalate hain.

Run:
    uv run main.py longest_substring
"""

import argparse

from ai_judge import heuristic_score
from config import load_problem
from moss import FLAG_AT, matches_for
from reference import reference_match
from same_bug import wrong_answers


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("problem")
    args = parser.parse_args()

    problem = load_problem(args.problem)
    signatures = wrong_answers(args.problem)

    print(f"\nClass scan: {args.problem} ({len(problem['submissions'])} submissions)\n")
    print(f"{'student':<10}{'top classmate':>18}{'same bug with':>16}{'AI ref':>8}{'AI style':>10}   send to agent?")

    for student, code in problem["submissions"].items():
        top = matches_for(args.problem, student, top=1)
        classmate = f"{top[0]['classmate']} {top[0]['similarity']:.0%}" if top else "-"
        same_bug = [s for s, sig in signatures.items() if sig and sig == signatures[student] and s != student]
        ref = reference_match(args.problem, student)
        style = heuristic_score(code, problem["starter"])

        bug_text = f"{same_bug[0]} +{len(same_bug) - 1}" if len(same_bug) > 1 else (same_bug[0] if same_bug else "-")

        reasons = []
        if top and top[0]["similarity"] >= FLAG_AT:
            reasons.append("copy")
        if same_bug:
            reasons.append("same bug")
        if ref["flag"]:
            reasons.append("AI ref")
        if style["flag"]:
            reasons.append("AI style")

        print(
            f"{student:<10}{classmate:>18}{bug_text:>16}"
            f"{ref['best_match']:>8.0%}{style['score']:>10.2f}   {'YES: ' + ', '.join(reasons) if reasons else ''}"
        )

    print("\nKisi ek pe agent chalao:  uv run agent.py", args.problem, "<student>")
    print("Yaad rakho: flag = sawaal poocho. Flag != cheater.")
