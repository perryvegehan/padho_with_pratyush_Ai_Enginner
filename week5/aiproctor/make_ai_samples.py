"""
"AI wale students" banao -- asli LLM output, haath se nahi likha.

Students alag tarah se poochte hain (reference.py wale prompt se alag), taaki
reference match "fixed" na lage -- match hua to isliye kyunki AI ka style hi aisa hai.

    uv run make_ai_samples.py

Writes:
    problems/longest_substring/submissions/<name>.py   (demo class ke 6 AI students)
    evals/dataset/ai/<problem>__<n>.py                 (evals ke liye AI samples)
"""

from config import PROBLEMS_DIR, ROOT, load_problem
from reference import REF_MODELS, ask_for_solution


STUDENT_PROMPTS = [
    "solve this in python\n\n{statement}\n\nReply with the code in a single ```python block.",
    "{statement}\n\ngive me python code for this. it should read input and print output. "
    "Reply with the code in a single ```python block.",
    "I have an online assessment question:\n\n{statement}\n\nWrite an efficient Python solution. "
    "Reply with the code in a single ```python block.",
]

DEMO_AI_STUDENTS = ["eshan", "farah", "gaurav", "heena", "ishaan", "jaya"]
EVAL_PROBLEMS = ["longest_substring", "two_sum", "valid_parentheses"]
EVAL_SAMPLES_PER_PROBLEM = 4


def write_sample(path, problem: dict, n: int):
    if path.exists():
        print(f"  cached   {path.relative_to(ROOT)}")
        return
    model = REF_MODELS[n % len(REF_MODELS)]
    prompt = STUDENT_PROMPTS[n % len(STUDENT_PROMPTS)].format(statement=problem["statement"])
    path.write_text(ask_for_solution(prompt, model), encoding="utf-8")
    print(f"  wrote    {path.relative_to(ROOT)}  ({model})")


if __name__ == "__main__":
    demo = load_problem("longest_substring")
    for n, name in enumerate(DEMO_AI_STUDENTS):
        write_sample(PROBLEMS_DIR / "longest_substring" / "submissions" / f"{name}.py", demo, n)

    out = ROOT / "evals" / "dataset" / "ai"
    out.mkdir(parents=True, exist_ok=True)
    for problem_id in EVAL_PROBLEMS:
        problem = load_problem(problem_id)
        for n in range(EVAL_SAMPLES_PER_PROBLEM):
            write_sample(out / f"{problem_id}__ai{n + 1}.py", problem, n + 1)
