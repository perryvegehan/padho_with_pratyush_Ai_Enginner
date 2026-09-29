def is_valid(s):
    # keep deleting innermost pairs until nothing changes
    previous = None
    while previous != s:
        previous = s
        s = s.replace("()", "").replace("[]", "").replace("{}", "")
    # balanced strings disappear completely
    return s == ""


s = input().strip()
print("true" if is_valid(s) else "false")
