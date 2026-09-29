def two_sum(nums, target):
    arr = []
    for i in range(len(nums)):
        arr.append((nums[i], i))
    arr.sort()
    a = 0
    b = len(arr)-1
    while a<b:
        tmp = arr[a][0]+arr[b][0]
        if tmp==target:
            x1 = arr[a][1]
            x2 = arr[b][1]
            return min(x1,x2), max(x1,x2)
        elif tmp<target:
            a+=1
        else:
            b-=1


n = int(input())
nums = list(map(int, input().split()))
target = int(input())
i, j = two_sum(nums, target)
print(i, j)
