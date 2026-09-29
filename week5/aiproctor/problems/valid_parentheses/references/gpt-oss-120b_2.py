def is_valid(s: str) -> bool:
    """
    Returns True if the string s contains a balanced and correctly nested
    sequence of parentheses, brackets and braces.
    """
    # Mapping of closing brackets to their corresponding opening brackets
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []

    for ch in s:
        if ch in pairs.values():            # opening bracket
            stack.append(ch)
        elif ch in pairs:                   # closing bracket
            if not stack or stack[-1] != pairs[ch]:
                return False                # mismatch or extra closing
            stack.pop()
        else:
            # According to the problem statement only the six characters appear,
            # but if any other character is present we treat the string as invalid.
            return False

    # If stack is empty, all opening brackets were matched
    return not stack


if __name__ == "__main__":
    s = input().strip()
    print("true" if is_valid(s) else "false")
