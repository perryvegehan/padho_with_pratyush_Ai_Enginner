n = int(input())
nums = list(map(int, input().split()))

res = nums[0]
running = 0
for x in nums:
    running = max(x, running + x)
    res = max(res, running)
print(res)
