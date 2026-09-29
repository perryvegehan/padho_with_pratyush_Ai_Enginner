import sys

def longest_unique_substring_length(s: str) -> int:
    last_seen = {}
    start = 0
    max_len = 0

    for i, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= start:
            start = last_seen[ch] + 1
        last_seen[ch] = i
        cur_len = i - start + 1
        if cur_len > max_len:
            max_len = cur_len
    return max_len

def main() -> None:
    # Read the entire input, keeping spaces if present
    s = sys.stdin.read().rstrip('\n')
    result = longest_unique_substring_length(s)
    print(result)

if __name__ == "__main__":
    main()
