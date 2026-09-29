def two_sum(nums, target):
    """
    Returns the indices (i, j) such that nums[i] + nums[j] == target.
    Exactly one solution is guaranteed. Indices are returned in
    ascending order (i < j).
    """
    # map from number to its index (the first occurrence)
    seen = {}
    for idx, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            i = seen[complement]
            j = idx
            # ensure the smaller index comes first
            return (i, j) if i < j else (j, i)
        # store only the first occurrence to keep the smallest possible index
        if num not in seen:
            seen[num] = idx
    # The problem guarantees a solution, so we should never reach here.
    raise ValueError("No two sum solution found")


if __name__ == "__main__":
    n = int(input())
    nums = list(map(int, input().split()))
    target = int(input())
    i, j = two_sum(nums, target)
    print(i, j)
