"""
quickselect.py

Implements two versions of Randomized Quickselect.

Both functions find the k-th smallest value in
expected O(n) time.

The value of k is 1-based:
k = 1 returns the smallest value.
"""

import random
from typing import List


# Find the k-th smallest value using new lists.
def randomized_quickselect(
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

    return _select(
        values,
        k
    )


# Recursive Quickselect helper.
def _select(
    values: List[int],
    k: int,
):
    # A list with one value is already solved.
    if len(values) == 1:
        return values[0]

    # Choose a random pivot.
    pivot = random.choice(values)

    # Split values around the pivot.
    less = [
        value
        for value in values
        if value < pivot
    ]

    equal = [
        value
        for value in values
        if value == pivot
    ]

    greater = [
        value
        for value in values
        if value > pivot
    ]

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


# Find the k-th smallest value using in-place partitioning.
def randomized_quickselect_in_place(
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

    # Copy the list so the original is unchanged.
    array = values[:]

    # Convert k to a zero-based index.
    target_index = k - 1

    low = 0
    high = len(array) - 1

    while True:
        if low == high:
            return array[low]

        # Choose and place a random pivot.
        pivot_index = random.randint(
            low,
            high
        )

        pivot_index = _lomuto_partition(
            array,
            low,
            high,
            pivot_index
        )

        # Check which side contains the target.
        if target_index == pivot_index:
            return array[target_index]

        if target_index < pivot_index:
            high = pivot_index - 1

        else:
            low = pivot_index + 1


# Partition the list around the pivot.
def _lomuto_partition(
    values: List[int],
    low: int,
    high: int,
    pivot_index: int,
) -> int:
    pivot_value = values[pivot_index]

    # Move the pivot to the end.
    values[pivot_index], values[high] = (
        values[high],
        values[pivot_index],
    )

    store_index = low

    # Move smaller values to the left.
    for index in range(low, high):
        if values[index] < pivot_value:
            values[index], values[store_index] = (
                values[store_index],
                values[index],
            )

            store_index += 1

    # Move the pivot to its final position.
    values[store_index], values[high] = (
        values[high],
        values[store_index],
    )

    return store_index


# Test the program.
if __name__ == "__main__":
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

    # Test the recursive version.
    for rank in range(
        1,
        len(test_values) + 1
    ):
        result = randomized_quickselect(
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
        "All Quickselect tests passed."
    )

    # Test the in-place version.
    for rank in range(
        1,
        len(test_values) + 1
    ):
        result = randomized_quickselect_in_place(
            test_values,
            rank
        )

        expected = expected_values[rank - 1]

        assert result == expected, (
            f"In-place rank {rank}: "
            f"got {result}, "
            f"expected {expected}"
        )

    print(
        "All in-place Quickselect tests passed."
    )

    # Test random lists.
    for _ in range(200):
        size = random.randint(1, 200)

        values = [
            random.randint(-100, 100)
            for _ in range(size)
        ]

        rank = random.randint(1, size)

        expected = sorted(values)[rank - 1]

        assert (
            randomized_quickselect(
                values,
                rank
            )
            == expected
        )

        assert (
            randomized_quickselect_in_place(
                values,
                rank
            )
            == expected
        )

    print(
        "Randomized stress tests passed."
    )