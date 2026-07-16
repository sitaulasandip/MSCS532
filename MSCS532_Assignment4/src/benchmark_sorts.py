"""

Compares the performance of:
1. Heap Sort
2. Quick Sort
3. Merge Sort

The algorithms are tested using:
- random data
- sorted data
- reverse-sorted data

Results are saved to data/sorting_benchmark.csv.
"""

import csv
import random
import sys
import time
from pathlib import Path


# Add the current folder so sorting files can be imported.
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent)
)

from heapsort import heapsort
from comparison_sorts import quicksort, merge_sort


# Keep random data the same for every run.
random.seed(42)


# Create different types of test data.
def make_input(kind: str, n: int):
    # Create random numbers.
    if kind == "random":
        return [
            random.randint(0, 1_000_000)
            for _ in range(n)
        ]

    # Create numbers in ascending order.
    if kind == "sorted":
        return list(range(n))

    # Create numbers in descending order.
    if kind == "reverse_sorted":
        return list(range(n, 0, -1))

    # Stop if the dataset type is not valid.
    raise ValueError(f"Unknown input type: {kind}")


# Measure the execution time of one algorithm.
def time_one(sort_function, data, trials=3):
    # Begin with an unlimited best time.
    best_time = float("inf")

    # Run the algorithm several times.
    for _ in range(trials):
        # Copy the data because sorting may change the list.
        work = list(data)

        # Start the timer.
        start = time.perf_counter()

        # Sort the copied list.
        sort_function(work)

        # Calculate the total execution time.
        elapsed = time.perf_counter() - start

        # Keep the fastest result.
        best_time = min(best_time, elapsed)

    return best_time


def main():
    # Dataset sizes used in the experiment.
    sizes = [
        500,
        1000,
        2000,
        4000,
        8000,
        16000,
    ]

    # Types of datasets used for testing.
    distributions = [
        "random",
        "sorted",
        "reverse_sorted",
    ]

    # Store all benchmark results.
    rows = []

    # Test each data distribution.
    for distribution in distributions:
        # Test each input size.
        for n in sizes:
            # Create the test data.
            data = make_input(distribution, n)

            # Measure Heap Sort.
            heap_time = time_one(
                heapsort,
                data
            )

            # Measure Quick Sort.
            quick_time = time_one(
                quicksort,
                data
            )

            # Measure Merge Sort.
            merge_time = time_one(
                merge_sort,
                data
            )

            # Save the results.
            rows.append({
                "distribution": distribution,
                "n": n,
                "heapsort_sec": heap_time,
                "quicksort_sec": quick_time,
                "merge_sort_sec": merge_time,
            })

            # Display the results in the terminal.
            print(
                f"{distribution:16s} "
                f"n={n:6d}  "
                f"heapsort={heap_time:.6f}s  "
                f"quicksort={quick_time:.6f}s  "
                f"merge_sort={merge_time:.6f}s"
            )

    # Create the data folder if it does not exist.
    data_folder = (
        Path(__file__).resolve().parent.parent / "data"
    )
    data_folder.mkdir(exist_ok=True)

    # Set the CSV output path.
    output_path = data_folder / "sorting_benchmark.csv"

    # Write benchmark results to the CSV file.
    with open(output_path, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "distribution",
                "n",
                "heapsort_sec",
                "quicksort_sec",
                "merge_sort_sec",
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResults written to: {output_path}")


# Run the benchmark when this file is executed directly.
if __name__ == "__main__":
    main()