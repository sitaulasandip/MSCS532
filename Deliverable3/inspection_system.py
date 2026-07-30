"""
inspection_system.py

Simple production-line inspection system using:
1. Dictionary for serial number lookup
2. Queue for station order
3. Priority queue for triage
4. Trie for SKU validation
"""

from __future__ import annotations

import heapq
import itertools
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional


# Inspection record
# slots=True (Python 3.10+) removes the per-instance __dict__ that a normal
# dataclass would otherwise carry, which matters here because the registry
# may hold tens of thousands of these records at once during a large batch.
@dataclass(slots=True)
class InspectionRecord:
    serial_number: str
    station_id: str
    stage_results: Dict[str, bool] = field(default_factory=dict)
    # Cosmetic/condition grade (e.g. "A", "B", "C"), recorded for
    # reference only.
    # This does NOT affect triage order - see TriageQueue below.
    grade: Optional[str] = None


# Hash table for inspection records
class InspectionRegistry:
    def __init__(self) -> None:
        # Store records using serial number as the key.
        self._records: Dict[str, InspectionRecord] = {}

    def start_unit(
        self,
        serial_number: str,
        station_id: str,
    ) -> InspectionRecord:
        # Create a new inspection record.
        record = InspectionRecord(serial_number, station_id)
        self._records[serial_number] = record
        return record

    def update_stage(
        self,
        serial_number: str,
        stage_name: str,
        passed: bool,
    ) -> None:
        # Find the record.
        record = self._records.get(serial_number)

        # Stop if the serial number does not exist.
        if record is None:
            raise KeyError(f"No active record for serial {serial_number}")

        # Save the inspection result.
        record.stage_results[stage_name] = passed

    def set_grade(self, serial_number: str, grade: str) -> None:
        # Record the cosmetic/condition grade (A, B, C). This is stored for
        # reference and reporting only - it does not affect triage order.
        record = self._records.get(serial_number)

        if record is None:
            raise KeyError(f"No active record for serial {serial_number}")

        record.grade = grade

    def get_record(self, serial_number: str) -> Optional[InspectionRecord]:
        # Return the record if it exists.
        return self._records.get(serial_number)

    def close_unit(self, serial_number: str) -> Optional[InspectionRecord]:
        # Remove the record after inspection is complete.
        return self._records.pop(serial_number, None)

    def __len__(self) -> int:
        return len(self._records)


# FIFO queue for inspection stations
class StationQueue:
    def __init__(self, maxlen: Optional[int] = None) -> None:
        # Store units in arrival order. An optional maxlen caps memory use
        # to model a station's physical buffer; once full, enqueue drops
        # the oldest waiting unit rather than growing without bound.
        self._queue: Deque[str] = deque(maxlen=maxlen)
        self._maxlen = maxlen
        self._dropped = 0

    def enqueue(self, serial_number: str) -> None:
        # Add a unit to the end of the queue.
        if self._maxlen is not None and len(self._queue) == self._maxlen:
            self._dropped += 1
        self._queue.append(serial_number)

    def dequeue(self) -> Optional[str]:
        # Return None if the queue is empty.
        if not self._queue:
            return None

        # Remove the first unit.
        return self._queue.popleft()

    def peek(self) -> Optional[str]:
        # Look at the next unit without removing it.
        return self._queue[0] if self._queue else None

    @property
    def dropped_count(self) -> int:
        # Number of units silently overwritten because the buffer was full.
        return self._dropped

    def __len__(self) -> int:
        return len(self._queue)


# Priority queue using a heap
class TriageQueue:
    def __init__(self) -> None:
        # Heap stores units by priority.
        self._heap: list = []

        # Counter keeps order when priorities are equal.
        self._counter = itertools.count()

    def push(self, serial_number: str, priority: int) -> None:
        # Keep insertion order for equal priorities.
        count = next(self._counter)

        # Negative priority makes the highest priority come out first.
        heapq.heappush(self._heap, (-priority, count, serial_number))

    def load_many(self, entries: list) -> None:
        # Bulk-load a batch of (serial_number, priority) pairs in O(n)
        # instead of calling push() n times at O(log n) each (O(n log n)
        # total). Useful when a backlog of units arrives at once, e.g.
        # at the start of a shift, rather than one at a time.
        for serial_number, priority in entries:
            count = next(self._counter)
            self._heap.append((-priority, count, serial_number))
        heapq.heapify(self._heap)

    def pop_highest_priority(self) -> Optional[str]:
        # Return None if the heap is empty.
        if not self._heap:
            return None

        # Remove the highest-priority unit.
        _, _, serial_number = heapq.heappop(self._heap)
        return serial_number

    def __len__(self) -> int:
        return len(self._heap)


