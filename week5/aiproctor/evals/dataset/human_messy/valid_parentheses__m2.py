def is_valid(s):
    stack = []
    mp = {')':'(', ']':'[', '}':'{'}
    for i in range(len(s)):
        if s[i] in mp.values():
            stack.append(s[i])
        else:
            if stack and stack[-1] == mp[s[i]]:
                stack.pop()
            else:
                return False
            #print(stack)
    if stack:
        return False
    return True


s = input().strip()
print("true" if is_valid(s) else "false")
