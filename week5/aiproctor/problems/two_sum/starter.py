def two_sum(nums, target):
    # write your code here
    pass


n = int(input())
nums = list(map(int, input().split()))
target = int(input())
i, j = two_sum(nums, target)
print(i, j)
