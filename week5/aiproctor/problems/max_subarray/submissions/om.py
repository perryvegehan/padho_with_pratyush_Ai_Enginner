n = int(input())
arr = list(map(int, input().split()))

mx = -10**18
s = 0
for v in arr:
    s += v
    mx = max(mx, s)
    if s < 0:
        s = 0
print(mx)
