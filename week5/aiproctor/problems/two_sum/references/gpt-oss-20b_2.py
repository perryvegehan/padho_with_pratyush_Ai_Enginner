def two_sum(nums, target):
    """Return indices of two numbers that sum to target."""
    index_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in index_map:
            j = index_map[complement]
            # Return smaller index first
            return (j, i) if j < i else (i, j)
        index_map[num] = i

# Read input
n = int(input())
nums = list(map(int, input().split()))
target = int(input())

# Find and print the result
i, j = two_sum(nums, target)
print(i, j)
