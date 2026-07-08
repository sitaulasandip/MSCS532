import sys
import random

# Increase recursion limit for Quick Sort.
sys.setrecursionlimit(1_000_000)


# Merge Sort
def merge_sort(arr):
    # Return a sorted list.
    n = len(arr)

    if n <= 1:          # List is already sorted.
        return arr

    mid = n // 2        # Find the middle.
    left = merge_sort(arr[:mid])     # Sort left half.
    right = merge_sort(arr[mid:])    # Sort right half.

    return merge_list(left, right)       # Merge both halves.


def merge_list(left, right):
    # Merge two sorted lists.
    merged = []
    i = j = 0

    # Compare elements from both lists.
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Add remaining elements.
    merged.extend(left[i:])
    merged.extend(right[j:])

    return merged


# Quick Sort
def quick_sort(arr, randomized=False):
    # Sort the list using Quick Sort.
    quick_sort_list(arr, 0, len(arr) - 1, randomized)
    return arr


def quick_sort_list(arr, low, high, randomized):
    if low < high:              # Continue if more than one element.
        p = partition(arr, low, high, randomized)

        quick_sort_list(arr, low, p - 1, randomized)    # Sort left side.
        quick_sort_list(arr, p + 1, high, randomized)   # Sort right side.


def partition(arr, low, high, randomized):
    # Partition the array around the pivot.

    if randomized:
        # Choose a random pivot.
        r = random.randint(low, high)
        arr[r], arr[high] = arr[high], arr[r]

    pivot = arr[high]      # Last element is the pivot.
    i = low - 1

    # Move smaller elements before the pivot.
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    # Put the pivot in the correct position.
    arr[i + 1], arr[high] = arr[high], arr[i + 1]

    return i + 1


if __name__ == "__main__":
    sample = [5, 2, 9, 1, 5, 6, 0, 3, 3, 8]

    assert merge_sort(sample) == sorted(sample)
    assert quick_sort(sample[:]) == sorted(sample)
    assert quick_sort(sample[:], randomized=True) == sorted(sample)

    print("Test passed:", merge_sort(sample))