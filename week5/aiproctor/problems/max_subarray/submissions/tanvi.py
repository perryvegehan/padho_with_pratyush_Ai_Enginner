n = int(input())
arr = list(map(int, input().split()))

cur = arr[0]
best = arr[0]
for i in range(1, n):
    cur = cur + arr[i]
    if cur < arr[i]:
        cur = arr[i]
    if cur > best:
        best = cur
print(best)
