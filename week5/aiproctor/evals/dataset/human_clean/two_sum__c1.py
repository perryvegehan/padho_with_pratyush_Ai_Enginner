def two_sum(nums, target):
    index_of = {}
    for i, value in enumerate(nums):
        complement = target - value
        if complement in index_of:
            return index_of[complement], i
        index_of[value] = i
    return -1, -1


n = int(input())
nums = list(map(int, input().split()))
target = int(input())
i, j = two_sum(nums, target)
print(i, j)
