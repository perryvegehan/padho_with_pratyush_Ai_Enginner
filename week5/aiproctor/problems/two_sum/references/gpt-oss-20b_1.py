def two_sum(nums, target):
    """
    Find indices of two numbers in nums that sum to target.
    Assumes exactly one solution exists.
    """
    seen = {}  # number -> index
    for idx, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            i, j = seen[complement], idx
            return (i, j) if i < j else (j, i)
        seen[num] = idx
    # Since problem guarantees a solution, we never reach here
    raise ValueError("No two sum solution found.")


if __name__ == "__main__":
    n = int(input())
    nums = list(map(int, input().split()))
    target = int(input())
    i, j = two_sum(nums, target)
    print(i, j)
