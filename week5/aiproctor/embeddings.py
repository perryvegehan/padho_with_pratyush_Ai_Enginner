"""
Embeddings vs MOSS -- same kaam, AI engineering wala tareeka.

Har submission ko ek code-embedding model se vector mein badlo, phir cosine similarity.
    - Embeddings: "logic" pakadte hain (loop ko recursion mein badlo, phir bhi similar)
    - MOSS: fast, free, aur batata hai KAUNSI LINE match hui (explainable)

Lesson: har problem pe LLM/embedding mat thopo. Pehle dekho data kya bolta hai.

Model: jinaai/jina-embeddings-v2-base-code (fastembed, local, ~640MB, pehli baar download hota hai)

Run:
    uv run embeddings.py longest_substring
"""

import argparse
from itertools import combinations

import numpy as np
from fastembed import TextEmbedding

from config import ROOT, load_problem
from moss import check_class, compare, fingerprint


EMBED_MODEL = "jinaai/jina-embeddings-v2-base-code"

_model = None


def embed(codes: list[str]) -> np.ndarray:
    global _model
    if _model is None:
        _model = TextEmbedding(EMBED_MODEL)
    vectors = np.array(list(_model.embed(codes)))
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)  # normalize -> dot = cosine


def cosine_pairs(submissions: dict[str, str]) -> dict[tuple[str, str], float]:
    names = list(submissions)
    vectors = embed([submissions[n] for n in names])
    sims = vectors @ vectors.T
    return {(names[i], names[j]): float(sims[i, j]) for i, j in combinations(range(len(names)), 2)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("problem")
    parser.add_argument("--top", type=int, default=15)
    args = parser.parse_args()

    problem = load_problem(args.problem)
    cos = cosine_pairs(problem["submissions"])
    moss = {(p["a"], p["b"]): p["score"] for p in check_class(args.problem)}

    print(f"\nEmbeddings vs MOSS for '{args.problem}' (sorted by embedding similarity)\n")
    print(f"{'pair':<22}{'embedding':>10}{'MOSS':>8}")
    for pair, c in sorted(cos.items(), key=lambda kv: kv[1], reverse=True)[: args.top]:
        print(f"{pair[0] + ' - ' + pair[1]:<22}{c:>10.2f}{moss[pair]:>8.0%}")

    values = list(cos.values())
    print(f"\nEmbedding range across ALL pairs: {min(values):.2f} .. {max(values):.2f}")
    print("(sab ek hi question solve kar rahe hain, to sab thode-bahut similar dikhte hain)")

    # --- loop -> recursion demo ---
    recursive = (ROOT / "samples" / "alice_recursive.py").read_text(encoding="utf-8")
    if args.problem == "longest_substring":
        alice = problem["submissions"]["alice"]
        moss_score = compare(fingerprint(alice), fingerprint(recursive))["score"]
        vectors = embed([alice, recursive])
        print("\nLogic copy: alice ka loop -> recursion mein likha (samples/alice_recursive.py)")
        print(f"  MOSS       {moss_score:.0%}")
        print(f"  embedding  {float(vectors[0] @ vectors[1]):.2f}")

        # lekin kya ye number honest students se alag hai?
        honest = ["karan", "lakshya", "meera", "nikhil"]
        print("\nComparison -- alice vs students jinhone KHUD likha:")
        for name in honest:
            print(f"  alice - {name:<8} embedding {cos[('alice', name)]:.2f}   MOSS {moss[('alice', name)]:.0%}")
