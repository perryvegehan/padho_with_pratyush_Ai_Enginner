def is_valid(s):
    """
    Return True if the string s contains balanced and properly nested brackets.
    Supported brackets: (), [], {}
    """
    # Mapping of closing to opening brackets
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []

    for ch in s:
        if ch in pairs.values():          # opening bracket
            stack.append(ch)
        elif ch in pairs:                 # closing bracket
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            # According to the problem statement, s contains only brackets,
            # but we ignore any other characters just in case.
            continue

    return not stack  # True if no unmatched opening brackets remain

if __name__ == "__main__":
    s = input().strip()
    print("true" if is_valid(s) else "false")
