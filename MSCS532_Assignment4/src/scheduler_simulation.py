"""

Simulates a single-processor task scheduler using a priority queue.

The scheduler:
1. Adds tasks when they arrive
2. Runs the highest-priority task first
3. Increases the priority of tasks that wait too long
4. Records scheduling events and performance statistics
"""

import random
from dataclasses import dataclass
from typing import List

from priority_queue import PriorityQueue, Task


# Store information about each scheduling event.
@dataclass
class ScheduleEvent:
    time: float
    task_id: int
    task_name: str
    event: str
    priority: float


# Run the task scheduling simulation.
def simulate_scheduler(
    tasks: List[Task],
    aging_threshold: float = 5.0,
    aging_boost: float = 1.0,
):
    # Create a max-heap priority queue.
    priority_queue = PriorityQueue(is_max=True)

    # Store tasks by ID for quick lookup.
    tasks_by_id = {
        task.task_id: task
        for task in tasks
    }

    # Sort tasks by arrival time.
    arrivals = sorted(
        tasks,
        key=lambda task: task.arrival_time
    )

    # Store all scheduling events.
    log: List[ScheduleEvent] = []

    clock = 0.0
    arrival_index = 0
    number_of_tasks = len(arrivals)

    # Track when each task entered the queue.
    waiting_since = {}

    # Track when each task finishes.
    completion_time = {}

    # Each task takes one time unit to complete.
    processing_time = {
        task.task_id: 1.0
        for task in tasks
    }

    # Continue until all tasks have arrived and finished.
    while (
        arrival_index < number_of_tasks
        or not priority_queue.is_empty()
    ):
        # Add every task that has arrived.
        while (
            arrival_index < number_of_tasks
            and arrivals[arrival_index].arrival_time <= clock
        ):
            task = arrivals[arrival_index]

            # Add the task to the priority queue.
            priority_queue.insert(task)

            # Record the arrival event.
            log.append(
                ScheduleEvent(
                    clock,
                    task.task_id,
                    task.name,
                    "arrived",
                    task.priority,
                )
            )

            # Start tracking how long the task waits.
            waiting_since[task.task_id] = clock

            arrival_index += 1

        # Move the clock forward if no tasks are ready.
        if priority_queue.is_empty():
            clock = arrivals[arrival_index].arrival_time
            continue

        # Increase priority for tasks waiting too long.
        for task_id, start_time in list(waiting_since.items()):
            task_is_waiting = task_id in priority_queue._index_of
            waited_too_long = (
                clock - start_time
            ) >= aging_threshold

            if task_is_waiting and waited_too_long:
                # Find the task's current priority.
                task_index = priority_queue._index_of[task_id]
                current_priority = (
                    priority_queue
                    ._heap[task_index]
                    .priority
                )

                # Increase the task's priority.
                new_priority = current_priority + aging_boost

                priority_queue.increase_key(
                    task_id,
                    new_priority
                )

                # Restart the aging timer.
                waiting_since[task_id] = clock

                # Record the priority change.
                log.append(
                    ScheduleEvent(
                        clock,
                        task_id,
                        tasks_by_id[task_id].name,
                        "priority_boosted",
                        new_priority,
                    )
                )

        # Remove the highest-priority task.
        running_task = priority_queue.extract_max()

        # The task is no longer waiting.
        waiting_since.pop(
            running_task.task_id,
            None
        )

        # Record when the task starts.
        log.append(
            ScheduleEvent(
                clock,
                running_task.task_id,
                running_task.name,
                "started",
                running_task.priority,
            )
        )

        # Run the task.
        clock += processing_time[running_task.task_id]

        # Save the completion time.
        completion_time[running_task.task_id] = clock

        # Record when the task finishes.
        log.append(
            ScheduleEvent(
                clock,
                running_task.task_id,
                running_task.name,
                "finished",
                running_task.priority,
            )
        )

    # Calculate turnaround time for each task.
    turnaround_times = {
        task_id: (
            completion_time[task_id]
            - tasks_by_id[task_id].arrival_time
        )
        for task_id in completion_time
    }

    # Calculate summary statistics.
    stats = {
        "num_tasks": number_of_tasks,
        "makespan": clock,
        "avg_turnaround_time": (
            sum(turnaround_times.values()) / number_of_tasks
            if number_of_tasks
            else 0.0
        ),
        "max_turnaround_time": (
            max(turnaround_times.values())
            if turnaround_times
            else 0.0
        ),
    }

    return log, stats


# Display the scheduling events and statistics.
def print_schedule(
    log,
    stats,
    max_events=40
):
    # Print the table heading.
    print(
        f"{'time':>6}  "
        f"{'event':<17} "
        f"{'task':<28} "
        f"priority"
    )

    print("-" * 65)

    # Print the selected number of events.
    for event in log[:max_events]:
        print(
            f"{event.time:6.1f}  "
            f"{event.event:<17} "
            f"{event.task_name:<28} "
            f"{event.priority}"
        )

    # Show how many events were hidden.
    if len(log) > max_events:
        print(
            f"... ({len(log) - max_events} more events)"
        )

    print()

    # Print the summary statistics.
    for key, value in stats.items():
        print(f"{key}: {value}")


# Test the scheduler.
if __name__ == "__main__":
    # Keep random values the same for each run.
    random.seed(11)

    # Create a small scheduling example.
    demo_tasks = [
        Task(
            priority=8,
            arrival_time=0.0,
            name="deploy hotfix"
        ),
        Task(
            priority=2,
            arrival_time=0.5,
            name="update documentation"
        ),
        Task(
            priority=6,
            arrival_time=1.0,
            name="investigate alert"
        ),
        Task(
            priority=9,
            arrival_time=1.2,
            name="handle outage"
        ),
        Task(
            priority=2,
            arrival_time=1.5,
            name="archive old logs"
        ),
        Task(
            priority=7,
            arrival_time=2.0,
            name="respond to customer"
        ),
        Task(
            priority=1,
            arrival_time=2.2,
            name="minor refactor"
        ),
        Task(
            priority=8,
            arrival_time=3.0,
            name="security patch"
        ),
        Task(
            priority=3,
            arrival_time=3.5,
            name="update dependencies"
        ),
        Task(
            priority=9,
            arrival_time=4.0,
            name="database failover"
        ),
    ]

    print(
        "=== Scheduling simulation "
        "(Max Heap with aging) ===\n"
    )

    # Run the small scheduling example.
    log, stats = simulate_scheduler(
        demo_tasks,
        aging_threshold=3.0,
        aging_boost=2.0
    )

    print_schedule(log, stats)

    print(
        "\n=== Larger randomized scenario ===\n"
    )

    # Create 500 random tasks.
    big_tasks = [
        Task(
            priority=random.randint(1, 10),
            arrival_time=round(
                random.uniform(0, 200),
                1
            ),
            name=f"task_{index}",
        )
        for index in range(500)
    ]

    # Run the large scheduling example.
    _, big_stats = simulate_scheduler(
        big_tasks,
        aging_threshold=5.0,
        aging_boost=1.0
    )

    # Display statistics for the large test.
    for key, value in big_stats.items():
        print(f"{key}: {value}")