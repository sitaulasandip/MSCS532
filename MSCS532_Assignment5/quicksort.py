"""

Implements:
1. Deterministic Quick Sort
2. Randomized Quick Sort

Both algorithms return a new sorted list without
changing the original input list.
"""

import random
from typing import List, Sequence, TypeVar

T = TypeVar("T")


# Deterministic Quick Sort
def quicksort(arr: List[T]) -> List[T]:
    # Copy the input list.
    values = list(arr)

    # Sort the copied list.
    _quicksort(values, 0, len(values) - 1)

    return values


# Sort the list recursively.
def _quicksort(values: List[T], low: int, high: int) -> None:
    # Continue while more than one element exists.
    if low < high:
        # Partition the list.
        pivot_index = _partition(values, low, high)

        # Sort the left side.
        _quicksort(values, low, pivot_index - 1)

        # Sort the right side.
        _quicksort(values, pivot_index + 1, high)


# Partition the list using the last element as the pivot.
def _partition(values: List[T], low: int, high: int) -> int:
    # Choose the last element as the pivot.
    pivot = values[high]

    # Track the last value smaller than the pivot.
    smaller = low - 1

    # Compare every value with the pivot.
    for index in range(low, high):
        if values[index] <= pivot:
            smaller += 1
            values[smaller], values[index] = (
                values[index],
                values[smaller],
            )

    # Place the pivot in its correct position.
    values[smaller + 1], values[high] = (
        values[high],
        values[smaller + 1],
    )

    return smaller + 1


# Randomized Quick Sort
def randomized_quicksort(arr: List[T]) -> List[T]:
    # Copy the input list.
    values = list(arr)

    # Sort the copied list.
    _randomized_quicksort(
        values,
        0,
        len(values) - 1,
    )

    return values


# Sort the list using a random pivot.
def _randomized_quicksort(
    values: List[T],
    low: int,
    high: int,
) -> None:
    if low < high:
        # Partition using a random pivot.
        pivot_index = _randomized_partition(
            values,
            low,
            high,
        )

        # Sort the left side.
        _randomized_quicksort(
            values,
            low,
            pivot_index - 1,
        )

        # Sort the right side.
        _randomized_quicksort(
            values,
            pivot_index + 1,
            high,
        )


# Choose a random pivot before partitioning.
def _randomized_partition(
    values: List[T],
    low: int,
    high: int,
) -> int:
    # Select a random pivot.
    random_index = random.randint(low, high)

    # Move the pivot to the end.
    values[random_index], values[high] = (
        values[high],
        values[random_index],
    )

    # Partition the list.
    return _partition(values, low, high)


# Test the program.
if __name__ == "__main__":
    import random as random_generator

    # Create different test cases.
    test_cases: Sequence[List[int]] = [
        [],
        [1],
        [2, 1],
        [5, 3, 8, 4, 2, 7, 1, 10],
        list(range(20, 0, -1)),
        list(range(20)),
        [
            random_generator.randint(-50, 50)
            for _ in range(200)
        ],
        [7] * 15,
    ]

    # Test both sorting algorithms.
    for case in test_cases:
        expected = sorted(case)

        assert quicksort(case) == expected
        assert randomized_quicksort(case) == expected

    print("All Quick Sort tests passed.")