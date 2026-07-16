"""
Implements Heap Sort using a max heap.

Main functions:
1. max_heapify()
2. build_max_heap()
3. heapsort()

Heap Sort returns a new sorted list without changing the original input.
"""

from typing import List, Sequence


# Restore the max heap property.
def max_heapify(values: List, index: int, heap_size: int) -> None:

    while True:
        # Find the left and right child.
        left = 2 * index + 1
        right = 2 * index + 2

        # Assume the current node is the largest.
        largest = index

        # Compare with the left child.
        if (
            left < heap_size
            and values[left] > values[largest]
        ):
            largest = left

        # Compare with the right child.
        if (
            right < heap_size
            and values[right] > values[largest]
        ):
            largest = right

        # Stop if the heap property is already correct.
        if largest == index:
            break

        # Swap the values.
        values[index], values[largest] = (
            values[largest],
            values[index],
        )

        # Continue from the child.
        index = largest


# Build a max heap from the list.
def build_max_heap(values: List) -> None:
    number_of_values = len(values)

    # Start from the last parent node.
    for index in range(
        number_of_values // 2 - 1,
        -1,
        -1,
    ):
        max_heapify(
            values,
            index,
            number_of_values,
        )


# Sort the list using Heap Sort.
def heapsort(arr: Sequence) -> List:
    # Copy the input list.
    values = list(arr)

    # A list with zero or one element is already sorted.
    if len(values) <= 1:
        return values

    # Build the max heap.
    build_max_heap(values)

    # Move the largest value to the end.
    for end in range(
        len(values) - 1,
        0,
        -1,
    ):
        # Swap the first and last values.
        values[0], values[end] = (
            values[end],
            values[0],
        )

        # Restore the heap.
        max_heapify(
            values,
            0,
            end,
        )

    return values


# Test the program.
if __name__ == "__main__":
    import random

    # Create different test cases.
    test_cases = {
        "empty": [],
        "single": [42],
        "two_elements_sorted": [1, 2],
        "two_elements_reverse": [2, 1],
        "already_sorted": list(range(1000)),
        "reverse_sorted": list(range(1000, 0, -1)),
        "all_duplicates": [7] * 500,
        "many_duplicates": [
            random.randint(0, 5)
            for _ in range(1000)
        ],
        "random": [
            random.randint(-10000, 10000)
            for _ in range(1000)
        ],
        "negative_and_positive": list(range(-500, 500)),
    }

    # Test Heap Sort on every dataset.
    for name, data in test_cases.items():
        expected = sorted(data)

        result = heapsort(data)

        assert result == expected, (
            f"Heap Sort failed on {name}"
        )

        print(f"[PASS] {name} (n={len(data)})")

    print("\nAll correctness tests passed.")