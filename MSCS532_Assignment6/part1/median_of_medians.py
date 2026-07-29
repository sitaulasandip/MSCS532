"""
median_of_medians.py

Implements the deterministic Median of Medians
selection algorithm.

The algorithm finds the k-th smallest value in
worst-case O(n) time.

The value of k is 1-based:
k = 1 returns the smallest value.
"""



from typing import List


# Sort a small list using insertion sort.
def _insertion_sort(values: List[int]) -> List[int]:
    # Copy the list so the original is unchanged.
    sorted_values = values[:]

    for index in range(1, len(sorted_values)):
        current_value = sorted_values[index]
        previous = index - 1

        # Move larger values to the right.
        while (
            previous >= 0
            and sorted_values[previous] > current_value
        ):
            sorted_values[previous + 1] = sorted_values[previous]
            previous -= 1

        sorted_values[previous + 1] = current_value

    return sorted_values


# Divide values into three groups around the pivot.
def _partition_around_value(
    values: List[int],
    pivot_value: int,
) -> tuple:
    less = []
    equal = []
    greater = []

    for value in values:
        if value < pivot_value:
            less.append(value)

        elif value == pivot_value:
            equal.append(value)

        else:
            greater.append(value)

    return less, equal, greater


# Find the k-th smallest value.
def median_of_medians_select(
    values: List[int],
    k: int,
):
    # The list cannot be empty.
    if not values:
        raise ValueError(
            "Cannot select from an empty array"
        )

    # Check that k is valid.
    if not 1 <= k <= len(values):
        raise IndexError(
            f"k={k} is out of bounds for "
            f"array of length {len(values)}"
        )

    return _select(values, k)


# Recursive selection helper.
def _select(
    values: List[int],
    k: int,
):
    size = len(values)

    # Sort small lists directly.
    if size <= 5:
        sorted_values = _insertion_sort(values)
        return sorted_values[k - 1]

    medians = []

    # Split the list into groups of five.
    for start in range(0, size, 5):
        group = values[start:start + 5]

        sorted_group = _insertion_sort(group)

        # Select the middle value from the group.
        middle_index = (
            len(sorted_group) - 1
        ) // 2

        medians.append(
            sorted_group[middle_index]
        )

    # Find the median of the group medians.
    middle_rank = (
        len(medians) + 1
    ) // 2

    pivot = _select(
        medians,
        middle_rank
    )

    # Partition the full list around the pivot.
    less, equal, greater = _partition_around_value(
        values,
        pivot
    )

    # Search the partition containing k.
    if k <= len(less):
        return _select(
            less,
            k
        )

    if k <= len(less) + len(equal):
        return pivot

    new_k = (
        k
        - len(less)
        - len(equal)
    )

    return _select(
        greater,
        new_k
    )


# Alternative name for the same selection function.
def median_of_medians_kth_smallest_iterative_wrapper(
    values: List[int],
    k: int,
):
    return median_of_medians_select(
        values,
        k
    )


# Test the program.
if __name__ == "__main__":
    import random

    # Test every rank in a fixed list.
    test_values = [
        12,
        3,
        5,
        7,
        4,
        19,
        26,
        1,
        3,
        3,
        9,
    ]

    expected_values = sorted(test_values)

    for rank in range(
        1,
        len(test_values) + 1
    ):
        result = median_of_medians_select(
            test_values,
            rank
        )

        expected = expected_values[rank - 1]

        assert result == expected, (
            f"Rank {rank}: "
            f"got {result}, "
            f"expected {expected}"
        )

    print(
        "All Median of Medians tests passed."
    )

    # Test random lists.
    for _ in range(200):
        size = random.randint(1, 200)

        values = [
            random.randint(-100, 100)
            for _ in range(size)
        ]

        rank = random.randint(1, size)

        result = median_of_medians_select(
            values,
            rank
        )

        expected = sorted(values)[rank - 1]

        assert result == expected

    print("Randomized stress tests passed.")