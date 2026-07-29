
"""
empirical_analysis.py

Compares Median of Medians and Randomized Quickselect.

The program tests:
1. Different input sizes
2. Random, sorted, and reverse-sorted data
3. The time needed to find the median

Results are saved as:
1. results/benchmark_results.csv
2. results/benchmark_plot.png
"""

import csv
import os
import random
import sys
import time

# Allow imports from the current folder.
sys.path.insert(
    0,
    os.path.dirname(__file__)
)

# Increase the recursion limit.
sys.setrecursionlimit(10000)

from median_of_medians import median_of_medians_select
from quickselect import randomized_quickselect_in_place


# Create test data.
def make_array(
    size: int,
    distribution: str,
) -> list:
    if distribution == "random":
        return [
            random.randint(-1_000_000, 1_000_000)
            for _ in range(size)
        ]

    if distribution == "sorted":
        return list(range(size))

    if distribution == "reverse_sorted":
        return list(range(size, 0, -1))

    raise ValueError(
        f"Unknown distribution: {distribution}"
    )


# Measure the fastest runtime.
def time_call(
    function,
    array,
    k,
    trials=3,
) -> float:
    best_time = float("inf")

    for _ in range(trials):
        # Use a fresh copy for every trial.
        array_copy = array[:]

        start_time = time.perf_counter()

        function(
            array_copy,
            k
        )

        elapsed_time = (
            time.perf_counter() - start_time
        )

        best_time = min(
            best_time,
            elapsed_time
        )

    return best_time


# Run all benchmark tests.
def run_benchmark() -> list:
    sizes = [
        100,
        500,
        1000,
        2000,
        4000,
        8000,
    ]

    distributions = [
        "random",
        "sorted",
        "reverse_sorted",
    ]

    results = []

    # Test each data distribution.
    for distribution in distributions:

        # Test each input size.
        for size in sizes:
            array = make_array(
                size,
                distribution
            )

            # Find the middle position.
            k = max(
                1,
                size // 2
            )

            # Measure both algorithms.
            median_time = time_call(
                median_of_medians_select,
                array,
                k
            )

            quickselect_time = time_call(
                randomized_quickselect_in_place,
                array,
                k
            )

            results.append(
                {
                    "distribution": distribution,
                    "n": size,
                    "median_of_medians_sec": median_time,
                    "quickselect_sec": quickselect_time,
                }
            )

            print(
                f"{distribution:>15} | "
                f"n={size:>6} | "
                f"MoM={median_time * 1000:8.3f} ms | "
                f"QS={quickselect_time * 1000:8.3f} ms"
            )

    return results


# Save benchmark results to a CSV file.
def write_csv(
    results,
    path,
) -> None:
    # Create the results folder if needed.
    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "distribution",
                "n",
                "median_of_medians_sec",
                "quickselect_sec",
            ],
        )

        writer.writeheader()
        writer.writerows(results)


# Create a chart from the benchmark results.
def make_plot(
    results,
    path,
) -> None:
    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    distributions = sorted(
        {
            row["distribution"]
            for row in results
        }
    )

    figure, axes = plt.subplots(
        1,
        len(distributions),
        figsize=(15, 4.5),
        sharey=True
    )

    # Create one chart for each distribution.
    for axis, distribution in zip(
        axes,
        distributions
    ):
        rows = [
            row
            for row in results
            if row["distribution"] == distribution
        ]

        rows.sort(
            key=lambda row: row["n"]
        )

        sizes = [
            row["n"]
            for row in rows
        ]

        median_times = [
            row["median_of_medians_sec"] * 1000
            for row in rows
        ]

        quickselect_times = [
            row["quickselect_sec"] * 1000
            for row in rows
        ]

        # Plot both algorithms.
        axis.plot(
            sizes,
            median_times,
            marker="o",
            label="Median of Medians"
        )

        axis.plot(
            sizes,
            quickselect_times,
            marker="s",
            label="Randomized Quickselect"
        )

        axis.set_title(
            distribution
            .replace("_", " ")
            .title()
        )

        axis.set_xlabel("Input size (n)")
        axis.grid(True, alpha=0.3)

    axes[0].set_ylabel("Time (ms)")
    axes[0].legend()

    figure.suptitle(
        "Median of Medians vs Randomized Quickselect"
    )

    figure.tight_layout()

    # Create the results folder if needed.
    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    figure.savefig(
        path,
        dpi=150
    )

    plt.close(figure)

    print(f"Saved plot to {path}")


# Start the benchmark.
if __name__ == "__main__":
    # Keep random results consistent.
    random.seed(42)

    benchmark_results = run_benchmark()

    results_folder = os.path.join(
        os.path.dirname(__file__),
        "..",
        "results"
    )

    csv_path = os.path.join(
        results_folder,
        "benchmark_results.csv"
    )

    plot_path = os.path.join(
        results_folder,
        "benchmark_plot.png"
    )

    write_csv(
        benchmark_results,
        csv_path
    )

    make_plot(
        benchmark_results,
        plot_path
    )

