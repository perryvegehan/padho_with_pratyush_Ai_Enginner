import sys

def longest_unique_substring(s: str) -> int:
    """
    Returns the length of the longest substring of `s` that contains no
    repeating characters.
    """
    last_pos = {}          # character -> most recent index
    start = 0              # start index of current window
    max_len = 0

    for i, ch in enumerate(s):
        # If character was seen inside the current window, move start right after
        # its previous occurrence.
        if ch in last_pos and last_pos[ch] >= start:
            start = last_pos[ch] + 1
        # Update the character's last seen position.
        last_pos[ch] = i
        # Update max length.
        max_len = max(max_len, i - start + 1)

    return max_len

def main():
    s = sys.stdin.readline().rstrip('\n')
    # The problem allows an empty string.
    print(longest_unique_substring(s))

if __name__ == "__main__":
    main()
