import sys

def longest_unique_substring(s: str) -> int:
    """Return the length of the longest substring without repeating characters."""
    last_seen = {}
    max_len = 0
    start = 0  # left boundary of the current window

    for i, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= start:
            # Move the start to one position after the previous occurrence
            start = last_seen[ch] + 1
        last_seen[ch] = i
        max_len = max(max_len, i - start + 1)
    return max_len

if __name__ == "__main__":
    s = sys.stdin.read().rstrip("\n")
    print(longest_unique_substring(s))
