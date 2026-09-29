import sys

def longest_substring_length(s: str) -> int:
    last_seen = {}
    max_len = 0
    start = 0  # left boundary of the current window

    for i, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= start:
            # Move the start right after the previous occurrence of ch
            start = last_seen[ch] + 1
        last_seen[ch] = i
        max_len = max(max_len, i - start + 1)

    return max_len

def main() -> None:
    s = sys.stdin.readline().rstrip('\n')
    print(longest_substring_length(s))

if __name__ == "__main__":
    main()
