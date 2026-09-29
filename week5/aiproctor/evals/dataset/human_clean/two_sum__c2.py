def two_sum(nums: list[int], target: int) -> tuple[int, int]:
    order = sorted(range(len(nums)), key=lambda k: nums[k])
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        total = nums[order[lo]] + nums[order[hi]]
        if total == target:
            return min(order[lo], order[hi]), max(order[lo], order[hi])
        if total < target:
            lo += 1
        else:
            hi -= 1
    return -1, -1


if __name__ == "__main__":
    n = int(input())
    nums = list(map(int, input().split()))
    target = int(input())
    i, j = two_sum(nums, target)
    print(i, j)
