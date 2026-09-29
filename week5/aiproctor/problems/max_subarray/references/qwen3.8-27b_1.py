n = int(input())
arr = list(map(int, input().split()))

best = arr[0]
current = arr[0]
for i in range(1, n):
    current = max(arr[i], current + arr[i])
    best = max(best, current)

print(best)
