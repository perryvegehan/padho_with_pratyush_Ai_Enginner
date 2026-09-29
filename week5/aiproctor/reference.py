"""
Reference match: "ChatGPT ka answer toh nahi?"

Problem: agar 20 students ne ChatGPT use kiya, to unka code ek-doosre jaisa hoga,
aur MOSS ka common-code filter use "common" samajh ke IGNORE kar dega.

Solution: khud AI se solution likhwao (alag models, kai baar, temperature ke saath),
aur unhe "fake students" ki tarah pool mein daalo. Phir har student ko in AI answers
se compare karo. Yahan common-code filter NAHI lagta -- AI jaisa hona hi toh signal hai.

Run:
    uv run reference.py generate longest_substring     # AI solutions banao (cache ho jaate hain)
    uv run reference.py match longest_substring        # har student vs AI
"""

import argparse
import re

from groq import BadRequestError

from config import PROBLEMS_DIR, groq, load_problem
from moss import fingerprint, compare


# jitne alag AI models, utna accha -- har model ka apna "style" hota hai
REF_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
RUNS_PER_MODEL = 3
TEMPERATURE = 0.8  # thoda variation chahiye, warna teeno runs same aayenge

REF_FLAG_AT = 0.5  # student ke code ka 50%+ kisi AI answer mein mila -> flag


# ============================================================
# AI SE SOLUTION LIKHWAO
# ============================================================


def extract_code(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, flags=re.DOTALL)
    code = max(blocks, key=len) if blocks else text
    return code.strip() + "\n"


def ask_for_solution(prompt: str, model: str, temperature: float = TEMPERATURE) -> str:
    for _ in range(3):
        try:
            response = groq.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You have no tools. Answer in plain markdown."},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
            )
            return extract_code(response.choices[0].message.content)
        except BadRequestError:
            # gpt-oss kabhi kabhi bina tools ke bhi "tool call" invent kar deta hai; groq reject karta hai
            continue
    raise RuntimeError(f"{model} kept failing")


def reference_prompt(problem: dict) -> str:
    # wahi jo ek candidate copy-paste karega: question + starter code
    return (
        f"{problem['statement']}\n\n"
        f"Starter code:\n```python\n{problem['starter']}```\n\n"
        "Write the complete Python solution. Reply with the code in a single ```python block."
    )


def generate_references(problem_id: str, force: bool = False):
    problem = load_problem(problem_id)
    folder = PROBLEMS_DIR / problem_id / "references"
    folder.mkdir(exist_ok=True)

    for model in REF_MODELS:
        short = model.split("/")[-1]
        for run in range(1, RUNS_PER_MODEL + 1):
            path = folder / f"{short}_{run}.py"
            if path.exists() and not force:
                print(f"  cached   {path.name}")
                continue
            try:
                path.write_text(ask_for_solution(reference_prompt(problem), model), encoding="utf-8")
                print(f"  wrote    {path.name}")
            except Exception as e:
                print(f"  failed   {path.name}: {e}")


# ============================================================
# STUDENT vs AI
# ============================================================


def reference_match(problem_id: str, student: str, code: str | None = None) -> dict:
    problem = load_problem(problem_id)
    if not problem["references"]:
        raise SystemExit(f"No references yet. Run: uv run reference.py generate {problem_id}")

    code = code if code is not None else problem["submissions"][student]
    mine = fingerprint(code)
    ignore = fingerprint(problem["starter"]).hashes  # sirf starter code ignore

    best = {"reference": None, "score": 0.0, "lines": []}
    union = set()
    for name, ref_code in problem["references"].items():
        ref = fingerprint(ref_code)
        result = compare(mine, ref, ignore)
        union |= (mine.hashes - ignore) & ref.hashes
        # pct_a = mere code ka kitna hissa is AI answer mein hai
        if result["pct_a"] > best["score"]:
            best = {"reference": name, "score": result["pct_a"], "lines": result["lines_a"]}

    total = len(mine.hashes - ignore)
    return {
        "best_reference": best["reference"],
        "best_match": round(best["score"], 2),
        "any_reference_coverage": round(len(union) / total, 2) if total else 0.0,
        "matched_lines": best["lines"],
        "flag": best["score"] >= REF_FLAG_AT,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["generate", "match"])
    parser.add_argument("problem")
    parser.add_argument("--force", action="store_true", help="cache ignore karke dobara generate karo")
    args = parser.parse_args()

    if args.action == "generate":
        generate_references(args.problem, args.force)
    else:
        problem = load_problem(args.problem)
        print(f"\nStudent vs {len(problem['references'])} AI solutions ({args.problem})\n")
        print(f"{'student':<10}{'best AI match':>15}{'coverage':>10}   closest reference")
        for student in problem["submissions"]:
            r = reference_match(args.problem, student)
            flag = "  <-- FLAG" if r["flag"] else ""
            print(f"{student:<10}{r['best_match']:>15.0%}{r['any_reference_coverage']:>10.0%}   {r['best_reference']}{flag}")
