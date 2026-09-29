def two_sum(nums, target):
    mp = {}
    for i in range(len(nums)):
        x = nums[i]
        # print(mp)
        if target-x in mp:
            return mp[target-x], i
        mp[x] = i
    return 0,0


n = int(input())
nums = list(map(int, input().split()))
target = int(input())
i, j = two_sum(nums, target)
print(i, j)
