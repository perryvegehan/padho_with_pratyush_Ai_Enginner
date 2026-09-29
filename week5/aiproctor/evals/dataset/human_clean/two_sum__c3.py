def two_sum(nums, target):
    # value -> index for everything we've already passed
    seen = {}
    for idx, num in enumerate(nums):
        need = target - num
        if need in seen:
            return seen[need], idx
        seen[num] = idx
    return None


n = int(input())
nums = list(map(int, input().split()))
target = int(input())
i, j = two_sum(nums, target)
print(i, j)
