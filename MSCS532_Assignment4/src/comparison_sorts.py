"""

Implements Quick Sort and Merge Sort.

These algorithms are used only to compare their performance
with Heap Sort.
"""

import random
from typing import List, Sequence


# Randomized Quick Sort
def quicksort(arr: Sequence) -> List:
    # Copy the input so the original list is unchanged.
    values = list(arr)

    # Sort the copied list.
    _quicksort_inplace(values, 0, len(values) - 1)

    return values


# Sort the list using a random pivot.
def _quicksort_inplace(values: List, low: int, high: int) -> None:
    # Use a stack instead of recursion.
    stack = [(low, high)]

    while stack:
        low, high = stack.pop()

        while low < high:
            # Use insertion sort for small sections.
            if high - low < 16:
                _insertion_sort(values, low, high)
                break

            # Choose a random pivot.
            pivot_index = random.randint(low, high)

            # Move the pivot to the beginning.
            values[low], values[pivot_index] = (
                values[pivot_index],
                values[low],
            )

            pivot = values[low]

            # Create three partitions.
            less = low
            current = low + 1
            greater = high

            while current <= greater:
                if values[current] < pivot:
                    values[less], values[current] = (
                        values[current],
                        values[less],
                    )
                    less += 1
                    current += 1

                elif values[current] > pivot:
                    values[current], values[greater] = (
                        values[greater],
                        values[current],
                    )
                    greater -= 1

                else:
                    current += 1

            # Process the smaller section first.
            left_size = less - 1 - low
            right_size = high - (greater + 1)

            if left_size < right_size:
                stack.append((greater + 1, high))
                high = less - 1
            else:
                stack.append((low, less - 1))
                low = greater + 1


# Insertion sort for small sections.
def _insertion_sort(values: List, low: int, high: int) -> None:
    for index in range(low + 1, high + 1):
        current_value = values[index]
        previous = index - 1

        # Move larger values to the right.
        while previous >= low and values[previous] > current_value:
            values[previous + 1] = values[previous]
            previous -= 1

        values[previous + 1] = current_value


# Merge Sort
def merge_sort(arr: Sequence) -> List:
    # Copy the input.
    values = list(arr)

    # A list with zero or one element is already sorted.
    if len(values) <= 1:
        return values

    # Create temporary storage for merging.
    buffer = [None] * len(values)

    # Sort the list.
    _merge_sort_inplace(
        values,
        buffer,
        0,
        len(values) - 1,
    )

    return values


# Divide the list into smaller sections.
def _merge_sort_inplace(
    values: List,
    buffer: List,
    low: int,
    high: int,
) -> None:
    # Stop when only one element remains.
    if low >= high:
        return

    # Find the middle.
    middle = (low + high) // 2

    # Sort the left half.
    _merge_sort_inplace(
        values,
        buffer,
        low,
        middle,
    )

    # Sort the right half.
    _merge_sort_inplace(
        values,
        buffer,
        middle + 1,
        high,
    )

    # Merge both halves.
    _merge(
        values,
        buffer,
        low,
        middle,
        high,
    )


# Merge two sorted halves.
def _merge(
    values: List,
    buffer: List,
    low: int,
    middle: int,
    high: int,
) -> None:

    left = low
    right = middle + 1
    index = low

    # Compare values from both halves.
    while left <= middle and right <= high:
        if values[left] <= values[right]:
            buffer[index] = values[left]
            left += 1
        else:
            buffer[index] = values[right]
            right += 1

        index += 1

    # Copy remaining values from the left half.
    while left <= middle:
        buffer[index] = values[left]
        left += 1
        index += 1

    # Copy remaining values from the right half.
    while right <= high:
        buffer[index] = values[right]
        right += 1
        index += 1

    # Copy the merged values back.
    values[low:high + 1] = buffer[low:high + 1]


# Test the program.
if __name__ == "__main__":

    test_cases = {
        "empty": [],
        "single": [42],
        "already_sorted": list(range(1000)),
        "reverse_sorted": list(range(1000, 0, -1)),
        "many_duplicates": [
            random.randint(0, 5)
            for _ in range(1000)
        ],
        "random": [
            random.randint(-10000, 10000)
            for _ in range(1000)
        ],
    }

    # Test both algorithms.
    for name, data in test_cases.items():
        expected = sorted(data)

        assert quicksort(data) == expected, (
            f"Quick Sort failed on {name}"
        )

        assert merge_sort(data) == expected, (
            f"Merge Sort failed on {name}"
        )

        print(f"[PASS] {name} (n={len(data)})")

    print("\nAll comparison sort tests passed.")