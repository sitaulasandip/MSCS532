"""
Implements two versions of Quick Sort:

1. Randomized Quick Sort
2. Deterministic Quick Sort using the first element as pivot

"""

import random
from typing import List, Sequence


# Randomized Quick Sort
def randomized_quicksort(arr: Sequence) -> List:
    # Copy the input so the original list is not changed.
    values = list(arr)

    # Sort the copied list.
    _randomized_quicksort_inplace(
        values,
        0,
        len(values) - 1
    )

    return values


# Sort the list using a random pivot.
def _randomized_quicksort_inplace(
    values: List,
    low: int,
    high: int
) -> None:
    # Use a stack instead of recursion.
    stack = [(low, high)]

    while stack:
        # Get the next section to sort.
        low, high = stack.pop()

        while low < high:
            # Use insertion sort for small sections.
            if high - low < 16:
                _insertion_sort(values, low, high)
                break

            # Divide values into less than, equal to, and greater than pivot.
            left_equal, right_equal = _random_partition_3way(
                values,
                low,
                high
            )

            # Calculate the sizes of both remaining sections.
            left_size = left_equal - 1 - low
            right_size = high - (right_equal + 1)

            # Process the smaller section first to keep the stack small.
            if left_size < right_size:
                stack.append((right_equal + 1, high))
                high = left_equal - 1
            else:
                stack.append((low, left_equal - 1))
                low = right_equal + 1


# Divide the list into three sections using a random pivot.
def _random_partition_3way(
    values: List,
    low: int,
    high: int
):
    # Select a random pivot.
    pivot_index = random.randint(low, high)

    # Move the pivot to the beginning.
    values[low], values[pivot_index] = (
        values[pivot_index],
        values[low]
    )

    pivot = values[low]

    # Track the three sections.
    less = low
    current = low + 1
    greater = high

    while current <= greater:
        # Move smaller values to the left.
        if values[current] < pivot:
            values[less], values[current] = (
                values[current],
                values[less]
            )
            less += 1
            current += 1

        # Move larger values to the right.
        elif values[current] > pivot:
            values[current], values[greater] = (
                values[greater],
                values[current]
            )
            greater -= 1

        # Keep equal values in the middle.
        else:
            current += 1

    return less, greater


# Deterministic Quick Sort
def deterministic_quicksort(arr: Sequence) -> List:
    # Copy the input so the original list is not changed.
    values = list(arr)

    # Sort using the first element as pivot.
    _deterministic_quicksort_inplace(
        values,
        0,
        len(values) - 1
    )

    return values


# Sort the list using the first element as pivot.
def _deterministic_quicksort_inplace(
    values: List,
    low: int,
    high: int
) -> None:
    # Use a stack instead of recursion.
    stack = [(low, high)]

    while stack:
        # Get the next section to sort.
        low, high = stack.pop()

        while low < high:
            # Partition the current section.
            pivot_position = _lomuto_partition_first_pivot(
                values,
                low,
                high
            )

            # Calculate the sizes of both sections.
            left_size = pivot_position - 1 - low
            right_size = high - (pivot_position + 1)

            # Process the smaller section first.
            if left_size < right_size:
                stack.append((pivot_position + 1, high))
                high = pivot_position - 1
            else:
                stack.append((low, pivot_position - 1))
                low = pivot_position + 1


# Partition using the first element as pivot.
def _lomuto_partition_first_pivot(
    values: List,
    low: int,
    high: int
) -> int:
    # Save the first element as pivot.
    pivot = values[low]

    # Move the pivot to the end.
    values[low], values[high] = (
        values[high],
        values[low]
    )

    store_index = low

    # Move smaller values before the pivot.
    for index in range(low, high):
        if values[index] < pivot:
            values[index], values[store_index] = (
                values[store_index],
                values[index]
            )
            store_index += 1

    # Put the pivot in its correct position.
    values[store_index], values[high] = (
        values[high],
        values[store_index]
    )

    return store_index


# Sort a small section using insertion sort.
def _insertion_sort(
    values: List,
    low: int,
    high: int
) -> None:
    for index in range(low + 1, high + 1):
        # Save the current value.
        current_value = values[index]
        previous = index - 1

        # Move larger values one position to the right.
        while (
            previous >= low
            and values[previous] > current_value
        ):
            values[previous + 1] = values[previous]
            previous -= 1

        # Insert the value in the correct position.
        values[previous + 1] = current_value


# Test the program.
if __name__ == "__main__":
    # Create different test cases.
    test_cases = {
        "empty": [],
        "single": [42],
        "already_sorted": list(range(1000)),
        "reverse_sorted": list(range(1000, 0, -1)),
        "all_duplicates": [7] * 500,
        "many_duplicates": [
            random.randint(0, 5)
            for _ in range(1000)
        ],
        "random": [
            random.randint(-10_000, 10_000)
            for _ in range(1000)
        ],
        "negative_and_positive": list(range(-500, 500)),
    }

    # Test both algorithms on every dataset.
    for name, data in test_cases.items():
        expected = sorted(data)

        randomized_result = randomized_quicksort(data)
        deterministic_result = deterministic_quicksort(data)

        # Check that both results are correct.
        assert randomized_result == expected, (
            f"Randomized Quick Sort failed on {name}"
        )

        assert deterministic_result == expected, (
            f"Deterministic Quick Sort failed on {name}"
        )

        print(f"[PASS] {name} (n={len(data)})")

    print("\nAll correctness tests passed.")