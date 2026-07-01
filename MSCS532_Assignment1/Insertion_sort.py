
def insertion_sort_decreasing(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] < key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


if __name__ == "__main__":
    sample = [5, 2, 9, 1, 5, 6, 7, 3, 8, 4]
    print("Original array:", sample)
    sorted_array = insertion_sort_decreasing(sample)
    print("Sorted array (decreasing):", sorted_array)