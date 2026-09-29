import sys


def lengthOfLongestSubstring(s):
    last = [-1] * 256
    i = 0
    best = 0
    for j, ch in enumerate(s):
        # print(j, ch, i)
        if last[ord(ch)] >= i:
            i = last[ord(ch)] + 1
        last[ord(ch)] = j
        if j - i + 1 > best:
            best = j - i + 1
    return best


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