# Node used in the trie
class TrieNode:
    def __init__(self) -> None:
        # Store child characters.
        self.children: Dict[str, "TrieNode"] = {}

        # Mark whether this node ends a valid SKU.
        self.is_terminal: bool = False


# Trie for SKU validation
class SKUTrie:
    def __init__(self) -> None:
        # Start with an empty root node.
        self._root = TrieNode()
        # Cache of recent exact-match results. The same SKU is often
        # scanned many times in a shift (e.g. a common model), so caching
        # avoids re-walking the trie for a code that was just checked.
        # Cleared whenever the catalog changes so it can never go stale.
        self._contains_cache: Dict[str, bool] = {}

    def insert(self, sku: str) -> None:
        # Start from the root.
        node = self._root

        # Create nodes if they do not exist.
        for char in sku:
            node = node.children.setdefault(char, TrieNode())

        # Mark the end of a valid SKU.
        node.is_terminal = True

        # Invalidate the cache: this SKU (and possibly others that were
        # previously reported as not-contained) may now resolve differently.
        self._contains_cache.clear()

    def has_prefix(self, prefix: str) -> bool:
        # Start from the root.
        node = self._root

        # Follow each character in the prefix.
        for char in prefix:
            node = node.children.get(char)

            # Prefix not found.
            if node is None:
                return False

        return True

    def contains(self, sku: str) -> bool:
        # Serve repeated lookups for the same code from cache.
        cached = self._contains_cache.get(sku)
        if cached is not None:
            return cached

        # Start from the root.
        node = self._root

        # Follow each character in the SKU.
        for char in sku:
            node = node.children.get(char)

            # SKU does not exist.
            if node is None:
                self._contains_cache[sku] = False
                return False

        # True only if this is a complete SKU.
        result = node.is_terminal
        self._contains_cache[sku] = result
        return result


# Test the program
if __name__ == "__main__":
    # Test hash table.
    registry = InspectionRegistry()
    registry.start_unit("SN123", "functional_test")
    registry.update_stage("SN123", "data_wipe", True)
    registry.update_stage("SN123", "functional_test", False)
    registry.set_grade("SN123", "B")

    assert registry.get_record("SN123").stage_results == {
        "data_wipe": True,
        "functional_test": False,
    }
    assert registry.get_record("SN123").grade == "B"

    registry.close_unit("SN123")
    assert len(registry) == 0

    # Test queue.
    q = StationQueue()
    q.enqueue("SN1")
    q.enqueue("SN2")

    assert q.peek() == "SN1"
    assert q.dequeue() == "SN1"
    assert q.dequeue() == "SN2"
    assert q.dequeue() is None

    # Test priority queue. Priority here represents shipment urgency
    # (1 = needed for an active shipment, 0 = not needed), not grade.
    triage = TriageQueue()
    triage.push("SN1", 0)
    triage.push("SN2", 1)
    triage.push("SN3", 1)
    triage.push("SN4", 0)

    order = [triage.pop_highest_priority() for _ in range(4)]
    assert order == ["SN2", "SN3", "SN1", "SN4"]

    # Test trie.
    trie = SKUTrie()

    for sku in ["AB100", "AB101", "AC200"]:
        trie.insert(sku)

    assert trie.has_prefix("AB") is True
    assert trie.has_prefix("AZ") is False
    assert trie.contains("AB100") is True
    assert trie.contains("AB1") is False
    # Cache should still report correctly after a repeat lookup, and
    # invalidate correctly if a new SKU is inserted afterward.
    assert trie.contains("AB100") is True  # served from cache the 2nd time
    trie.insert("AB1")
    assert trie.contains("AB1") is True  # cache correctly invalidated

    # Test bounded queue (maxlen) - oldest unit should be dropped once full.
    bounded = StationQueue(maxlen=2)
    bounded.enqueue("SNA")
    bounded.enqueue("SNB")
    bounded.enqueue("SNC")  # SNA should be dropped
    assert len(bounded) == 2
    assert bounded.dequeue() == "SNB"
    assert bounded.dropped_count == 1

    # Test bulk load via heapify - should produce the same priority order
    # as pushing one at a time.
    bulk = TriageQueue()
    bulk.load_many([("SN1", 0), ("SN2", 1), ("SN3", 1), ("SN4", 0)])
    bulk_order = [bulk.pop_highest_priority() for _ in range(4)]
    assert bulk_order == order

    # Confirm slots actually removed the per-instance __dict__.
    assert not hasattr(InspectionRecord("SNX", "intake"), "__dict__")

    print("All tests passed.")