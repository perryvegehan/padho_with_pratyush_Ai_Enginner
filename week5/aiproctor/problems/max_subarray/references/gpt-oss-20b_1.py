n = int(input().strip())
arr = list(map(int, input().split()))

# Kadane's algorithm
current_sum = global_max = arr[0]
for num in arr[1:]:
    current_sum = max(num, current_sum + num)
    global_max = max(global_max, current_sum)

print(global_max)
