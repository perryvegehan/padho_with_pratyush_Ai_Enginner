def is_valid(s):
    """Return True if brackets in s are balanced and correctly nested."""
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            # ignore any other characters (not expected per problem statement)
            pass
    return not stack


# Read input, evaluate, and print result
if __name__ == "__main__":
    s = input().strip()
    print("true" if is_valid(s) else "false")
