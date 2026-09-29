"""
Same bug check: "galti bhi same, output bhi same?"

Do log alag-alag sahi solution likh sakte hain. Lekin do log alag-alag EK HI GALTI
karein, aur galat answer bhi same aaye -- ye coincidence bahut rare hai.

Har submission ko test cases pe chalao, aur jo students same test pe same GALAT output
dete hain unhe group karo.

Run:
    uv run same_bug.py longest_substring
"""

import argparse
import json
import subprocess
import sys

from config import PROBLEMS_DIR, load_problem


def run_code(code: str, stdin: str) -> str:
    try:
        result = subprocess.run(
            [sys.executable, "-c", code], input=stdin, capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else "ERROR"
    except subprocess.TimeoutExpired:
        return "TIMEOUT"


def wrong_answers(problem_id: str) -> dict[str, tuple]:
    """student -> (test ke hisaab se galat outputs ka 'signature'). Sab sahi = empty tuple."""
    problem = load_problem(problem_id)
    tests = json.loads((PROBLEMS_DIR / problem_id / "tests.json").read_text(encoding="utf-8"))

    signatures = {}
    for student, code in problem["submissions"].items():
        wrong = []
        for n, test in enumerate(tests):
            got = run_code(code, test["input"])
            if got != test["output"]:
                wrong.append((n, test["input"].strip(), got))
        signatures[student] = tuple(wrong)
    return signatures


def same_bug_groups(problem_id: str) -> list[dict]:
    groups = {}
    for student, signature in wrong_answers(problem_id).items():
        if signature:  # sirf galat wale
            groups.setdefault(signature, []).append(student)

    return [
        {
            "students": students,
            "wrong_tests": [{"input": inp, "their_output": got} for _, inp, got in signature],
        }
        for signature, students in groups.items()
        if len(students) >= 2
    ]


def same_bug_for(problem_id: str, student: str) -> dict:
    """Agent tool: is student ke jaisi galti aur kisne ki?"""
    signature = wrong_answers(problem_id)
    mine = signature[student]
    if not mine:
        return {"passes_all_tests": True, "same_wrong_output_as": []}
    return {
        "passes_all_tests": False,
        "failed_tests": [{"input": inp, "output": got} for _, inp, got in mine],
        "same_wrong_output_as": [s for s, sig in signature.items() if sig == mine and s != student],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("problem")
    args = parser.parse_args()

    groups = same_bug_groups(args.problem)
    if not groups:
        print("Koi do students same galti nahi kar rahe.")
    for g in groups:
        print(f"\nSame wrong answers: {', '.join(g['students'])}")
        for t in g["wrong_tests"]:
            print(f"    input {t['input']!r:<14} -> sab ne diya {t['their_output']!r}")
