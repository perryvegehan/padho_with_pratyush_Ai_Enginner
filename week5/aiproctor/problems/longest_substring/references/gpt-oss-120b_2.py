import sys

def lengthOfLongestSubstring(s: str) -> int:
    """
    Returns the length of the longest substring without repeating characters.
    Uses a sliding window with a dictionary that stores the most recent index
    of each character.
    """
    # dictionary: character -> last position seen (0‑based)
    last_pos = {}
    max_len = 0
    # start of the current window (inclusive)
    left = 0

    for right, ch in enumerate(s):
        # If the character was seen inside the current window,
        # move the left bound right after its previous occurrence.
        if ch in last_pos and last_pos[ch] >= left:
            left = last_pos[ch] + 1

        # Update the last seen position of the character.
        last_pos[ch] = right

        # Length of the current window is right - left + 1
        max_len = max(max_len, right - left + 1)

    return max_len


if __name__ == "__main__":
    # Read the input string (may be empty, so .strip() is safe)
    s = sys.stdin.readline().rstrip("\n")
    print(lengthOfLongestSubstring(s))
