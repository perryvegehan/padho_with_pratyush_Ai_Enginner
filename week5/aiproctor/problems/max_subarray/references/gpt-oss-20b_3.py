# Maximum Subarray Sum (Kadane's algorithm)

n = int(input())
arr = list(map(int, input().split()))

# Initialize with the first element to handle all-negative arrays
max_ending_here = max_so_far = arr[0]

for x in arr[1:]:
    # Either start a new subarray at x or extend the previous one
    max_ending_here = max(x, max_ending_here + x)
    # Update global maximum if needed
    max_so_far = max(max_so_far, max_ending_here)

print(max_so_far)
