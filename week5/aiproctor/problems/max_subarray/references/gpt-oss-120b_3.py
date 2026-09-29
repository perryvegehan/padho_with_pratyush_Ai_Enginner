# Maximum Subarray Sum - Kadane's algorithm

n = int(input())
arr = list(map(int, input().split()))

# Ensure we have at least one element (as per problem statement)
max_current = max_global = arr[0]

for x in arr[1:]:
    # Either extend the previous subarray or start a new one at x
    max_current = max(x, max_current + x)
    max_global = max(max_global, max_current)

print(max_global)
