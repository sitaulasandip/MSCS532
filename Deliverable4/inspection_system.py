"""
inspection_system.py

Simple production-line inspection system.
"""

from __future__ import annotations

import heapq
import itertools
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional


# Inspection record.
@dataclass(slots=True)
class InspectionRecord:
    serial_number: str
    station_id: str
    stage_results: Dict[str, bool] = field(default_factory=dict)
    # Store the unit condition grade.
    grade: Optional[str] = None


# Store inspection records by serial number.
class InspectionRegistry:
    def __init__(self) -> None:
        # Store records by serial number.
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
        # Find the inspection record.
        record = self._records.get(serial_number)

        # Check if the record exists.
        if record is None:
            raise KeyError(
                f"No active record for serial {serial_number}"
            )

        # Save the stage result.
        record.stage_results[stage_name] = passed

    def set_grade(
        self,
        serial_number: str,
        grade: str,
    ) -> None:
        # Save the unit grade.
        record = self._records.get(serial_number)

        if record is None:
            raise KeyError(
                f"No active record for serial {serial_number}"
            )

        record.grade = grade

    def get_record(
        self,
        serial_number: str,
    ) -> Optional[InspectionRecord]:
        # Return the inspection record.
        return self._records.get(serial_number)

    def close_unit(
        self,
        serial_number: str,
    ) -> Optional[InspectionRecord]:
        # Remove the completed record.
        return self._records.pop(serial_number, None)

    def __len__(self) -> int:
        return len(self._records)


# FIFO queue for inspection stations.
class StationQueue:
    def __init__(
        self,
        maxlen: Optional[int] = None,
    ) -> None:
        # Create the station queue.
        self._queue: Deque[str] = deque(maxlen=maxlen)
        self._maxlen = maxlen
        self._dropped = 0

    def enqueue(self, serial_number: str) -> None:
        # Add a unit to the queue.
        if (
            self._maxlen is not None
            and len(self._queue) == self._maxlen
        ):
            self._dropped += 1

        self._queue.append(serial_number)

    def dequeue(self) -> Optional[str]:
        # Check if the queue is empty.
        if not self._queue:
            return None

        # Remove the first unit.
        return self._queue.popleft()

    def peek(self) -> Optional[str]:
        # View the next unit.
        return self._queue[0] if self._queue else None

    @property
    def dropped_count(self) -> int:
        # Return the number of dropped units.
        return self._dropped

    def __len__(self) -> int:
        return len(self._queue)


# Priority queue for triage.
class TriageQueue:
    def __init__(self) -> None:
        # Store units by priority.
        self._heap: list = []

        # Track insertion order.
        self._counter = itertools.count()

    def push(
        self,
        serial_number: str,
        priority: int,
    ) -> None:
        # Keep order for equal priorities.
        count = next(self._counter)

        # Add the unit by priority.
        heapq.heappush(
            self._heap,
            (-priority, count, serial_number),
        )

    def load_many(self, entries: list) -> None:
        # Load multiple units at once.
        for serial_number, priority in entries:
            count = next(self._counter)
            self._heap.append(
                (-priority, count, serial_number)
            )

        heapq.heapify(self._heap)

    def pop_highest_priority(self) -> Optional[str]:
        # Check if the queue is empty.
        if not self._heap:
            return None

        # Remove the highest-priority unit.
        _, _, serial_number = heapq.heappop(
            self._heap
        )

        return serial_number

    def __len__(self) -> int:
        return len(self._heap)


# Node for the SKU trie.
class TrieNode:
    def __init__(self) -> None:
        # Store child characters.
        self.children: Dict[str, "TrieNode"] = {}

        # Mark the end of a valid SKU.
        self.is_terminal: bool = False


# Trie for SKU validation.
class SKUTrie:
    def __init__(self) -> None:
        # Create the root node.
        self._root = TrieNode()

        # Store recent lookup results.
        self._contains_cache: Dict[str, bool] = {}

    def insert(self, sku: str) -> None:
        # Start at the root.
        node = self._root

        # Add each SKU character.
        for char in sku:
            node = node.children.setdefault(
                char,
                TrieNode(),
            )

        # Mark the complete SKU.
        node.is_terminal = True

        # Clear old cache results.
        self._contains_cache.clear()

    def has_prefix(self, prefix: str) -> bool:
        # Start at the root.
        node = self._root

        # Check each prefix character.
        for char in prefix:
            node = node.children.get(char)

            # Prefix does not exist.
            if node is None:
                return False

        return True

    def contains(self, sku: str) -> bool:
        # Check the cache first.
        cached = self._contains_cache.get(sku)

        if cached is not None:
            return cached

        # Start at the root.
        node = self._root

        # Check each SKU character.
        for char in sku:
            node = node.children.get(char)

            # SKU does not exist.
            if node is None:
                self._contains_cache[sku] = False
                return False

        # Check for a complete SKU.
        result = node.is_terminal
        self._contains_cache[sku] = result

        return result


# Run basic tests.
if __name__ == "__main__":

    # Test inspection registry.
    registry = InspectionRegistry()
    registry.start_unit(
        "SN123",
        "functional_test",
    )
    registry.update_stage(
        "SN123",
        "data_wipe",
        True,
    )
    registry.update_stage(
        "SN123",
        "functional_test",
        False,
    )
    registry.set_grade("SN123", "B")

    assert registry.get_record(
        "SN123"
    ).stage_results == {
        "data_wipe": True,
        "functional_test": False,
    }

    assert registry.get_record(
        "SN123"
    ).grade == "B"

    registry.close_unit("SN123")
    assert len(registry) == 0

    # Test station queue.
    q = StationQueue()
    q.enqueue("SN1")
    q.enqueue("SN2")

    assert q.peek() == "SN1"
    assert q.dequeue() == "SN1"
    assert q.dequeue() == "SN2"
    assert q.dequeue() is None

    # Test priority queue.
    triage = TriageQueue()
    triage.push("SN1", 0)
    triage.push("SN2", 1)
    triage.push("SN3", 1)
    triage.push("SN4", 0)

    order = [
        triage.pop_highest_priority()
        for _ in range(4)
    ]

    assert order == [
        "SN2",
        "SN3",
        "SN1",
        "SN4",
    ]

    # Test SKU trie.
    trie = SKUTrie()

    for sku in [
        "AB100",
        "AB101",
        "AC200",
    ]:
        trie.insert(sku)

    assert trie.has_prefix("AB") is True
    assert trie.has_prefix("AZ") is False
    assert trie.contains("AB100") is True
    assert trie.contains("AB1") is False

    # Test cached lookup.
    assert trie.contains("AB100") is True

    trie.insert("AB1")

    # Test cache reset.
    assert trie.contains("AB1") is True

    # Test bounded queue.
    bounded = StationQueue(maxlen=2)
    bounded.enqueue("SNA")
    bounded.enqueue("SNB")
    bounded.enqueue("SNC")

    assert len(bounded) == 2
    assert bounded.dequeue() == "SNB"
    assert bounded.dropped_count == 1

    # Test bulk loading.
    bulk = TriageQueue()

    bulk.load_many([
        ("SN1", 0),
        ("SN2", 1),
        ("SN3", 1),
        ("SN4", 0),
    ])

    bulk_order = [
        bulk.pop_highest_priority()
        for _ in range(4)
    ]

    assert bulk_order == order

    # Test slots.
    assert not hasattr(
        InspectionRecord("SNX", "intake"),
        "__dict__",
    )

    print("All tests passed.")