import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# SETUP  (keys come from the .env at the repo root)
# ============================================================

load_dotenv()

# Windows terminal LLM ke unicode characters (jaise ‑) pe crash na kare
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# free tier ka rate limit chhota hai, SDK khud wait karke retry karega
groq = Groq(api_key=os.getenv("GROQ_API_KEY"), max_retries=10)

MODEL = "openai/gpt-oss-120b"

ROOT = Path(__file__).parent
PROBLEMS_DIR = ROOT / "problems"


# ============================================================
# PROBLEM LOADER
# ============================================================
# problems/<problem_id>/
#     problem.md        -> question
#     starter.py        -> base file (jo code sabko diya gaya tha)
#     submissions/*.py  -> students ka code
#     references/*.py   -> AI (LLM) ke solutions, reference.py banata hai


def read_folder(folder: Path) -> dict[str, str]:
    if not folder.exists():
        return {}
    return {f.stem: f.read_text(encoding="utf-8") for f in sorted(folder.glob("*.py"))}


def load_problem(problem_id: str) -> dict:
    folder = PROBLEMS_DIR / problem_id
    if not folder.exists():
        raise SystemExit(f"No problem called '{problem_id}'. Options: {list_problems()}")

    return {
        "id": problem_id,
        "statement": (folder / "problem.md").read_text(encoding="utf-8"),
        "starter": (folder / "starter.py").read_text(encoding="utf-8"),
        "submissions": read_folder(folder / "submissions"),
        "references": read_folder(folder / "references"),
    }


def list_problems() -> list[str]:
    return sorted(p.name for p in PROBLEMS_DIR.iterdir() if p.is_dir())


# ============================================================
# TOKEN USAGE  (har LLM call yahan count hota hai)
# ============================================================

TOKENS = {}  # label -> {"calls": .., "total": ..}


def track(label: str, usage):
    entry = TOKENS.setdefault(label, {"calls": 0, "total": 0})
    entry["calls"] += 1
    entry["total"] += usage.total_tokens


def print_tokens():
    print("\n--- Token usage ---")
    for label, e in TOKENS.items():
        print(f"{label:<14}{e['calls']:>4} calls{e['total']:>9} tokens")
    print(f"{'TOTAL':<14}{sum(e['calls'] for e in TOKENS.values()):>4} calls"
          f"{sum(e['total'] for e in TOKENS.values()):>9} tokens")
