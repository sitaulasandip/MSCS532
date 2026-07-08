

import csv
import time
import random
import tracemalloc
import statistics
from pathlib import Path

from sorting import merge_sort, quick_sort

# Create results folder.
RESULTS = Path(__file__).resolve().parent.parent / "results"
RESULTS.mkdir(exist_ok=True)

# Keep random data the same every time.
random.seed(42)


# Create test data.
def make_dataset(n, kind):
    base = list(range(n))

    if kind == "random":
        data = base[:]
        random.shuffle(data)
        return data

    if kind == "sorted":
        return base

    if kind == "reverse":
        return base[::-1]

    raise ValueError(kind)


# Measure sorting time.
def time_sort(sort_function, data, trials=5):
    times = []

    for _ in range(trials):
        work = data[:]
        start = time.perf_counter()
        sort_function(work)
        end = time.perf_counter()
        times.append(end - start)

    return statistics.median(times)


# Measure memory usage.
def peak_memory(sort_function, data):
    work = data[:]

    tracemalloc.start()
    sort_function(work)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return peak / 1024.0


# Sorting algorithms to test.
ALGORITHMS = {
    "merge_sort": lambda a: merge_sort(a),
    "quick_sort": lambda a: quick_sort(a, randomized=False),
    "randomized_quick_sort": lambda a: quick_sort(a, randomized=True),
}


# Test sorting speed on random data.
def experiment_random_scaling():
    sizes = [1000, 2000, 4000, 8000, 16000, 32000]
    rows = []

    for n in sizes:
        data = make_dataset(n, "random")
        row = {"n": n}

        for name, fn in ALGORITHMS.items():
            row[name] = round(time_sort(fn, data), 6)

        rows.append(row)

        print(
            f"[random data] n={n:>6}  "
            + "  ".join(f"{k}={row[k]:.4f}s" for k in ALGORITHMS)
        )

    with open(RESULTS / "random_timing.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["n", *ALGORITHMS])
        writer.writeheader()
        writer.writerows(rows)

    return rows


# Test Quick Sort on sorted, reverse, and random data.
def experiment_quicksort_worstcase():
    sizes = [500, 1000, 2000, 4000]
    kinds = ["random", "sorted", "reverse"]
    rows = []

    for n in sizes:
        row = {"n": n}

        for kind in kinds:
            data = make_dataset(n, kind)
            row[kind] = round(
                time_sort(lambda a: quick_sort(a, randomized=False), data, trials=3),
                6
            )

        rows.append(row)

        print(
            f"[quick sort] n={n:>5}  "
            + "  ".join(f"{k}={row[k]:.4f}s" for k in kinds)
        )

    with open(RESULTS / "quicksort_worstcase.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["n", *kinds])
        writer.writeheader()
        writer.writerows(rows)

    return rows


# Test memory usage.
def experiment_memory():
    sizes = [1000, 2000, 4000, 8000, 16000, 32000]
    rows = []

    for n in sizes:
        data = make_dataset(n, "random")

        row = {
            "n": n,
            "merge_sort_kb": round(peak_memory(ALGORITHMS["merge_sort"], data), 1),
            "quick_sort_kb": round(
                peak_memory(ALGORITHMS["randomized_quick_sort"], data), 1
            ),
        }

        rows.append(row)

        print(
            f"[memory] n={n:>6}  "
            f"merge={row['merge_sort_kb']:.1f}KB  "
            f"quick={row['quick_sort_kb']:.1f}KB"
        )

    with open(RESULTS / "memory.csv", "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["n", "merge_sort_kb", "quick_sort_kb"]
        )
        writer.writeheader()
        writer.writerows(rows)

    return rows


if __name__ == "__main__":
    print("=== Experiment 1: Random Data Speed ===")
    experiment_random_scaling()

    print("\n=== Experiment 2: Quick Sort Worst Case ===")
    experiment_quicksort_worstcase()

    print("\n=== Experiment 3: Memory Usage ===")
    experiment_memory()

    print("\nAll results saved to:", RESULTS)
