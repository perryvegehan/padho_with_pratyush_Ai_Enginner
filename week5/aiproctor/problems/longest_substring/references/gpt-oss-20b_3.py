import sys

def lengthOfLongestSubstring(s: str) -> int:
    last_seen = {}
    max_len = 0
    start = 0  # start index of current window

    for i, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= start:
            # character repeated within current window, move start
            start = last_seen[ch] + 1
        # update last seen index
        last_seen[ch] = i
        # update max length
        current_len = i - start + 1
        if current_len > max_len:
            max_len = current_len

    return max_len

if __name__ == "__main__":
    s = sys.stdin.readline().strip()
    print(lengthOfLongestSubstring(s))
