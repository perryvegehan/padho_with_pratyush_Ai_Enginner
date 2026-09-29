import sys

def length_of_longest_substring(s: str) -> int:
    """
    Returns the length of the longest substring of `s` that contains no
    repeating characters. Uses a sliding window with a dictionary that
    stores the most recent index of each character.
    """
    last_pos = {}          # character -> last index seen
    start = 0              # left bound of the current window
    max_len = 0

    for i, ch in enumerate(s):
        # If the character was seen inside the current window,
        # move the start just after its previous occurrence.
        if ch in last_pos and last_pos[ch] >= start:
            start = last_pos[ch] + 1
        # Update the last seen position of the character.
        last_pos[ch] = i
        # Update the answer.
        max_len = max(max_len, i - start + 1)

    return max_len


def main():
    data = sys.stdin.read().splitlines()
    # The problem states a single line input, but we guard against extra whitespace.
    s = data[0] if data else ""
    print(length_of_longest_substring(s))


if __name__ == "__main__":
    main()
