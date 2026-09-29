import sys


def upd(ans, l, r):
    if r - l + 1 > ans:
        ans = r - l + 1
    return ans


def lengthOfLongestSubstring(s):
    last = {}
    l = 0
    ans = 0
    for r in range(len(s)):
        c = s[r]
        if c in last and last[c] > l:
            l = last[c] + 1
        last[c] = r
        ans = upd(ans, l, r)
    return ans


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
