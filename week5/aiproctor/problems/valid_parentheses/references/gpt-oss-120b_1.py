def is_valid(s: str) -> bool:
    """
    Returns True if the string s contains a valid sequence of parentheses,
    brackets and braces; otherwise returns False.
    """
    # Mapping of closing brackets to their corresponding opening brackets
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
            # According to the problem statement the string contains only
            # the six bracket characters, but we ignore any other characters.
            continue

    # If stack is empty, all brackets were matched
    return not stack


if __name__ == "__main__":
    s = input().strip()
    print("true" if is_valid(s) else "false")
