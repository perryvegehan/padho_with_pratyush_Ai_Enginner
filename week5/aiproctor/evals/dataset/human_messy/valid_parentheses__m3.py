def is_valid(s):
    cnt1 = 0
    cnt2 = 0
    cnt3 = 0
    a = []
    for ch in s:
        if ch in "([{":
            a.append(ch)
            continue
        if not a:
            return False
        top = a[-1]
        if (top == "(" and ch == ")") or (top == "[" and ch == "]") or (top == "{" and ch == "}"):
            a.pop()
        else:
            return False
    return a == []


s = input().strip()
print("true" if is_valid(s) else "false")
