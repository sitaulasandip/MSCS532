"""
benchmark.py

Compares optimized data structures with simpler versions.

The benchmarks test:
1. StationQueue deque vs. a list queue
2. TriageQueue push loop vs. bulk loading
3. SKUTrie cached vs. uncached searches
4. InspectionRecord memory with and without slots
"""

import gc
import random
import string
import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Dict, Optional

from inspection_system import (
    InspectionRecord,
    SKUTrie,
    StationQueue,
    TriageQueue,
)

random.seed(42)

SIZES = [
    100,
    1_000,
    10_000,
    100_000,
]


@dataclass
class UnslottedRecord:
    """Inspection record without slots."""

    serial_number: str
    station_id: str
    stage_results: Dict[str, bool] = field(
        default_factory=dict
    )
    grade: Optional[str] = None


class NaiveListQueue:
    """Queue built with a regular Python list."""

    def __init__(self) -> None:
        self._items = []

    def enqueue(self, serial_number: str) -> None:
        self._items.append(serial_number)

    def dequeue(self):
        if not self._items:
            return None

        return self._items.pop(0)


def random_serial(index: int) -> str:
    return f"SN-{index:07d}"


def random_sku(length: int = 8) -> str:
    characters = (
        string.ascii_uppercase
        + string.digits
    )

    return "".join(
        random.choices(
            characters,
            k=length
        )
    )


# Compare deque queue and list queue.
def bench_queue(size: int):
    serials = [
        random_serial(index)
        for index in range(size)
    ]

    deque_queue = StationQueue()

    start_time = time.perf_counter()

    for serial in serials:
        deque_queue.enqueue(serial)

    for _ in range(size):
        deque_queue.dequeue()

    deque_time = (
        time.perf_counter()
        - start_time
    )

    list_queue = NaiveListQueue()

    start_time = time.perf_counter()

    for serial in serials:
        list_queue.enqueue(serial)

    for _ in range(size):
        list_queue.dequeue()

    list_time = (
        time.perf_counter()
        - start_time
    )

    return deque_time, list_time


# Compare individual pushes and bulk loading.
def bench_triage_bulk_load(size: int):
    entries = [
        (
            random_serial(index),
            random.randint(0, 1),
        )
        for index in range(size)
    ]

    push_queue = TriageQueue()

    start_time = time.perf_counter()

    for serial, priority in entries:
        push_queue.push(
            serial,
            priority
        )

    push_time = (
        time.perf_counter()
        - start_time
    )

    bulk_queue = TriageQueue()

    start_time = time.perf_counter()

    bulk_queue.load_many(entries)

    bulk_time = (
        time.perf_counter()
        - start_time
    )

    return push_time, bulk_time


# Compare cached and uncached trie searches.
def bench_trie_cache(
    number_of_skus: int,
    number_of_lookups: int,
):
    skus = [
        random_sku()
        for _ in range(number_of_skus)
    ]

    trie = SKUTrie()

    for sku in skus:
        trie.insert(sku)

    hot_skus = skus[
        :max(1, number_of_skus // 20)
    ]

    lookups = [
        random.choice(hot_skus)
        for _ in range(number_of_lookups)
    ]

    # Time searches with caching.
    trie._contains_cache.clear()

    start_time = time.perf_counter()

    for sku in lookups:
        trie.contains(sku)

    cached_time = (
        time.perf_counter()
        - start_time
    )

    # Time searches without caching.
    start_time = time.perf_counter()

    for sku in lookups:
        trie._contains_cache.clear()
        trie.contains(sku)

    uncached_time = (
        time.perf_counter()
        - start_time
    )

    return cached_time, uncached_time


# Compare memory use with and without slots.
def bench_record_memory(size: int):
    gc.collect()
    tracemalloc.start()

    slotted_records = [
        InspectionRecord(
            random_serial(index),
            "intake"
        )
        for index in range(size)
    ]

    _, slotted_peak = (
        tracemalloc.get_traced_memory()
    )

    tracemalloc.stop()

    del slotted_records
    gc.collect()

    tracemalloc.start()

    unslotted_records = [
        UnslottedRecord(
            random_serial(index),
            "intake"
        )
        for index in range(size)
    ]

    _, unslotted_peak = (
        tracemalloc.get_traced_memory()
    )

    tracemalloc.stop()

    del unslotted_records
    gc.collect()

    return slotted_peak, unslotted_peak


def main():
    print(
        "=== Benchmark 1: StationQueue "
        "(deque) vs. list queue ==="
    )

    print(
        f"{'n':>10} | "
        f"{'deque (s)':>12} | "
        f"{'list (s)':>12} | "
        f"speedup"
    )

    for size in SIZES:
        deque_time, list_time = bench_queue(
            size
        )

        if deque_time > 0:
            speedup = list_time / deque_time
        else:
            speedup = float("inf")

        print(
            f"{size:>10} | "
            f"{deque_time:>12.5f} | "
            f"{list_time:>12.5f} | "
            f"{speedup:>6.1f}x"
        )

    print(
        "\n=== Benchmark 2: TriageQueue "
        "push loop vs. load_many ==="
    )

    print(
        f"{'n':>10} | "
        f"{'push loop (s)':>14} | "
        f"{'load_many (s)':>14} | "
        f"speedup"
    )

    for size in SIZES:
        push_time, bulk_time = (
            bench_triage_bulk_load(size)
        )

        if bulk_time > 0:
            speedup = push_time / bulk_time
        else:
            speedup = float("inf")

        print(
            f"{size:>10} | "
            f"{push_time:>14.5f} | "
            f"{bulk_time:>14.5f} | "
            f"{speedup:>6.1f}x"
        )

    print(
        "\n=== Benchmark 3: SKUTrie "
        "cached vs. uncached ==="
    )

    print(
        f"{'catalog size':>12} | "
        f"{'cached (s)':>12} | "
        f"{'uncached (s)':>13} | "
        f"speedup"
    )

    for size in SIZES:
        cached_time, uncached_time = (
            bench_trie_cache(
                size,
                10_000
            )
        )

        if cached_time > 0:
            speedup = (
                uncached_time
                / cached_time
            )
        else:
            speedup = float("inf")

        print(
            f"{size:>12} | "
            f"{cached_time:>12.5f} | "
            f"{uncached_time:>13.5f} | "
            f"{speedup:>6.1f}x"
        )

    print(
        "\n=== Benchmark 4: "
        "InspectionRecord memory ==="
    )

    print(
        f"{'n':>10} | "
        f"{'slotted (KB)':>13} | "
        f"{'unslotted (KB)':>15} | "
        f"reduction"
    )

    for size in SIZES:
        slotted_peak, unslotted_peak = (
            bench_record_memory(size)
        )

        if unslotted_peak:
            reduction = (
                1
                - slotted_peak
                / unslotted_peak
            ) * 100
        else:
            reduction = 0

        print(
            f"{size:>10} | "
            f"{slotted_peak / 1024:>13.1f} | "
            f"{unslotted_peak / 1024:>15.1f} | "
            f"{reduction:>6.1f}%"
        )


if __name__ == "__main__":
    main()