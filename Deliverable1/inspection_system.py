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
@dataclass
class InspectionRecord:
    serial_number: str
    station_id: str
    stage_results: Dict[str, bool] = field(default_factory=dict)


# Hash table for inspection records
class InspectionRegistry:
    def __init__(self) -> None:
        # Store records using serial number as the key.
        self._records: Dict[str, InspectionRecord] = {}

    def start_unit(self, serial_number: str, station_id: str) -> InspectionRecord:
        # Create a new inspection record.
        record = InspectionRecord(serial_number, station_id)
        self._records[serial_number] = record
        return record

    def update_stage(self, serial_number: str, stage_name: str, passed: bool) -> None:
        # Find the record.
        record = self._records.get(serial_number)

        # Stop if the serial number does not exist.
        if record is None:
            raise KeyError(f"No active record for serial {serial_number}")

        # Save the inspection result.
        record.stage_results[stage_name] = passed

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
    def __init__(self) -> None:
        # Store units in arrival order.
        self._queue: Deque[str] = deque()

    def enqueue(self, serial_number: str) -> None:
        # Add a unit to the end of the queue.
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

    def __len__(self) -> int:
        return len(self._queue)


# Priority queue using a heap
class TriageQueue:
    def __init__(self) -> None:
        # Heap stores units by priority.
        self._heap: list = []

        # Counter keeps order when priorities are equal.
        self._counter = itertools.count()

    def push(self, serial_number: str, grade: int) -> None:
        # Keep insertion order for equal priorities.
        count = next(self._counter)

        # Negative grade makes the highest grade come out first.
        heapq.heappush(self._heap, (-grade, count, serial_number))

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

    def insert(self, sku: str) -> None:
        # Start from the root.
        node = self._root

        # Create nodes if they do not exist.
        for char in sku:
            node = node.children.setdefault(char, TrieNode())

        # Mark the end of a valid SKU.
        node.is_terminal = True

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
        # Start from the root.
        node = self._root

        # Follow each character in the SKU.
        for char in sku:
            node = node.children.get(char)

            # SKU does not exist.
            if node is None:
                return False

        # True only if this is a complete SKU.
        return node.is_terminal


# Test the program
if __name__ == "__main__":
    # Test hash table.
    registry = InspectionRegistry()
    registry.start_unit("SN123", "functional_test")
    registry.update_stage("SN123", "data_wipe", True)
    registry.update_stage("SN123", "functional_test", False)

    assert registry.get_record("SN123").stage_results == {
        "data_wipe": True,
        "functional_test": False,
    }

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

    # Test priority queue.
    triage = TriageQueue()
    triage.push("SN1", 2)
    triage.push("SN2", 5)
    triage.push("SN3", 5)
    triage.push("SN4", 1)

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

    print("All tests passed.")