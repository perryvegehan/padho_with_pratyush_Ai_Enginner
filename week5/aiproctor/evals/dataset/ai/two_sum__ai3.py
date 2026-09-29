import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return

    # first token is n
    n = int(data[0])
    # next n tokens are the array
    nums = list(map(int, data[1:1 + n]))
    # last token is target
    target = int(data[1 + n])

    # hashmap: value -> index
    seen = {}
    for i, v in enumerate(nums):
        complement = target - v
        if complement in seen:
            j = seen[complement]
            # output smaller index first
            if j < i:
                print(j, i)
            else:
                print(i, j)
            return
        seen[v] = i

if __name__ == "__main__":
    solve()
