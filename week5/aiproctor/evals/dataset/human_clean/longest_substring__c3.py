import sys


def lengthOfLongestSubstring(s):
    # position where each character was last seen
    last_seen = {}
    start = 0
    answer = 0

    for end, char in enumerate(s):
        # repeated inside the window -> jump start past it
        if char in last_seen and last_seen[char] >= start:
            start = last_seen[char] + 1
        last_seen[char] = end
        answer = max(answer, end - start + 1)

    return answer


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
