import sys

def lengthOfLongestSubstring(s: str) -> int:
    """
    Returns the length of the longest substring of `s` that contains no
    repeating characters.
    """
    # Dictionary that maps a character to its most recent index (+1)
    # The stored value is the index just after the previous occurrence,
    # which allows us to move the left boundary of the window in O(1).
    last_idx = {}
    max_len = 0
    left = 0                     # start index of the current window

    for right, ch in enumerate(s):
        # If the character was seen and its last occurrence is inside the
        # current window, slide the left boundary right after that occurrence.
        if ch in last_idx and last_idx[ch] > left:
            left = last_idx[ch]

        # Update the max length using the current window size.
        current_len = right - left + 1
        if current_len > max_len:
            max_len = current_len

        # Store the index just after the current character.
        # This makes the next possible window start at right+1 if needed.
        last_idx[ch] = right + 1

    return max_len


if __name__ == "__main__":
    s = sys.stdin.readline().rstrip("\n")
    print(lengthOfLongestSubstring(s))
