# Stress tests for the inspection system.

import random
import string
import time
import tracemalloc

from inspection_system import (
    InspectionRecord,
    InspectionRegistry,
    StationQueue,
    TriageQueue,
    SKUTrie,
)

random.seed(7)


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")

    if not condition:
        raise AssertionError(label)


# Test large-scale processing.

def stress_large_scale(n: int = 500_000) -> None:
    print(
        f"\n=== Stress test: {n:,} units through "
        "registry, queue, and triage ==="
    )

    registry = InspectionRegistry()
    queue = StationQueue()
    triage = TriageQueue()

    start = time.perf_counter()

    for i in range(n):
        serial = f"SN-{i:08d}"
        registry.start_unit(serial, "intake")
        queue.enqueue(serial)

    build_time = time.perf_counter() - start

    start = time.perf_counter()

    while len(queue) > 0:
        serial = queue.dequeue()
        registry.update_stage(
            serial,
            "data_wipe",
            True,
        )
        triage.push(
            serial,
            random.randint(0, 1),
        )

    drain_time = time.perf_counter() - start

    start = time.perf_counter()
    popped = 0

    while len(triage) > 0:
        triage.pop_highest_priority()
        popped += 1

    triage_time = time.perf_counter() - start

    check(
        f"registry holds {n:,} records",
        len(registry) == n,
    )

    check(
        f"all {n:,} units drained from triage",
        popped == n,
    )

    print(
        f"    build: {build_time:.3f}s, "
        f"drain+wipe: {drain_time:.3f}s, "
        f"triage drain: {triage_time:.3f}s"
    )

    # Remove all records and check cleanup.
    tracemalloc.start()

    for i in range(n):
        registry.close_unit(
            f"SN-{i:08d}"
        )

    check(
        "registry empty after closing all units",
        len(registry) == 0,
    )

    tracemalloc.stop()


# Test unexpected inputs.

def stress_edge_cases() -> None:
    print(
        "\n=== Stress test: unexpected inputs ==="
    )

    # Test empty serial number.
    registry = InspectionRegistry()
    registry.start_unit("", "intake")

    check(
        "empty-string serial number is accepted",
        registry.get_record("") is not None,
    )

    # Test empty SKU.
    trie = SKUTrie()
    trie.insert("")

    check(
        "empty-string SKU can be inserted",
        trie.contains("") is True,
    )

    check(
        "empty-string prefix matches everything",
        trie.has_prefix("") is True,
    )

    # Test duplicate serial registration.
    registry.start_unit(
        "SN-DUP",
        "intake",
    )

    registry.update_stage(
        "SN-DUP",
        "data_wipe",
        True,
    )

    registry.start_unit(
        "SN-DUP",
        "intake",
    )

    check(
        "re-registering a serial resets its stage history",
        registry.get_record(
            "SN-DUP"
        ).stage_results == {},
    )

    # Test a very long SKU.
    long_sku = "".join(
        random.choices(
            string.ascii_uppercase,
            k=10_000,
        )
    )

    trie.insert(long_sku)

    check(
        "10,000-character SKU inserts without error",
        trie.contains(long_sku) is True,
    )

    # Test Unicode values.
    unicode_serial = "SN-éè中文"

    registry.start_unit(
        unicode_serial,
        "intake",
    )

    check(
        "unicode serial number is accepted",
        registry.get_record(
            unicode_serial
        ) is not None,
    )

    trie.insert("SKÚUNICØDE")

    check(
        "unicode SKU is accepted",
        trie.contains("SKÚUNICØDE") is True,
    )

    # Test different priority values.
    triage = TriageQueue()

    triage.push("A", -5)
    triage.push("B", 0)
    triage.push("C", 5)

    order = [
        triage.pop_highest_priority()
        for _ in range(3)
    ]

    check(
        "negative priority sorts below zero and positive",
        order == ["C", "B", "A"],
    )

    # Test empty priority queue.
    empty_triage = TriageQueue()

    check(
        "popping empty TriageQueue twice returns None",
        empty_triage.pop_highest_priority() is None
        and empty_triage.pop_highest_priority() is None,
    )

    # Test empty station queue.
    empty_queue = StationQueue()

    check(
        "dequeuing empty StationQueue twice returns None",
        empty_queue.dequeue() is None
        and empty_queue.dequeue() is None,
    )

    # Test queue with zero capacity.
    zero_queue = StationQueue(maxlen=0)
    zero_queue.enqueue("X")

    check(
        "maxlen=0 queue never holds anything",
        len(zero_queue) == 0,
    )

    # Test empty bulk load.
    triage.load_many([])

    check(
        "load_many([]) does not raise",
        True,
    )

    # Test update after closing a unit.
    registry.start_unit(
        "SN-CLOSE-ME",
        "intake",
    )

    registry.close_unit(
        "SN-CLOSE-ME"
    )

    try:
        registry.update_stage(
            "SN-CLOSE-ME",
            "data_wipe",
            True,
        )

        check(
            "update_stage on a closed unit raises KeyError",
            False,
        )

    except KeyError:
        check(
            "update_stage on a closed unit raises KeyError",
            True,
        )


# Test repeated start and close cycles.

def stress_churn(
    cycles: int = 200_000,
) -> None:
    print(
        f"\n=== Stress test: {cycles:,} "
        "rapid start/close cycles ==="
    )

    registry = InspectionRegistry()

    tracemalloc.start()
    baseline, _ = tracemalloc.get_traced_memory()

    for i in range(cycles):
        # Reuse a small group of serial numbers.
        serial = (
            f"SN-CHURN-{i % 1000:04d}"
        )

        registry.start_unit(
            serial,
            "intake",
        )

        registry.update_stage(
            serial,
            "data_wipe",
            True,
        )

        registry.close_unit(serial)

    current, peak = (
        tracemalloc.get_traced_memory()
    )

    tracemalloc.stop()

    check(
        f"registry empty after {cycles:,} churn cycles",
        len(registry) == 0,
    )

    print(
        f"    baseline: {baseline / 1024:.1f} KB, "
        f"after churn: {current / 1024:.1f} KB, "
        f"peak during churn: {peak / 1024:.1f} KB"
    )

    check(
        "memory after churn stays close to baseline (no leak)",
        current < baseline + 50_000,
    )


if __name__ == "__main__":
    stress_large_scale()
    stress_edge_cases()
    stress_churn()

    print("\nAll stress tests passed.")