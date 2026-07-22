"""

Compares deterministic and randomized Quick Sort
using different input sizes and data types.

The program saves:
1. results.csv
2. benchmark_chart.png
"""

import csv
import random
import sys
import time
from statistics import mean

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from quicksort import quicksort, randomized_quicksort


# Increase the recursion limit for large sorted inputs.
sys.setrecursionlimit(20000)

# Number of timing runs for each test.
REPEATS = 3


# Create input data based on the selected distribution.
def make_input(size: int, distribution: str) -> list:
    if distribution == "random":
        return [
            random.randint(-1_000_000, 1_000_000)
            for _ in range(size)
        ]

    if distribution == "sorted":
        return list(range(size))

    if distribution == "reverse":
        return list(range(size, 0, -1))

    if distribution == "duplicates":
        return [
            random.choice([1, 2, 3, 4, 5])
            for _ in range(size)
        ]

    raise ValueError(
        f"Unknown distribution: {distribution}"
    )


# Measure how long one function call takes.
def time_call(function, data) -> float:
    start_time = time.perf_counter()

    function(data)

    end_time = time.perf_counter()

    return end_time - start_time


# Run all benchmark tests.
def main() -> None:
    sizes = [
        100,
        500,
        1000,
        2000,
        4000,
    ]

    distributions = [
        "random",
        "sorted",
        "reverse",
        "duplicates",
    ]

    algorithms = {
        "deterministic": quicksort,
        "randomized": randomized_quicksort,
    }

    rows = []

    # Test each input distribution.
    for distribution in distributions:

        # Test each input size.
        for size in sizes:

            # Test both Quick Sort versions.
            for algorithm_name, algorithm_function in algorithms.items():
                times = []

                # Run the same test several times.
                for _ in range(REPEATS):
                    data = make_input(
                        size,
                        distribution
                    )

                    runtime = time_call(
                        algorithm_function,
                        data
                    )

                    times.append(runtime)

                # Calculate the average time.
                average_time = mean(times)

                rows.append(
                    {
                        "distribution": distribution,
                        "size": size,
                        "algorithm": algorithm_name,
                        "avg_time_sec": average_time,
                    }
                )

                print(
                    f"{distribution:>10} | "
                    f"n={size:<5} | "
                    f"{algorithm_name:<13} | "
                    f"{average_time:.6f} s"
                )

    # Save the timing results.
    with open(
        "results.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "distribution",
                "size",
                "algorithm",
                "avg_time_sec",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    # Create the benchmark chart.
    plot_results(
        rows,
        distributions,
        sizes
    )


# Create charts from the timing results.
def plot_results(
    rows,
    distributions,
    sizes,
) -> None:
    figure, axes = plt.subplots(
        2,
        2,
        figsize=(12, 9)
    )

    axes = axes.flatten()

    # Create one chart for each distribution.
    for axis, distribution in zip(
        axes,
        distributions
    ):
        deterministic_times = [
            row["avg_time_sec"]
            for row in rows
            if (
                row["distribution"] == distribution
                and row["algorithm"] == "deterministic"
            )
        ]

        randomized_times = [
            row["avg_time_sec"]
            for row in rows
            if (
                row["distribution"] == distribution
                and row["algorithm"] == "randomized"
            )
        ]

        # Plot both algorithms.
        axis.plot(
            sizes,
            deterministic_times,
            marker="o",
            label="Deterministic"
        )

        axis.plot(
            sizes,
            randomized_times,
            marker="s",
            label="Randomized"
        )

        axis.set_title(
            f"{distribution.capitalize()} input"
        )

        axis.set_xlabel("Input size (n)")
        axis.set_ylabel("Time (seconds)")
        axis.legend()
        axis.grid(True, alpha=0.3)

    figure.suptitle(
        "Deterministic vs. Randomized Quicksort: Running Time",
        fontsize=14
    )

    figure.tight_layout()

    # Save the chart as an image.
    figure.savefig(
        "benchmark_chart.png",
        dpi=150
    )

    plt.close(figure)

    print(
        "\nSaved results.csv and benchmark_chart.png"
    )


# Start the program.
if __name__ == "__main__":
    main()