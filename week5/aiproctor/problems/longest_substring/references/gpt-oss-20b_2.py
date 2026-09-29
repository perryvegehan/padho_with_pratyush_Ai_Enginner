import sys

def lengthOfLongestSubstring(s: str) -> int:
    """
    Returns the length of the longest substring without repeating characters.
    Uses a sliding window with a dictionary that maps each character to its
    last seen index. The window is expanded to the right while ensuring that
    no character repeats inside it. When a repeat is found, the left boundary
    of the window jumps to one position after the previous occurrence of that
    character.
    """
    n = len(s)
    if n == 0:
        return 0

    char_index = {}          # character -> last index seen
    left = 0                 # left boundary of the window
    max_len = 0

    for right, ch in enumerate(s):
        if ch in char_index and char_index[ch] >= left:
            # Found a repeating character inside the current window.
            # Move left past the previous occurrence.
            left = char_index[ch] + 1

        char_index[ch] = right
        current_len = right - left + 1
        if current_len > max_len:
            max_len = current_len

    return max_len


if __name__ == "__main__":
    s = sys.stdin.readline().rstrip('\n')
    print(lengthOfLongestSubstring(s))
