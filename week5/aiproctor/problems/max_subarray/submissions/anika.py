n = int(input())
arr = list(map(int, input().split()))

best = arr[0]
cur = 0
for x in arr:
    cur = max(x, cur + x)
    best = max(best, cur)
print(best)
