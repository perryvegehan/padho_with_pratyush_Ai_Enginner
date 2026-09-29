import sys

def main() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return

    n = int(data[0])
    numbers = list(map(int, data[1:1 + n]))
    target = int(data[1 + n])

    seen = {}
    for i, num in enumerate(numbers):
        complement = target - num
        if complement in seen:
            a, b = seen[complement], i
            if a > b:
                a, b = b, a
            print(f"{a} {b}")
            return
        seen[num] = i

if __name__ == "__main__":
    main()
