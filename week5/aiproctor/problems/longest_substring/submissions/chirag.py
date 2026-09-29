import sys

# sliding window approach
def lengthOfLongestSubstring(s):
    pos = {}      # char -> index
    left = 0
    mx = 0
    for right in range(len(s)):
        x = s[right]
        if x in pos and pos[x] > left:
            left = pos[x] + 1   # shrink window
        pos[x] = right
        mx = check(mx, left, right)
    return mx


def check(mx, left, right):
    if right - left + 1 > mx:
        mx = right - left + 1
    return mx


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
