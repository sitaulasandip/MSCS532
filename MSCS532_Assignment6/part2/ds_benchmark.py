"""
ds_benchmark.py

Compares array-backed and linked-list-backed
stack and queue implementations.

The program measures the time needed to add and
remove different numbers of elements.
"""

import csv
import os
import sys
import time

# Allow imports from the current folder.
sys.path.insert(
    0,
    os.path.dirname(__file__)
)

from data_structures import (
    ArrayQueue,
    ArrayStack,
    LinkedListQueue,
    LinkedListStack,
)


# Measure stack performance.
def time_stack(
    stack_class,
    size: int,
) -> float:
    stack = stack_class()

    start_time = time.perf_counter()

    for value in range(size):
        stack.push(value)

    for _ in range(size):
        stack.pop()

    return time.perf_counter() - start_time


# Measure queue performance.
def time_queue(
    queue_class,
    size: int,
) -> float:
    queue = queue_class()

    start_time = time.perf_counter()

    for value in range(size):
        queue.enqueue(value)

    for _ in range(size):
        queue.dequeue()

    return time.perf_counter() - start_time


# Run all benchmark tests.
def run() -> list:
    sizes = [
        1000,
        5000,
        10000,
        50000,
        100000,
    ]

    results = []

    for size in sizes:
        row = {
            "n": size,
            "array_stack_sec": time_stack(
                ArrayStack,
                size
            ),
            "linked_stack_sec": time_stack(
                LinkedListStack,
                size
            ),
            "array_queue_sec": time_queue(
                ArrayQueue,
                size
            ),
            "linked_queue_sec": time_queue(
                LinkedListQueue,
                size
            ),
        }

        results.append(row)

        print(
            f"n={size:>7} | "
            f"ArrStack="
            f"{row['array_stack_sec'] * 1000:8.2f} ms | "
            f"LLStack="
            f"{row['linked_stack_sec'] * 1000:8.2f} ms | "
            f"ArrQueue="
            f"{row['array_queue_sec'] * 1000:8.2f} ms | "
            f"LLQueue="
            f"{row['linked_queue_sec'] * 1000:8.2f} ms"
        )

    return results


# Save the results to a CSV file.
def write_csv(
    results,
    path: str,
) -> None:
    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    field_names = [
        "n",
        "array_stack_sec",
        "linked_stack_sec",
        "array_queue_sec",
        "linked_queue_sec",
    ]

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=field_names
        )

        writer.writeheader()
        writer.writerows(results)


# Start the benchmark.
if __name__ == "__main__":
    benchmark_results = run()

    output_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "results",
        "ds_benchmark_results.csv"
    )

    write_csv(
        benchmark_results,
        output_path
    )

    print(
        f"Saved results to {output_path}"
    )