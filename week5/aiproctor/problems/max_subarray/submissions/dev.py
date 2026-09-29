n = int(input())
a = list(map(int, input().split()))

ans = a[0]
curr = 0
for v in a:
    curr = max(v, curr + v)
    ans = max(ans, curr)
print(ans)
