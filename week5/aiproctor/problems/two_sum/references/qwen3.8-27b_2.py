def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return seen[complement], i
        seen[num] = i


n = int(input())
nums = list(map(int, input().split()))
target = int(input())
i, j = two_sum(nums, target)
print(i, j)
