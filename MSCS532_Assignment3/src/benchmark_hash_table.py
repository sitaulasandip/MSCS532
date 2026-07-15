"""
benchmark_hash_table.py

Tests how the load factor affects hash table performance.

It compares:
1. A dynamic hash table that resizes automatically.
2. A fixed-size hash table that does not resize.
"""

import csv
import random
import sys
import time
from pathlib import Path

# Add the src folder so hash_table.py can be imported.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from hash_table import HashTableChaining

# Keep random test values the same each time.
random.seed(7)


# Hash table that does not resize.
class FixedCapacityHashTable(HashTableChaining):

    def insert(self, key, value):
        # Find the bucket for the key.
        index = self._hash(key)
        chain = self._table[index]

        # Update the value if the key already exists.
        for i, (existing_key, _) in enumerate(chain):
            if existing_key == key:
                chain[i] = (key, value)
                return

        # Add a new key-value pair to the chain.
        chain.append((key, value))
        self._size += 1

        # Resizing is intentionally disabled.


# Measure the average search time.
def avg_search_time(table, keys, trials=20000):
    # Select random keys to search for.
    sample = [random.choice(keys) for _ in range(trials)]

    start = time.perf_counter()

    # Search for every selected key.
    for key in sample:
        table.search(key)

    total_time = time.perf_counter() - start

    # Return the average time for one search.
    return total_time / trials


# Compare dynamic and fixed hash tables.
def experiment_dynamic_vs_fixed():
    rows = []

    # Number of items used in each test.
    sizes = [100, 1000, 5000, 10000, 20000, 40000]

    # Fixed table uses only 128 buckets.
    fixed_capacity = 128

    for n in sizes:
        keys = list(range(n))

        # Create and fill the dynamic hash table.
        dynamic_table = HashTableChaining()

        for key in keys:
            dynamic_table.insert(key, key)

        # Get load factor and chain information.
        dynamic_stats = dynamic_table.chain_length_stats()

        # Measure dynamic table search time.
        dynamic_time = avg_search_time(dynamic_table, keys)

        # Create and fill the fixed-size hash table.
        fixed_table = FixedCapacityHashTable(
            initial_capacity=fixed_capacity
        )

        for key in keys:
            fixed_table.insert(key, key)

        # Get fixed table load factor and chain information.
        fixed_stats = fixed_table.chain_length_stats()

        # Measure fixed table search time.
        fixed_time = avg_search_time(fixed_table, keys)

        # Save the test results.
        rows.append({
            "n": n,
            "dynamic_load_factor": round(
                dynamic_stats["load_factor"], 4
            ),
            "dynamic_max_chain": dynamic_stats[
                "max_chain_length"
            ],
            "dynamic_avg_search_sec": dynamic_time,
            "fixed_load_factor": round(
                fixed_stats["load_factor"], 4
            ),
            "fixed_max_chain": fixed_stats[
                "max_chain_length"
            ],
            "fixed_avg_search_sec": fixed_time,
        })

        # Display the results in the terminal.
        print(
            f"n={n:6d}  "
            f"dynamic: alpha={dynamic_stats['load_factor']:.2f} "
            f"max chain={dynamic_stats['max_chain_length']:2d} "
            f"search={dynamic_time * 1e6:.3f} us   |   "
            f"fixed: alpha={fixed_stats['load_factor']:.2f} "
            f"max chain={fixed_stats['max_chain_length']:3d} "
            f"search={fixed_time * 1e6:.3f} us"
        )

    return rows


def main():
    print("=== Dynamic Hash Table vs Fixed Hash Table ===")

    # Run the experiment.
    rows = experiment_dynamic_vs_fixed()

    # Create the data folder if it does not exist.
    data_folder = (
        Path(__file__).resolve().parent.parent / "data"
    )
    data_folder.mkdir(exist_ok=True)

    # Set the CSV output file location.
    output_path = data_folder / "hash_table_benchmark.csv"

    # Write the results to the CSV file.
    with open(output_path, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys())
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResults written to: {output_path}")


# Run the benchmark when this file is executed directly.
if __name__ == "__main__":
    main()