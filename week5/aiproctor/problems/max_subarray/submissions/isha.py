n = int(input())
arr = list(map(int, input().split()))

# kadane
mx = arr[0]
s = 0
for num in arr:
    s = max(num, s + num)
    mx = max(mx, s)

print(mx)
