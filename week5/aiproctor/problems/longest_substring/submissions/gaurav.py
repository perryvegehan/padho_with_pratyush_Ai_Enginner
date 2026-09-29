class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        char_index = {}
        left = 0
        max_len = 0
        
        for right, char in enumerate(s):
            if char in char_index and char_index[char] >= left:
                left = char_index[char] + 1
            char_index[char] = right
            max_len = max(max_len, right - left + 1)
        
        return max_len

if __name__ == "__main__":
    s = input().strip()
    sol = Solution()
    print(sol.lengthOfLongestSubstring(s))
