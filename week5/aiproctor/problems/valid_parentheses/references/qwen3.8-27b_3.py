def is_valid(s):
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}
    opening = {'(', '[', '{'}
    
    for char in s:
        if char in opening:
            stack.append(char)
        elif char in matching:
            if not stack or stack[-1] != matching[char]:
                return False
            stack.pop()
        else:
            return False
    
    return len(stack) == 0


s = input().strip()
print("true" if is_valid(s) else "false")
