"""
MOSS-style similarity: "kisne kisse copy kiya?"

Pipeline:
    code -> tokens (tokenizer.py) -> k-grams -> hash -> winnowing -> fingerprints
    do students ke fingerprints compare karo -> similarity %

Paper: Schleimer, Wilkerson, Aiken - "Winnowing: Local Algorithms for Document
Fingerprinting" (SIGMOD 2003). MOSS isi pe based hai.

Run:
    uv run moss.py longest_substring
    uv run moss.py longest_substring --no-filter
    uv run moss.py longest_substring --show alice bob
"""

import argparse
import hashlib
from dataclasses import dataclass, field
from itertools import combinations

from config import load_problem
from tokenizer import Token, tokenize


K = 5  # k-gram size: kitne tokens ka ek tukda
W = 4  # winnowing window: kitne hashes mein se ek minimum chunna hai

# koi fingerprint agar itne se ZYADA students mein hai, to wo "common code" hai -> ignore.
# Asli MOSS ka default ~10 hai; humari demo class chhoti hai to 4 rakha hai.
COMMON_THRESHOLD = 4

FLAG_AT = 0.5  # 50% se upar similarity -> review ke liye flag


# ============================================================
# STEP 2: k-grams + hashing
# ============================================================
# "ID = ID + NUM" jaise har 5 tokens ke overlapping window ka ek number (hash) banao.
# Asli MOSS rolling hash (Karp-Rabin) use karta hai taaki fast ho; hum simple hash use kar rahe hain.


