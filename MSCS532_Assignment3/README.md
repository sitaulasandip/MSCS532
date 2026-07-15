
## Requirements

Python 3.8 or newer. No external packages are required.

## How to run everything

From the repository root:

```
python3 src/quicksort.py
python3 src/hash_table.py
python3 src/benchmark_quicksort.py
python3 src/benchmark_hash_table.py
```

The first two commands run correctness tests and print a pass or fail
line for each case. The second two commands run the timing experiments
described in the report and write their raw results into the data
folder as CSV files.
