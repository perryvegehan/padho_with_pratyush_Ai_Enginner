# Maximum Subarray Sum – Kadane's algorithm

n = int(input())
arr = list(map(int, input().split()))

# Initialise both current and best sums with the first element
current_max = best_max = arr[0]

for x in arr[1:]:
    # Either start a new subarray at x or extend the previous one
    current_max = max(x, current_max + x)
    best_max = max(best_max, current_max)

print(best_max)
