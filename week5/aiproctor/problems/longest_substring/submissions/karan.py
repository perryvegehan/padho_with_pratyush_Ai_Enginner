import sys


def lengthOfLongestSubstring(s):
    n = len(s)
    ans = 0
    for i in range(n):
        st = set()
        for j in range(i, n):
            if s[j] in st:
                break
            st.add(s[j])
        ans = max(ans, len(st))
    return ans


s = sys.stdin.readline().strip()
print(lengthOfLongestSubstring(s))
