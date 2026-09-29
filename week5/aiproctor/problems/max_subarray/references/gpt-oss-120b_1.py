# Maximum Subarray Sum (Kadane's algorithm)

def max_subarray_sum(arr):
    """Return the maximum sum of a non‑empty contiguous subarray."""
    # Initialise both current and best sums with the first element
    current_max = best_max = arr[0]

    for x in arr[1:]:
        # Either extend the previous subarray or start a new one at x
        current_max = max(x, current_max + x)
        # Keep track of the best sum seen so far
        best_max = max(best_max, current_max)

    return best_max


if __name__ == "__main__":
    import sys

    data = sys.stdin.read().strip().split()
    if not data:
        sys.exit(0)          # no input

    n = int(data[0])
    # Take exactly n numbers after the first token (ignore any extra)
    arr = list(map(int, data[1:1 + n]))

    # Edge case: n could be 0 (though problem says non‑empty), guard anyway
    if not arr:
        print(0)
    else:
        print(max_subarray_sum(arr))
