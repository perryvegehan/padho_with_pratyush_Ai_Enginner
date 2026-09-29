"""
Evals: "clean coder bhi flag hoga kya?"

Detector banana easy hai. Ye NAAPNA ki wo kitna galat hai -- ye asli kaam hai.

Dataset (label = folder ka naam):
    dataset/ai/            -> AI ne likha         (positive)
    dataset/human_clean/   -> insaan, saaf code   (negative)
    dataset/human_messy/   -> insaan, messy code  (negative)
File name format: <problem_id>__<kuch_bhi>.py   (problem_id se reference solutions milte hain)

Apna code daalo: dataset/human_clean/longest_substring__pratyush.py -- dekho tum flag hote ho ya nahi.

Run (aiproctor folder se):
    uv run evals/run_evals.py            # heuristic + reference match (free)
    uv run evals/run_evals.py --llm      # + LLM judge (results cache ho jaate hain)
    uv run evals/run_evals.py --llm -v   # har sample ka score
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_judge import heuristic_score, llm_judge  # noqa: E402
from config import load_problem, print_tokens  # noqa: E402
from reference import reference_match  # noqa: E402


DATASET = Path(__file__).parent / "dataset"
LLM_CACHE = Path(__file__).parent / "llm_cache.json"
LABELS = ["ai", "human_clean", "human_messy"]


def load_dataset() -> list[dict]:
    samples = []
    for label in LABELS:
        for f in sorted((DATASET / label).glob("*.py")):
            samples.append({
                "name": f"{label}/{f.stem}",
                "label": label,
                "is_ai": label == "ai",
                "problem": f.stem.split("__")[0],
                "code": f.read_text(encoding="utf-8"),
            })
    return samples


def cached_llm_judge(sample: dict, cache: dict) -> dict:
    key = hashlib.sha1(sample["code"].encode()).hexdigest()
    if key not in cache:
        problem = load_problem(sample["problem"])
        cache[key] = llm_judge(sample["code"], problem["statement"])
        LLM_CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    return cache[key]


def run_detectors(samples: list[dict], use_llm: bool):
    cache = json.loads(LLM_CACHE.read_text(encoding="utf-8")) if LLM_CACHE.exists() else {}

    for s in samples:
        problem = load_problem(s["problem"])
        h = heuristic_score(s["code"], problem["starter"])
        r = reference_match(s["problem"], None, code=s["code"])
        s["scores"] = {"heuristic": h["score"], "reference": r["best_match"]}
        s["flags"] = {"heuristic": h["flag"], "reference": r["flag"]}

        if use_llm:
            l = cached_llm_judge(s, cache)
            s["scores"]["llm_judge"] = l["ai_likelihood"]
            s["flags"]["llm_judge"] = l["flag"]

        # combined: kam se kam 2 detectors agree karein tabhi flag
        s["flags"]["combined (2+ agree)"] = sum(s["flags"].values()) >= 2


def metrics(samples: list[dict], detector: str) -> dict:
    tp = sum(1 for s in samples if s["is_ai"] and s["flags"][detector])
    fn = sum(1 for s in samples if s["is_ai"] and not s["flags"][detector])
    fp = sum(1 for s in samples if not s["is_ai"] and s["flags"][detector])
    tn = sum(1 for s in samples if not s["is_ai"] and not s["flags"][detector])

    def fp_in(label):
        group = [s for s in samples if s["label"] == label]
        return sum(1 for s in group if s["flags"][detector]), len(group)

    return {
        "precision": tp / (tp + fp) if tp + fp else 0.0,  # flag kiya, usme se kitne sach mein AI
        "recall": tp / (tp + fn) if tp + fn else 0.0,  # saare AI mein se kitne pakde
        "fpr": fp / (fp + tn) if fp + tn else 0.0,  # saare insaano mein se kitne galti se flag
        "fp_clean": fp_in("human_clean"),
        "fp_messy": fp_in("human_messy"),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", action="store_true", help="LLM judge bhi chalao")
    parser.add_argument("-v", "--verbose", action="store_true", help="har sample ka score dikhao")
    args = parser.parse_args()

    samples = load_dataset()
    counts = {label: sum(1 for s in samples if s["label"] == label) for label in LABELS}
    print(f"Dataset: {len(samples)} samples  {counts}")

    run_detectors(samples, args.llm)
    detectors = list(samples[0]["flags"])

    if args.verbose:
        print(f"\n{'sample':<42}" + "".join(f"{d[:10]:>12}" for d in detectors[:-1]) + "   flagged?")
        for s in samples:
            row = "".join(f"{s['scores'][d]:>12.2f}" for d in detectors[:-1])
            print(f"{s['name']:<42}{row}   {'YES' if s['flags'][detectors[-1]] else ''}")

    print(f"\n{'detector':<22}{'precision':>10}{'recall':>8}{'FPR':>7}{'FP clean':>10}{'FP messy':>10}")
    for d in detectors:
        m = metrics(samples, d)
        clean = f"{m['fp_clean'][0]}/{m['fp_clean'][1]}"
        messy = f"{m['fp_messy'][0]}/{m['fp_messy'][1]}"
        print(f"{d:<22}{m['precision']:>10.0%}{m['recall']:>8.0%}{m['fpr']:>7.0%}{clean:>10}{messy:>10}")

    wrongly_flagged = [s["name"] for s in samples if not s["is_ai"] and s["flags"][detectors[-1]]]
    missed = [s["name"] for s in samples if s["is_ai"] and not s["flags"][detectors[-1]]]
    print(f"\nHumans flagged by combined detector: {wrongly_flagged or 'none'}")
    print(f"AI samples missed by combined detector: {missed or 'none'}")

    if args.llm:
        print_tokens()
