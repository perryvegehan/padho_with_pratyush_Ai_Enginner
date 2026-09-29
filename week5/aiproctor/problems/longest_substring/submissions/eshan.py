import sys

def longest_unique_substring(s: str) -> int:
    """
    Returns the length of the longest substring of `s` that contains no
    repeated characters.
    Uses the classic sliding‑window technique with a dictionary that stores
    the most recent index of each character.
    """
    last_pos = {}          # character -> last index where it appeared
    start = 0              # left bound of the current window
    max_len = 0

    for i, ch in enumerate(s):
        # If `ch` was seen inside the current window, move the start right
        if ch in last_pos and last_pos[ch] >= start:
            start = last_pos[ch] + 1
        # Update the last seen position of `ch`
        last_pos[ch] = i
        # Update answer
        max_len = max(max_len, i - start + 1)

    return max_len

def main() -> None:
    s = sys.stdin.readline().rstrip('\n')
    # The problem allows an empty string; handle it gracefully
    print(longest_unique_substring(s))

if __name__ == "__main__":
    main()
