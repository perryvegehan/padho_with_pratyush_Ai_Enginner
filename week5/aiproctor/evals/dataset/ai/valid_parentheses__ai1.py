# Valid Parentheses checker
# Reads a single line from stdin and prints "true" if the brackets are balanced,
# otherwise prints "false".

def is_balanced(s: str) -> bool:
    stack = []
    # Mapping of closing to opening brackets
    pairs = {')': '(', ']': '[', '}': '{'}
    open_brackets = set(pairs.values())

    for ch in s:
        if ch in open_brackets:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            # If any other character appears, it's considered invalid
            return False

    return not stack

if __name__ == "__main__":
    import sys
    # Read the input string (strip to remove any trailing newline)
    s = sys.stdin.readline().strip()
    print("true" if is_balanced(s) else "false")
