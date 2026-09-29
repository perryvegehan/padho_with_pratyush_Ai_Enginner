n = int(input())
arr = list(map(int, input().split()))

maxi = arr[0]
sm = 0
for e in arr:
    sm = max(e, sm + e)
    maxi = max(maxi, sm)
print(maxi)
