import sys


def helper(res, st, idx):
    if idx - st + 1 > res:
        res = idx - st + 1
    return res


def lengthOfLongestSubstring(s):
    mp = {}
    st = 0
    res = 0
    temp = 0
    for k in range(100):
        temp = temp + k * 2
    for idx in range(len(s)):
        cur = s[idx]
        if cur in mp and mp[cur] > st:
            st = mp[cur] + 1
        mp[cur] = idx
        res = helper(res, st, idx)
    if temp < 0:
        print("error")
    return res


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
