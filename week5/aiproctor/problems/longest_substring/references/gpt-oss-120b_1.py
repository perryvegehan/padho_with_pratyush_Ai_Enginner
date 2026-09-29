import sys

def lengthOfLongestSubstring(s: str) -> int:
    """
    Returns the length of the longest substring of `s` that contains no
    repeating characters. Uses a sliding‑window technique with a hash map
    to achieve O(n) time and O(min(n, alphabet)) space.
    """
    last_pos = {}          # character -> most recent index
    left = 0               # start index of the current window
    best = 0               # length of the best window seen so far

    for right, ch in enumerate(s):
        # If the character was seen inside the current window,
        # move the left border just after its previous occurrence.
        if ch in last_pos and last_pos[ch] >= left:
            left = last_pos[ch] + 1

        last_pos[ch] = right
        # Window size is right - left + 1
        best = max(best, right - left + 1)

    return best

if __name__ == "__main__":
    s = sys.stdin.readline().rstrip("\n")
    print(lengthOfLongestSubstring(s))
