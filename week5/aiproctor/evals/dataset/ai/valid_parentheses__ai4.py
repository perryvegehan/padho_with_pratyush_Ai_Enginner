import sys

def is_balanced(s: str) -> bool:
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    opening = set(pairs.values())

    for ch in s:
        if ch in opening:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            # ignore any other characters (not expected per problem statement)
            continue

    return not stack

if __name__ == "__main__":
    s = sys.stdin.readline().strip()
    print("true" if is_balanced(s) else "false")
