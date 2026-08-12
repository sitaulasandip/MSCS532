

import gc
import random
import time
from dataclasses import dataclass
from typing import Iterator, List


# Represents one node in the singly linked list.
@dataclass
class Node:
    value: int
    next: "Node | None" = None


# Simple singly linked list with O(1) append and O(n) traversal.
class LinkedList:
    def __init__(self) -> None:
        self._head: Node | None = None
        self._tail: Node | None = None
        self._size = 0

    def append(self, value: int) -> None:
        # Add a new value to the end of the linked list.
        node = Node(value)

        if self._head is None:
            self._head = node
        else:
            self._tail.next = node  # type: ignore[union-attr]

        self._tail = node
        self._size += 1

    def __iter__(self) -> Iterator[int]:
        # Traverse nodes from the head to the end of the list.
        current = self._head

        while current is not None:
            yield current.value
            current = current.next

    def __len__(self) -> int:
        return self._size


# Build a contiguous Python list from the same input values.
def build_array(values: List[int]) -> List[int]:
    return list(values)


# Measure the time required to traverse and sum all values.
def time_traversal_sum(container) -> float:
    start = time.perf_counter()

    total = 0

    for value in container:
        total += value

    elapsed = time.perf_counter() - start

    return elapsed


# Compare average traversal time for both data structures.
def run_benchmark(
    sizes: List[int],
    repeats: int = 5,
) -> dict:

    results = {
        "n": [],
        "linked_list": [],
        "array": [],
        "speedup": [],
    }

    for n in sizes:
        # Use the same random data for both structures.
        random.seed(42)

        values = [
            random.randint(0, 1_000_000)
            for _ in range(n)
        ]

        # Build both structures using identical values.
        linked = LinkedList()

        for v in values:
            linked.append(v)

        arr = build_array(values)

        # Measure linked-list traversal time.
        gc.collect()

        ll_times = [
            time_traversal_sum(linked)
            for _ in range(repeats)
        ]

        # Measure contiguous-list traversal time.
        gc.collect()

        arr_times = [
            time_traversal_sum(arr)
            for _ in range(repeats)
        ]

        # Calculate average execution times.
        ll_avg = sum(ll_times) / repeats
        arr_avg = sum(arr_times) / repeats

        results["n"].append(n)
        results["linked_list"].append(ll_avg)
        results["array"].append(arr_avg)

        # Calculate how much faster the contiguous list is.
        results["speedup"].append(
            ll_avg / arr_avg
            if arr_avg > 0
            else float("nan")
        )

        print(
            f"n={n:>9,d}  "
            f"linked_list={ll_avg * 1000:9.3f} ms  "
            f"array={arr_avg * 1000:9.3f} ms  "
            f"speedup={ll_avg / arr_avg:5.2f}x"
        )

    return results


# Run the benchmark at increasing input sizes.
if __name__ == "__main__":
    print("=" * 78)

    print(
        "Benchmark 1: Sequential traversal -- "
        "LinkedList vs contiguous array"
    )

    print(
        "Reproduces the CGAL-8855eb5 / "
        "TileDB-d51b082 optimization pattern"
    )

    print(
        "from Azad et al. (2023), Section IV-A-1a"
    )

    print("=" * 78)

    sizes = [
        10_000,
        50_000,
        100_000,
        500_000,
        1_000_000,
        2_000_000,
    ]

    run_benchmark(sizes)