"""
Compares Randomized Quick Sort and Deterministic Quick Sort.

The algorithms are tested using:
1. Random data
2. Sorted data
3. Reverse-sorted data
4. Data with many duplicate values
"""

import csv
import random
import sys
import time
from pathlib import Path

# Add the src folder so quicksort.py can be imported.
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "src")
)

from quicksort import randomized_quicksort, deterministic_quicksort

# Keep random values the same for every program run.
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

    # Create data containing many repeated values.
    if kind == "many_duplicates":
        number_of_values = max(1, int(n ** 0.5))

        return [
            random.randint(0, number_of_values)
            for _ in range(n)
        ]

    # Stop the program if the input type is invalid.
    raise ValueError(f"Unknown input type: {kind}")


# Measure the execution time of a sorting algorithm.
def time_one(sort_function, data, trials=3):
    # Begin with an unlimited best time.
    best_time = float("inf")

    # Run the algorithm several times.
    for _ in range(trials):
        # Copy the data because Quick Sort changes the original list.
        work = list(data)

        # Start the timer.
        start = time.perf_counter()

        # Sort the copied list.
        sort_function(work)

        # Calculate the execution time.
        elapsed = time.perf_counter() - start

        # Keep the fastest result.
        best_time = min(best_time, elapsed)

    return best_time


def main():
    # Sizes used to test both algorithms.
    regular_sizes = [100, 500, 1000, 2000, 4000]

    # Larger sizes used only for random data.
    large_sizes = [8000, 16000, 32000]

    # Types of datasets used in the experiment.
    distributions = [
        "random",
        "sorted",
        "reverse_sorted",
        "many_duplicates",
    ]

    # Store all benchmark results.
    rows = []

    # Test every dataset type using the regular sizes.
    for distribution in distributions:
        for n in regular_sizes:
            # Create the test data.
            data = make_input(distribution, n)

            # Measure Randomized Quick Sort.
            randomized_time = time_one(
                randomized_quicksort,
                data
            )

            # Measure Deterministic Quick Sort.
            deterministic_time = time_one(
                deterministic_quicksort,
                data
            )

            # Save the results.
            rows.append({
                "distribution": distribution,
                "n": n,
                "randomized_sec": randomized_time,
                "deterministic_sec": deterministic_time,
            })

            # Display the results in the terminal.
            print(
                f"{distribution:16s} "
                f"n={n:6d}  "
                f"randomized={randomized_time:.6f}s  "
                f"deterministic={deterministic_time:.6f}s"
            )

    # Test larger random datasets.
    for n in large_sizes:
        # Create random test data.
        data = make_input("random", n)

        # Measure both algorithms.
        randomized_time = time_one(
            randomized_quicksort,
            data
        )

        deterministic_time = time_one(
            deterministic_quicksort,
            data
        )

        # Save the results.
        rows.append({
            "distribution": "random",
            "n": n,
            "randomized_sec": randomized_time,
            "deterministic_sec": deterministic_time,
        })

        # Display the results.
        print(
            f"{'random':16s} "
            f"n={n:6d}  "
            f"randomized={randomized_time:.6f}s  "
            f"deterministic={deterministic_time:.6f}s"
        )

    # Create the data folder if it does not exist.
    data_folder = (
        Path(__file__).resolve().parent.parent / "data"
    )
    data_folder.mkdir(exist_ok=True)

    # Set the output CSV file location.
    output_path = data_folder / "quicksort_benchmark.csv"

    # Write all benchmark results to the CSV file.
    with open(output_path, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "distribution",
                "n",
                "randomized_sec",
                "deterministic_sec",
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResults written to: {output_path}")


# Run the benchmark when this file is executed directly.
if __name__ == "__main__":
    main()