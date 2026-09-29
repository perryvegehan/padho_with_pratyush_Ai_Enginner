def two_sum(nums, target):
    n=len(nums)
    for i in range(n):
        for j in range(i+1,n):
            if nums[i]+nums[j]==target:
                return i,j


n = int(input())
nums = list(map(int, input().split()))
target = int(input())
i, j = two_sum(nums, target)
print(i, j)
