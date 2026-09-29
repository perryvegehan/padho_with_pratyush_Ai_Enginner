import sys


def lengthOfLongestSubstring(s):
    freq = {}
    i = 0
    res = 0
    for j in range(len(s)):
        freq[s[j]] = freq.get(s[j], 0) + 1
        while freq[s[j]] > 1:
            freq[s[i]] -= 1
            i += 1
        res = max(res, j - i + 1)
    # print(freq)
    return res


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
