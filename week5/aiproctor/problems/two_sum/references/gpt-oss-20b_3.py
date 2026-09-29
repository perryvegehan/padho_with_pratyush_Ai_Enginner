def two_sum(nums, target):
    """Return indices of two numbers in `nums` that sum to `target`."""
    # Map each number to its index.
    index_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in index_map:
            # Found the pair; return indices in ascending order.
            return (index_map[complement], i) if index_map[complement] < i else (i, index_map[complement])
        index_map[num] = i

    # Since the problem guarantees exactly one solution, this line should never be reached.
    raise ValueError("No two-sum solution found")


if __name__ == "__main__":
    n = int(input())
    nums = list(map(int, input().split()))
    target = int(input())
    i, j = two_sum(nums, target)
    print(i, j)
