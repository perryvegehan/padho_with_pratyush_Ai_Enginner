def is_valid(s: str) -> bool:
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
            # Invalid character (not expected in the problem statement)
            return False

    # All opening brackets must be closed
    return not stack

# Read input, evaluate, and print result
s = input().strip()
print("true" if is_valid(s) else "false")
