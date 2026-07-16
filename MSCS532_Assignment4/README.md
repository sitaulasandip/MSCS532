

## Requirements

Python 3.8 or newer. No external packages are required.

## How to run everything

From the repository root:

```
python3 src/heapsort.py
python3 src/comparison_sorts.py
python3 src/priority_queue.py
python3 src/scheduler_simulation.py
python3 src/benchmark_sorts.py
```

The first three commands run correctness tests and print a pass or
fail line for each case, including a five thousand operation stress
test for the priority queue. The fourth command runs a readable ten
task scheduling demonstration followed by a larger five hundred task
randomized scenario. The fifth command runs the timing experiments
comparing Heapsort, Quicksort, and Merge Sort, and writes the raw
results into the data folder as a CSV file.

