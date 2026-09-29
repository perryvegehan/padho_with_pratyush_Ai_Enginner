import sys


def lengthOfLongestSubstring(s):
    last_seen = {}
    start = 0
    max_len = 0
    
    for i, char in enumerate(s):
        if char in last_seen and last_seen[char] >= start:
            start = last_seen[char] + 1
        last_seen[char] = i
        max_len = max(max_len, i - start + 1)
    
    return max_len


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
