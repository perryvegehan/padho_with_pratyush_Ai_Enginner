def is_valid(s: str) -> bool:
    if len(s) % 2 == 1:
        return False
    closing_for = {"(": ")", "[": "]", "{": "}"}
    expected = []
    for bracket in s:
        if bracket in closing_for:
            expected.append(closing_for[bracket])
        elif not expected or expected.pop() != bracket:
            return False
    return len(expected) == 0


if __name__ == "__main__":
    s = input().strip()
    print("true" if is_valid(s) else "false")
