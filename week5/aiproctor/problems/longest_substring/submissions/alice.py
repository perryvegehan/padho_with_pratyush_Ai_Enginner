import sys


def update_best(best, start, i):
    if i - start + 1 > best:
        best = i - start + 1
    return best


def lengthOfLongestSubstring(s):
    seen = {}
    start = 0
    best = 0
    for i in range(len(s)):
        ch = s[i]
        if ch in seen and seen[ch] > start:
            start = seen[ch] + 1
        seen[ch] = i
        best = update_best(best, start, i)
    return best


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
