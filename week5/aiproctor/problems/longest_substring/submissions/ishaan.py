import sys

def longest_unique_substring_length(s: str) -> int:
    """Return the length of the longest substring without repeating characters."""
    last_seen = {}          # maps character -> last index seen
    start = 0              # start index of current window
    max_len = 0

    for i, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= start:
            # character repeated inside current window, move start
            start = last_seen[ch] + 1
        last_seen[ch] = i
        max_len = max(max_len, i - start + 1)
    return max_len

def main() -> None:
    s = sys.stdin.readline().rstrip('\n')
    print(longest_unique_substring_length(s))

if __name__ == "__main__":
    main()
