# Benchmark optimized data structures against basic versions.

import gc
import random
import string
import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Dict, Optional

from inspection_system import (
    InspectionRecord,
    StationQueue,
    TriageQueue,
    SKUTrie,
)

random.seed(42)

SIZES = [100, 1_000, 10_000, 100_000]


# Basic versions for comparison.

@dataclass
class UnslottedRecord:
    # Record without slots.
    serial_number: str
    station_id: str
    stage_results: Dict[str, bool] = field(default_factory=dict)
    grade: Optional[str] = None


class NaiveListQueue:
    # Simple list-based queue.

    def __init__(self) -> None:
        self._items = []

    def enqueue(self, serial_number: str) -> None:
        self._items.append(serial_number)

    def dequeue(self):
        if not self._items:
            return None
        return self._items.pop(0)  # Remove first item.


def random_serial(i: int) -> str:
    return f"SN-{i:07d}"


def random_sku(length: int = 8) -> str:
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )


# Test queue performance.

def bench_queue(n: int):
    serials = [random_serial(i) for i in range(n)]

    deque_q = StationQueue()
    start = time.perf_counter()
    for s in serials:
        deque_q.enqueue(s)
    for _ in range(n):
        deque_q.dequeue()
    deque_time = time.perf_counter() - start

    naive_q = NaiveListQueue()
    start = time.perf_counter()
    for s in serials:
        naive_q.enqueue(s)
    for _ in range(n):
        naive_q.dequeue()
    naive_time = time.perf_counter() - start

    return deque_time, naive_time


# Test bulk loading performance.

def bench_triage_bulk_load(n: int):
    entries = [
        (random_serial(i), random.randint(0, 1))
        for i in range(n)
    ]

    push_loop = TriageQueue()
    start = time.perf_counter()
    for serial, priority in entries:
        push_loop.push(serial, priority)
    push_time = time.perf_counter() - start

    bulk = TriageQueue()
    start = time.perf_counter()
    bulk.load_many(entries)
    bulk_time = time.perf_counter() - start

    return push_time, bulk_time


# Test SKU lookup caching.

def bench_trie_cache(n_skus: int, n_lookups: int):
    skus = [random_sku() for _ in range(n_skus)]

    trie = SKUTrie()
    for sku in skus:
        trie.insert(sku)

    # Use common SKUs for repeated lookups.
    hot_skus = skus[: max(1, n_skus // 20)]
    lookups = [
        random.choice(hot_skus)
        for _ in range(n_lookups)
    ]

    # Test with cache.
    trie._contains_cache.clear()
    start = time.perf_counter()
    for sku in lookups:
        trie.contains(sku)
    cached_time = time.perf_counter() - start

    # Test without cache.
    start = time.perf_counter()
    for sku in lookups:
        trie._contains_cache.clear()
        trie.contains(sku)
    uncached_time = time.perf_counter() - start

    return cached_time, uncached_time


# Test record memory usage.

def bench_record_memory(n: int):
    gc.collect()
    tracemalloc.start()

    slotted = [
        InspectionRecord(random_serial(i), "intake")
        for i in range(n)
    ]

    _, slotted_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    del slotted
    gc.collect()

    tracemalloc.start()

    unslotted = [
        UnslottedRecord(random_serial(i), "intake")
        for i in range(n)
    ]

    _, unslotted_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    del unslotted
    gc.collect()

    return slotted_peak, unslotted_peak


# Run all benchmarks.

def main():
    print(
        "=== Benchmark 1: StationQueue (deque) "
        "vs. naive list queue ==="
    )
    print(
        f"{'n':>10} | {'deque (s)':>12} | "
        f"{'naive list (s)':>15} | speedup"
    )

    for n in SIZES:
        deque_time, naive_time = bench_queue(n)

        speedup = (
            naive_time / deque_time
            if deque_time > 0
            else float("inf")
        )

        print(
            f"{n:>10} | {deque_time:>12.5f} | "
            f"{naive_time:>15.5f} | {speedup:>6.1f}x"
        )

    print(
        "\n=== Benchmark 2: TriageQueue push-loop "
        "vs. load_many (heapify) ==="
    )
    print(
        f"{'n':>10} | {'push-loop (s)':>14} | "
        f"{'load_many (s)':>14} | speedup"
    )

    for n in SIZES:
        push_time, bulk_time = bench_triage_bulk_load(n)

        speedup = (
            push_time / bulk_time
            if bulk_time > 0
            else float("inf")
        )

        print(
            f"{n:>10} | {push_time:>14.5f} | "
            f"{bulk_time:>14.5f} | {speedup:>6.1f}x"
        )

    print(
        "\n=== Benchmark 3: SKUTrie.contains() cached "
        "vs. uncached (10,000 lookups) ==="
    )
    print(
        f"{'catalog size':>12} | {'cached (s)':>12} | "
        f"{'uncached (s)':>13} | speedup"
    )

    for n in SIZES:
        cached_time, uncached_time = bench_trie_cache(
            n,
            10_000,
        )

        speedup = (
            uncached_time / cached_time
            if cached_time > 0
            else float("inf")
        )

        print(
            f"{n:>12} | {cached_time:>12.5f} | "
            f"{uncached_time:>13.5f} | {speedup:>6.1f}x"
        )

    print(
        "\n=== Benchmark 4: InspectionRecord memory, "
        "slots vs. no slots ==="
    )
    print(
        f"{'n':>10} | {'slotted (KB)':>13} | "
        f"{'unslotted (KB)':>15} | reduction"
    )

    for n in SIZES:
        slotted_peak, unslotted_peak = bench_record_memory(n)

        reduction = (
            (1 - slotted_peak / unslotted_peak) * 100
            if unslotted_peak
            else 0
        )

        print(
            f"{n:>10} | {slotted_peak / 1024:>13.1f} | "
            f"{unslotted_peak / 1024:>15.1f} | "
            f"{reduction:>6.1f}%"
        )


if __name__ == "__main__":
    main()