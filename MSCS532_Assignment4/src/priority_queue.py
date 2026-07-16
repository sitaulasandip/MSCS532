"""
Implements a priority queue using a binary heap.

Supports:
1. Insert a task
2. Remove the highest (or lowest) priority task
3. Update task priority
4. Max heap and Min heap modes
"""

import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# Task information
@dataclass
class Task:
    priority: float
    arrival_time: float = 0.0
    deadline: Optional[float] = None
    name: str = ""
    task_id: int = field(default_factory=lambda: next(_task_id_counter))

    def __repr__(self):
        return (
            f"Task(id={self.task_id}, "
            f"name={self.name!r}, "
            f"priority={self.priority}, "
            f"arrival={self.arrival_time}, "
            f"deadline={self.deadline})"
        )


# Automatically generate task IDs.
_task_id_counter = itertools.count(1)


# Priority Queue
class PriorityQueue:

    def __init__(self, is_max=True):
        # Store heap values.
        self._heap: List[Task] = []

        # Store task positions for quick lookup.
        self._index_of: Dict[int, int] = {}

        # True = Max Heap, False = Min Heap.
        self._is_max = is_max

    # Compare two tasks.
    def _higher_priority(self, task1: Task, task2: Task) -> bool:
        if self._is_max:
            return task1.priority > task2.priority

        return task1.priority < task2.priority

    # Check whether the queue is empty.
    def is_empty(self):
        return len(self._heap) == 0

    def __len__(self):
        return len(self._heap)

    # Return the top task without removing it.
    def peek(self):
        return self._heap[0] if self._heap else None

    # Swap two heap elements.
    def _swap(self, i, j):
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

        # Update their positions.
        self._index_of[self._heap[i].task_id] = i
        self._index_of[self._heap[j].task_id] = j

    # Move a task upward.
    def _sift_up(self, index):
        while index > 0:
            parent = (index - 1) // 2

            if self._higher_priority(
                self._heap[index],
                self._heap[parent]
            ):
                self._swap(index, parent)
                index = parent
            else:
                break

    # Move a task downward.
    def _sift_down(self, index):
        size = len(self._heap)

        while True:
            left = 2 * index + 1
            right = 2 * index + 2

            best = index

            # Compare with left child.
            if (
                left < size
                and self._higher_priority(
                    self._heap[left],
                    self._heap[best]
                )
            ):
                best = left

            # Compare with right child.
            if (
                right < size
                and self._higher_priority(
                    self._heap[right],
                    self._heap[best]
                )
            ):
                best = right

            # Stop if heap property is satisfied.
            if best == index:
                break

            self._swap(index, best)
            index = best

    # Insert a new task.
    def insert(self, task: Task):
        self._heap.append(task)

        index = len(self._heap) - 1
        self._index_of[task.task_id] = index

        # Restore heap order.
        self._sift_up(index)

    # Remove the highest (or lowest) priority task.
    def extract(self):

        if not self._heap:
            return None

        root = self._heap[0]
        last = self._heap.pop()

        del self._index_of[root.task_id]

        if self._heap:
            self._heap[0] = last
            self._index_of[last.task_id] = 0

            # Restore heap order.
            self._sift_down(0)

        return root

    def extract_max(self):
        if not self._is_max:
            raise ValueError(
                "This queue is a Min Heap."
            )

        return self.extract()

    def extract_min(self):
        if self._is_max:
            raise ValueError(
                "This queue is a Max Heap."
            )

        return self.extract()

    # Change a task's priority.
    def update_priority(
        self,
        task_id,
        new_priority,
    ):
        if task_id not in self._index_of:
            raise KeyError(
                f"No task with id {task_id}"
            )

        index = self._index_of[task_id]

        self._heap[index].priority = new_priority

        # Move the task if needed.
        self._sift_up(index)
        self._sift_down(
            self._index_of[task_id]
        )

    # Increase a task's priority.
    def increase_key(
        self,
        task_id,
        new_priority,
    ):
        index = self._index_of[task_id]

        if (
            self._is_max
            and new_priority < self._heap[index].priority
        ):
            raise ValueError(
                "Priority is smaller."
            )

        if (
            not self._is_max
            and new_priority > self._heap[index].priority
        ):
            raise ValueError(
                "Priority is larger."
            )

        self.update_priority(
            task_id,
            new_priority,
        )

    # Decrease a task's priority.
    def decrease_key(
        self,
        task_id,
        new_priority,
    ):
        index = self._index_of[task_id]

        if (
            self._is_max
            and new_priority > self._heap[index].priority
        ):
            raise ValueError(
                "Priority is larger."
            )

        if (
            not self._is_max
            and new_priority < self._heap[index].priority
        ):
            raise ValueError(
                "Priority is smaller."
            )

        self.update_priority(
            task_id,
            new_priority,
        )

    # Check whether the heap is valid.
    def is_valid_heap(self):
        size = len(self._heap)

        for i in range(size):

            left = 2 * i + 1
            right = 2 * i + 2

            if (
                left < size
                and self._higher_priority(
                    self._heap[left],
                    self._heap[i]
                )
            ):
                return False

            if (
                right < size
                and self._higher_priority(
                    self._heap[right],
                    self._heap[i]
                )
            ):
                return False

        return True


# Test the program.
if __name__ == "__main__":
    import random

    # Test Max Heap.
    pq = PriorityQueue()

    tasks = [
        Task(priority=3, name="Write Report"),
        Task(priority=9, name="Fix Bug"),
        Task(priority=1, name="Email"),
        Task(priority=5, name="Review"),
        Task(priority=9, name="Customer"),
    ]

    for task in tasks:
        pq.insert(task)
        assert pq.is_valid_heap()

    priorities = []

    while not pq.is_empty():
        priorities.append(
            pq.extract_max().priority
        )

    assert priorities == sorted(
        [t.priority for t in tasks],
        reverse=True
    )

    print("[PASS] Max Heap")

    # Test updating priorities.
    pq2 = PriorityQueue()

    ids = []

    for i in range(20):
        task = Task(
            priority=random.randint(0, 100)
        )

        ids.append(task.task_id)
        pq2.insert(task)

    for task_id in random.sample(ids, 10):
        pq2.update_priority(
            task_id,
            random.randint(0, 100)
        )

        assert pq2.is_valid_heap()

    print("[PASS] Update Priority")

    # Test empty queue.
    pq3 = PriorityQueue()

    assert pq3.is_empty()

    pq3.insert(Task(priority=1))

    assert not pq3.is_empty()

    pq3.extract_max()

    assert pq3.is_empty()

    print("[PASS] Empty Queue")

    # Test Min Heap.
    pq4 = PriorityQueue(is_max=False)

    for priority in [5, 1, 9, 3, 7]:
        pq4.insert(Task(priority=priority))

    values = []

    while not pq4.is_empty():
        values.append(
            pq4.extract_min().priority
        )

    assert values == sorted(
        [5, 1, 9, 3, 7]
    )

    print("[PASS] Min Heap")

    print("\nAll priority queue tests passed.")