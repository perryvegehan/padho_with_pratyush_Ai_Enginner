def two_sum(nums, target):
    """
    Returns the indices of the two numbers in `nums` that add up to `target`.
    The returned indices are in increasing order.
    """
    # Dictionary to store number -> its index while we iterate
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            # We have found the pair
            j = seen[complement]
            # Return indices sorted (smaller first)
            return (j, i) if j < i else (i, j)
        # Store the current number with its index for future look‑ups
        seen[num] = i
    # According to the problem statement this line should never be reached
    raise ValueError("No two sum solution exists")


# ---- I/O handling ----
if __name__ == "__main__":
    n = int(input().strip())
    nums = list(map(int, input().split()))
    target = int(input().strip())
    i, j = two_sum(nums, target)
    print(i, j)