def hash_kgram(norms: list[str]) -> int:
    digest = hashlib.blake2b(" ".join(norms).encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def kgram_hashes(tokens: list[Token], k: int = K) -> list[int]:
    norms = [t.norm for t in tokens]
    return [hash_kgram(norms[i : i + k]) for i in range(len(norms) - k + 1)]


# ============================================================
# STEP 3: winnowing
# ============================================================
# Saare hashes store karna mehenga hai. Isliye har W hashes ki window mein se
# sirf MINIMUM uthao. Guarantee: agar do files mein W+K-1 tokens ka same match hai,
# to wo zaroor pakda jayega.


def winnow(hashes: list[int], w: int = W) -> list[tuple[int, int]]:
    """Returns [(hash, position)] -- position = kaunse token se k-gram shuru hua."""
    if not hashes:
        return []
    if len(hashes) < w:
        pos = min(range(len(hashes)), key=lambda i: hashes[i])
        return [(hashes[pos], pos)]

    picked = []
    last_pos = -1
    for start in range(len(hashes) - w + 1):
        window = range(start, start + w)
        # minimum; tie ho to sabse right wala (paper ka "robust winnowing")
        pos = min(window, key=lambda i: (hashes[i], -i))
        if pos != last_pos:
            picked.append((hashes[pos], pos))
            last_pos = pos
    return picked


@dataclass
class Fingerprint:
    tokens: list[Token]
    positions: dict[int, list[int]] = field(default_factory=dict)  # hash -> token positions

    @property
    def hashes(self) -> set[int]:
        return set(self.positions)

    def lines_for(self, h: int) -> set[int]:
        """Is hash wale k-gram ne kaunsi lines cover ki?"""
        lines = set()
        for pos in self.positions.get(h, []):
            lines.update(t.line for t in self.tokens[pos : pos + K])
        return lines


def fingerprint(code: str) -> Fingerprint:
    tokens = tokenize(code)
    fp = Fingerprint(tokens)
    for h, pos in winnow(kgram_hashes(tokens)):
        fp.positions.setdefault(h, []).append(pos)
    return fp


# ============================================================
# STEP 4: compare
# ============================================================


def compare(a: Fingerprint, b: Fingerprint, ignore: set[int] = frozenset()) -> dict:
    ha = a.hashes - ignore
    hb = b.hashes - ignore
    shared = ha & hb

    pct_a = len(shared) / len(ha) if ha else 0.0  # A ka kitna hissa B mein mila
    pct_b = len(shared) / len(hb) if hb else 0.0  # B ka kitna hissa A mein mila

    lines_a, lines_b = set(), set()
    for h in shared:
        lines_a |= a.lines_for(h)
        lines_b |= b.lines_for(h)

    return {
        "score": max(pct_a, pct_b),
        "pct_a": pct_a,
        "pct_b": pct_b,
        "shared": len(shared),
        "lines_a": sorted(lines_a),
        "lines_b": sorted(lines_b),
    }


# ============================================================
# STEP 5: common code ignore karo
# ============================================================
# (a) starter code (base file) jo sabko diya gaya tha
# (b) jo fingerprint bahut saare students mein hai -- easy question pe sab same likhte hain


def common_hashes(fps: dict[str, Fingerprint], starter: str, threshold: int | None = COMMON_THRESHOLD) -> set[int]:
    ignore = set(fingerprint(starter).hashes)

    if threshold is not None:
        counts = {}
        for fp in fps.values():
            for h in fp.hashes:
                counts[h] = counts.get(h, 0) + 1
        ignore |= {h for h, c in counts.items() if c > threshold}

    return ignore


def check_class(problem_id: str, use_filter: bool = True) -> list[dict]:
    """Har pair of students compare karo, sabse suspicious pehle."""
    problem = load_problem(problem_id)
    fps = {name: fingerprint(code) for name, code in problem["submissions"].items()}
    ignore = common_hashes(fps, problem["starter"], COMMON_THRESHOLD if use_filter else None)

    pairs = []
    for a, b in combinations(fps, 2):
        result = compare(fps[a], fps[b], ignore)
        pairs.append({"a": a, "b": b, **result})

    return sorted(pairs, key=lambda p: p["score"], reverse=True)


def matches_for(problem_id: str, student: str, top: int = 3) -> list[dict]:
    """Ek student ke sabse similar classmates (agent ka tool yahi use karta hai)."""
    pairs = [p for p in check_class(problem_id) if student in (p["a"], p["b"])]
    out = []
    for p in pairs[:top]:
        mine = "a" if p["a"] == student else "b"
        other = "b" if mine == "a" else "a"
        out.append({
            "classmate": p[other],
            "similarity": round(p["score"], 2),
            "my_code_matched": round(p[f"pct_{mine}"], 2),
            "their_code_matched": round(p[f"pct_{other}"], 2),
            "my_matched_lines": p[f"lines_{mine}"],
        })
    return out


# ============================================================
# PRINTING
# ============================================================


def print_report(pairs: list[dict], top: int = 10):
    print(f"\n{'pair':<22}{'similarity':>11}{'A matched':>11}{'B matched':>11}{'shared fp':>11}")
    for p in pairs[:top]:
        flag = "  <-- FLAG" if p["score"] >= FLAG_AT else ""
        print(
            f"{p['a'] + ' - ' + p['b']:<22}{p['score']:>10.0%}{p['pct_a']:>11.0%}"
            f"{p['pct_b']:>11.0%}{p['shared']:>11}{flag}"
        )


def show_pair(problem_id: str, a: str, b: str):
    """Dono files side by side, matched lines pe >> ka nishaan."""
    pair = next(p for p in check_class(problem_id) if {p["a"], p["b"]} == {a, b})
    if pair["a"] != a:
        pair["lines_a"], pair["lines_b"] = pair["lines_b"], pair["lines_a"]

    subs = load_problem(problem_id)["submissions"]
    left = subs[a].splitlines()
    right = subs[b].splitlines()
    width = max(len(line) for line in left) + 2

    print(f"\n{a} vs {b}: {pair['score']:.0%} similar  (>> = matched line)\n")
    print(f"     {a:<{width}}      {b}")
    for i in range(max(len(left), len(right))):
        l = left[i] if i < len(left) else ""
        r = right[i] if i < len(right) else ""
        ml = ">>" if i + 1 in pair["lines_a"] else "  "
        mr = ">>" if i + 1 in pair["lines_b"] else "  "
        print(f"{ml} {i + 1:>2} {l:<{width}} {mr} {i + 1:>2} {r}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("problem")
    parser.add_argument("--no-filter", action="store_true", help="common-code filter band karo")
    parser.add_argument("--show", nargs=2, metavar=("A", "B"), help="do students side by side dikhao")
    parser.add_argument("--top", type=int, default=12)
    args = parser.parse_args()

    if args.show:
        show_pair(args.problem, *args.show)
    else:
        label = "WITHOUT" if args.no_filter else f"WITH (threshold={COMMON_THRESHOLD})"
        print(f"MOSS report for '{args.problem}' -- common-code filter {label}")
        print_report(check_class(args.problem, use_filter=not args.no_filter), args.top)
