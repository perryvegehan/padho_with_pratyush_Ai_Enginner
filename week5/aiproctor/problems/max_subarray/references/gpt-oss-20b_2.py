import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:n+1]))

    max_sum = -10**18  # sufficiently small
    cur_sum = 0
    for x in arr:
        cur_sum = max(x, cur_sum + x)
        max_sum = max(max_sum, cur_sum)

    print(max_sum)

if __name__ == "__main__":
    solve()
