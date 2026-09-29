"""
STEP 1 of MOSS: Tokenizer (lexer)

Code ko characters ki jagah TOKENS mein todte hain, aur phir unhe "normalize" karte hain:
    - variable / function names  ->  ID
    - numbers                    ->  NUM
    - strings                    ->  STR
    - whitespace + comments      ->  gayab

Isliye   sum += arr[i]   aur   total += nums[j]   dono ban jaate hain:
         ID += ID [ ID ]

Ye lexer ek chhota DFA hai (Theory of Computation wala): pehla character dekh ke
state choose karo (identifier / number / string / comment / operator), phir us state
mein tab tak characters khao jab tak state khatam na ho.
"""

import keyword
from dataclasses import dataclass


# keywords waise hi rehte hain -- "for" ko rename nahi kar sakte
KEYWORDS = set(keyword.kwlist)

# builtins + common methods bhi waise hi rakhte hain -- LEKIN sirf jab call ho rahe hon
# (len(...), .append(...)). Student inhe rename nahi kar sakta, to ye asli structure batate hain.
# Agar kisi ne "sum" naam ka variable banaya, to wo normal ID hi banega.
KEEP_NAMES = {
    "len", "range", "print", "input", "int", "str", "float", "list", "dict", "set", "tuple",
    "max", "min", "sum", "abs", "sorted", "reversed", "enumerate", "zip", "map", "filter",
    "append", "pop", "get", "add", "remove", "split", "strip", "join", "items", "keys",
    "values", "readline", "stdin", "sys", "self", "ord", "chr", "index", "count", "sort",
    "isalnum", "lower", "__name__", "__main__",
}

# lambi wali pehle, taaki "**=" ko "*" "*" "=" na samjhe
OPERATORS = sorted(
    [
        "**=", "//=", ">>=", "<<=", "->", ":=",
        "==", "!=", "<=", ">=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=",
        "**", "//", "<<", ">>",
        "+", "-", "*", "/", "%", "=", "<", ">", "&", "|", "^", "~",
        "(", ")", "[", "]", "{", "}", ",", ":", ".", ";", "@",
    ],
    key=len,
    reverse=True,
)

STRING_PREFIXES = {"f", "r", "b", "u", "rb", "br", "fr", "rf"}


@dataclass
class Token:
    kind: str  # ID / NUM / STR / KEYWORD / OP
    text: str  # original text, jaise "total"
    norm: str  # normalized, jaise "ID"
    line: int  # kaunsi line pe tha (matched lines highlight karne ke liye)


def read_string(code: str, i: int) -> int:
    """i pe quote shuru hota hai. String ke khatam hone ke baad wala index return karo."""
    quote = code[i] * 3 if code[i : i + 3] in ('"""', "'''") else code[i]
    j = i + len(quote)
    while j < len(code):
        if code[j] == "\\":
            j += 2
            continue
        if code.startswith(quote, j):
            return j + len(quote)
        j += 1
    return j


def tokenize(code: str) -> list[Token]:
    tokens = []
    i = 0
    line = 1

    while i < len(code):
        ch = code[i]

        # --- state: whitespace -> skip ---
        if ch.isspace():
            if ch == "\n":
                line += 1
            i += 1

        # --- state: comment -> line ke end tak skip ---
        elif ch == "#":
            while i < len(code) and code[i] != "\n":
                i += 1

        # --- state: string ---
        elif ch in "\"'":
            end = read_string(code, i)
            text = code[i:end]
            tokens.append(Token("STR", text, "STR", line))
            line += text.count("\n")
            i = end

        # --- state: identifier / keyword ---
        elif ch.isalpha() or ch == "_":
            j = i
            while j < len(code) and (code[j].isalnum() or code[j] == "_"):
                j += 1
            word = code[i:j]

            if word.lower() in STRING_PREFIXES and j < len(code) and code[j] in "\"'":
                # f"..." / r"..." jaisa string hai, identifier nahi
                end = read_string(code, j)
                text = code[i:end]
                tokens.append(Token("STR", text, "STR", line))
                line += text.count("\n")
                i = end
                continue

            if word in KEYWORDS:
                tokens.append(Token("KEYWORD", word, word, line))
            else:
                tokens.append(Token("ID", word, "ID", line))
            i = j

        # --- state: number ---
        elif ch.isdigit():
            j = i
            while j < len(code) and (code[j].isalnum() or code[j] in "._"):
                j += 1
            tokens.append(Token("NUM", code[i:j], "NUM", line))
            i = j

        # --- state: operator / punctuation ---
        else:
            for op in OPERATORS:
                if code.startswith(op, i):
                    tokens.append(Token("OP", op, op, line))
                    i += len(op)
                    break
            else:
                i += 1  # koi ajeeb character, ignore

    # builtin tabhi rakho jab call ho raha ho:  len(   ya   .append
    for k, t in enumerate(tokens):
        if t.kind == "ID" and t.text in KEEP_NAMES:
            called = k + 1 < len(tokens) and tokens[k + 1].text == "("
            method = k > 0 and tokens[k - 1].text == "."
            if called or method or t.text.startswith("__"):
                t.norm = t.text

    return tokens


def normalize(code: str) -> str:
    return " ".join(t.norm for t in tokenize(code))


if __name__ == "__main__":
    a = "sum += arr[i]   # adding"
    b = "total += nums[j]"

    print(f"{a!r:30} -> {normalize(a)}")
    print(f"{b!r:30} -> {normalize(b)}")
    print("Same?", normalize(a) == normalize(b))

    print("\nFull tokens for a function:")
    code = 'def best(s):\n    seen = {}  # last index\n    return len(s) + 1\n'
    for t in tokenize(code):
        print(f"  line {t.line}  {t.kind:<8} {t.text!r:<10} -> {t.norm}")
