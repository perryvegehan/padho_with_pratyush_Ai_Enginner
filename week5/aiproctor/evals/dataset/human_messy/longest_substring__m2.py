import sys


def lengthOfLongestSubstring(s):
    if len(s)==0: return 0
    temp = ""
    mx = 1
    for i in range(len(s)):
        temp = ""
        for j in range(i,len(s)):
            if s[j] not in temp:
                temp = temp + s[j]
            else:
                break
        if len(temp)>mx:
            mx = len(temp)
    return mx


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
