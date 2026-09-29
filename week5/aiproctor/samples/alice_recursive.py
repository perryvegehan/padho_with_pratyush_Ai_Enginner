import sys

sys.setrecursionlimit(10**6)


def go(s, i, start, seen, best):
    if i == len(s):
        return best
    if s[i] in seen and seen[s[i]] > start:
        start = seen[s[i]] + 1
    seen[s[i]] = i
    return go(s, i + 1, start, seen, max(best, i - start + 1))


def lengthOfLongestSubstring(s):
    return go(s, 0, 0, {}, 0)


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
