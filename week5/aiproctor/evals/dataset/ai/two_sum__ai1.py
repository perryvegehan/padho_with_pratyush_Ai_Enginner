import sys

def main() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))
    target = int(data[1 + n])

    # Map from number to its index
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            # Found the pair
            first, second = seen[complement], i
            # Ensure the smaller index comes first
            if first > second:
                first, second = second, first
            print(first, second)
            return
        seen[num] = i

if __name__ == "__main__":
    main()
