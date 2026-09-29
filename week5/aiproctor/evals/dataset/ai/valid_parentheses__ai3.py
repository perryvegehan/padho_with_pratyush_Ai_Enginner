import sys

def is_balanced(s: str) -> bool:
    """Return True if the string s contains a balanced and properly nested
    sequence of parentheses, brackets and braces."""
    pairs = {')': '(', ']': '[', '}': '{'}
    opening = set(pairs.values())
    stack = []

    for ch in s:
        if ch in opening:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        # any other character is ignored (problem guarantees only brackets)

    return not stack


def main():
    s = sys.stdin.readline().strip()
    print("true" if is_balanced(s) else "false")


if __name__ == "__main__":
    main()
