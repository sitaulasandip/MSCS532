"""
stress_test.py

Runs large-scale and edge-case tests for the
production-line inspection system.

Run with:
    python stress_test.py
"""

import random
import string
import time
import tracemalloc

from inspection_system import (
    InspectionRegistry,
    SKUTrie,
    StationQueue,
    TriageQueue,
)

random.seed(7)


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")

    if not condition:
        raise AssertionError(label)


# Test the system with a large number of units.
def stress_large_scale(size: int = 500_000) -> None:
    print(f"\n=== Large-scale test: {size:,} units ===")

    registry = InspectionRegistry()
    station_queue = StationQueue()
    triage_queue = TriageQueue()

    start_time = time.perf_counter()

    for index in range(size):
        serial_number = f"SN-{index:08d}"
        registry.start_unit(serial_number, "intake")
        station_queue.enqueue(serial_number)

    build_time = time.perf_counter() - start_time

    start_time = time.perf_counter()

    while len(station_queue) > 0:
        serial_number = station_queue.dequeue()

        registry.update_stage(
            serial_number,
            "data_wipe",
            True,
        )

        triage_queue.push(
            serial_number,
            random.randint(0, 1),
        )

    queue_time = time.perf_counter() - start_time

    start_time = time.perf_counter()
    removed_count = 0

    while len(triage_queue) > 0:
        triage_queue.pop_highest_priority()
        removed_count += 1

    triage_time = time.perf_counter() - start_time

    check(
        f"registry holds {size:,} records",
        len(registry) == size,
    )

    check(
        f"all {size:,} units removed from triage",
        removed_count == size,
    )

    print(
        f"    build: {build_time:.3f}s, "
        f"queue and update: {queue_time:.3f}s, "
        f"triage drain: {triage_time:.3f}s"
    )

    tracemalloc.start()

    for index in range(size):
        registry.close_unit(f"SN-{index:08d}")

    check(
        "registry empty after closing all units",
        len(registry) == 0,
    )

    tracemalloc.stop()


# Test unusual and edge-case inputs.
def stress_edge_cases() -> None:
    print("\n=== Edge-case tests ===")

    registry = InspectionRegistry()

    # Empty serial number.
    registry.start_unit("", "intake")

    check(
        "empty serial number is accepted",
        registry.get_record("") is not None,
    )

    # Empty SKU.
    trie = SKUTrie()
    trie.insert("")

    check(
        "empty SKU can be inserted",
        trie.contains("") is True,
    )

    check(
        "empty prefix matches",
        trie.has_prefix("") is True,
    )

    # Register the same serial number twice.
    registry.start_unit("SN-DUP", "intake")
    registry.update_stage("SN-DUP", "data_wipe", True)
    registry.start_unit("SN-DUP", "intake")

    duplicate_record = registry.get_record("SN-DUP")

    check(
        "re-registering resets stage history",
        duplicate_record.stage_results == {},
    )

    # Very long SKU.
    long_sku = "".join(
        random.choices(
            string.ascii_uppercase,
            k=10_000,
        )
    )

    trie.insert(long_sku)

    check(
        "10,000-character SKU is accepted",
        trie.contains(long_sku) is True,
    )

    # Unicode values.
    unicode_serial = "SN-éè中文"
    registry.start_unit(unicode_serial, "intake")

    check(
        "unicode serial number is accepted",
        registry.get_record(unicode_serial) is not None,
    )

    unicode_sku = "SKÚUNICØDE"
    trie.insert(unicode_sku)

    check(
        "unicode SKU is accepted",
        trie.contains(unicode_sku) is True,
    )

    # Negative, zero, and positive priorities.
    triage = TriageQueue()
    triage.push("A", -5)
    triage.push("B", 0)
    triage.push("C", 5)

    priority_order = [
        triage.pop_highest_priority()
        for _ in range(3)
    ]

    check(
        "priorities are returned in correct order",
        priority_order == ["C", "B", "A"],
    )

    # Remove from empty queues.
    empty_triage = TriageQueue()

    first_pop = empty_triage.pop_highest_priority()
    second_pop = empty_triage.pop_highest_priority()

    check(
        "empty triage queue returns None",
        first_pop is None and second_pop is None,
    )

    empty_station = StationQueue()

    first_dequeue = empty_station.dequeue()
    second_dequeue = empty_station.dequeue()

    check(
        "empty station queue returns None",
        first_dequeue is None and second_dequeue is None,
    )

    # Queue with zero capacity.
    zero_queue = StationQueue(maxlen=0)
    zero_queue.enqueue("X")

    check(
        "zero-capacity queue stays empty",
        len(zero_queue) == 0,
    )

    # Empty bulk load.
    triage.load_many([])

    check(
        "empty bulk load does not fail",
        True,
    )

    # Update a closed record.
    registry.start_unit("SN-CLOSE-ME", "intake")
    registry.close_unit("SN-CLOSE-ME")

    try:
        registry.update_stage(
            "SN-CLOSE-ME",
            "data_wipe",
            True,
        )

        check(
            "closed record raises KeyError",
            False,
        )

    except KeyError:
        check(
            "closed record raises KeyError",
            True,
        )


# Test repeated record creation and removal.
def stress_churn(cycles: int = 200_000) -> None:
    print(f"\n=== Churn test: {cycles:,} cycles ===")

    registry = InspectionRegistry()

    tracemalloc.start()
    baseline_memory, _ = tracemalloc.get_traced_memory()

    for index in range(cycles):
        serial_number = f"SN-CHURN-{index % 1000:04d}"

        registry.start_unit(serial_number, "intake")
        registry.update_stage(serial_number, "data_wipe", True)
        registry.close_unit(serial_number)

    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    check(
        f"registry empty after {cycles:,} cycles",
        len(registry) == 0,
    )

    print(
        f"    baseline: {baseline_memory / 1024:.1f} KB, "
        f"after churn: {current_memory / 1024:.1f} KB, "
        f"peak: {peak_memory / 1024:.1f} KB"
    )

    check(
        "memory stays close to baseline",
        current_memory < baseline_memory + 50_000,
    )


if __name__ == "__main__":
    stress_large_scale()
    stress_edge_cases()
    stress_churn()

    print("\nAll stress tests passed.")