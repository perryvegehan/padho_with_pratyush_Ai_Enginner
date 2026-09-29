def two_sum(nums, target):
    """
    Returns the pair of indices (i, j) such that nums[i] + nums[j] == target.
    Exactly one solution is guaranteed, and i < j.
    """
    # Dictionary to store value -> its index as we scan the list
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            # We have found the pair; ensure smaller index first
            j = i
            i = seen[complement]
            return (i, j) if i < j else (j, i)
        # Store the current number with its index for future look‑ups
        seen[num] = i
    # According to the problem statement this line is never reached
    raise ValueError("No two sum solution exists")


# ----- I/O handling -----
if __name__ == "__main__":
    n = int(input())
    nums = list(map(int, input().split()))
    target = int(input())
    i, j = two_sum(nums, target)
    print(i, j)
