import sys


def lengthOfLongestSubstring(s):
    cur = ""
    mx = 0
    for c in s:
        if c in cur:
            cur = cur[cur.index(c) + 1:]
        cur += c
        if len(cur) > mx:
            mx = len(cur)
    return mx


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
