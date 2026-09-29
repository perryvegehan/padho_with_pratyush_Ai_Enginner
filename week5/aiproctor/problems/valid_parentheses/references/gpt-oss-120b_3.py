def is_valid(s: str) -> bool:
    """
    Returns True if the string s contains a valid sequence of brackets,
    otherwise returns False.
    """
    # Mapping of closing brackets to their corresponding opening brackets
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []

    for ch in s:
        if ch in "({[":
            stack.append(ch)
        elif ch in ")}]":
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            # If any other character appears, the string is considered invalid.
            # The problem statement says the string contains only brackets,
            # but we guard against unexpected input.
            return False

    # If stack is empty, all brackets were matched correctly.
    return not stack


if __name__ == "__main__":
    s = input().strip()
    print("true" if is_valid(s) else "false")
