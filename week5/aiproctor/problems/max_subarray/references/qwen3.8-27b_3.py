n = int(input())
arr = list(map(int, input().split()))

# Kadane's algorithm
max_ending_here = arr[0]
max_so_far = arr[0]

for i in range(1, n):
    max_ending_here = max(arr[i], max_ending_here + arr[i])
    max_so_far = max(max_so_far, max_ending_here)

print(max_so_far)
