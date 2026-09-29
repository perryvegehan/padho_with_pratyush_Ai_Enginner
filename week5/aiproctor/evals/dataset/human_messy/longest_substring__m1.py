import sys
def lengthOfLongestSubstring(s):
    d={}
    l=0
    ans=0
    for r in range(len(s)):
        if s[r] in d:
            l=max(l,d[s[r]]+1)
        d[s[r]]=r
        ans=max(ans,r-l+1)
        #print(l,r,ans)
    return ans
s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
