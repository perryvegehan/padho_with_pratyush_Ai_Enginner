def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return seen[complement], i
        seen[num] = i
    return None

# Read input
n = int(input())
nums = list(map(int, input().split()))
target = int(input())

result = two_sum(nums, target)
if result:
    print(result[0], result[1])
