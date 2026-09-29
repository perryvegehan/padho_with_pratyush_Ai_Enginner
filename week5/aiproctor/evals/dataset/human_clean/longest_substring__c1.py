import sys


def lengthOfLongestSubstring(s):
    last_index = {}
    window_start = 0
    longest = 0

    for i, ch in enumerate(s):
        if last_index.get(ch, -1) >= window_start:
            window_start = last_index[ch] + 1
        last_index[ch] = i
        longest = max(longest, i - window_start + 1)

    return longest


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
