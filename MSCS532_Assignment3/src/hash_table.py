
#Implements a hash table using chaining.

import random
from typing import Any, List, Optional, Tuple


# Large prime number used by the hash function.
_LARGE_PRIME = 2_305_843_009_213_693_951


class HashTableChaining:
    # Resize limits for the load factor.
    UPPER_LOAD_FACTOR = 1.0
    LOWER_LOAD_FACTOR = 0.25
    MIN_CAPACITY = 8

    def __init__(self, initial_capacity: int = MIN_CAPACITY):
        # Make sure the table is not smaller than the minimum size.
        self._capacity = max(initial_capacity, self.MIN_CAPACITY)

        # Create an empty list for each bucket.
        self._table: List[List[Tuple[Any, Any]]] = [
            [] for _ in range(self._capacity)
        ]

        # Track the number of stored keys.
        self._size = 0

        # Create random values for the hash function.
        self._reseed()

    # Create new hash function values.
    def _reseed(self) -> None:
        # Choose a random odd value for a.
        self._a = random.randrange(1, _LARGE_PRIME, 2)

        # Choose a random value for b.
        self._b = random.randrange(0, _LARGE_PRIME)

    # Find the bucket index for a key.
    def _hash(self, key: Any) -> int:
        # Convert the key into a non-negative integer.
        key_number = hash(key) & 0x7FFFFFFFFFFFFFFF

        # Use universal hashing to calculate the bucket.
        return (
            (self._a * key_number + self._b)
            % _LARGE_PRIME
        ) % self._capacity

    # Insert a new key or update an existing key.
    def insert(self, key: Any, value: Any) -> None:
        # Find the correct bucket.
        index = self._hash(key)
        chain = self._table[index]

        # Update the value if the key already exists.
        for i, (existing_key, _) in enumerate(chain):
            if existing_key == key:
                chain[i] = (key, value)
                return

        # Add the new key-value pair to the chain.
        chain.append((key, value))
        self._size += 1

        # Grow the table if the load factor becomes too high.
        if self._load_factor() > self.UPPER_LOAD_FACTOR:
            self._resize(self._capacity * 2)

    # Search for a value using its key.
    def search(self, key: Any) -> Optional[Any]:
        # Find the bucket where the key should be.
        index = self._hash(key)

        # Search through the chain.
        for existing_key, value in self._table[index]:
            if existing_key == key:
                return value

        # Return None when the key is not found.
        return None

    # Allow the use of: key in hash_table
    def __contains__(self, key: Any) -> bool:
        index = self._hash(key)

        # Return True if the key exists in the chain.
        return any(
            existing_key == key
            for existing_key, _ in self._table[index]
        )

    # Delete a key from the table.
    def delete(self, key: Any) -> bool:
        # Find the correct bucket.
        index = self._hash(key)
        chain = self._table[index]

        # Search for the key in the chain.
        for i, (existing_key, _) in enumerate(chain):
            if existing_key == key:
                # Remove the key-value pair.
                chain.pop(i)
                self._size -= 1

                # Shrink the table if the load factor becomes too low.
                if (
                    self._capacity > self.MIN_CAPACITY
                    and self._load_factor() < self.LOWER_LOAD_FACTOR
                ):
                    new_capacity = max(
                        self._capacity // 2,
                        self.MIN_CAPACITY
                    )
                    self._resize(new_capacity)

                return True

        # Return False if the key was not found.
        return False

    # Return the number of stored keys.
    def __len__(self) -> int:
        return self._size

    # Public method for getting the load factor.
    def load_factor(self) -> float:
        return self._load_factor()

    # Calculate the load factor.
    def _load_factor(self) -> float:
        return self._size / self._capacity

    # Resize the table and move all items.
    def _resize(self, new_capacity: int) -> None:
        # Save all existing key-value pairs.
        old_items = [
            pair
            for chain in self._table
            for pair in chain
        ]

        # Create a new table with the new capacity.
        self._capacity = new_capacity
        self._table = [
            [] for _ in range(self._capacity)
        ]

        # Create new random hash values.
        self._reseed()

        # Reinsert every item into its new bucket.
        for key, value in old_items:
            index = self._hash(key)
            self._table[index].append((key, value))

    # Return information about the chains.
    def chain_length_stats(self) -> dict:
        # Get the length of every chain.
        lengths = [
            len(chain)
            for chain in self._table
        ]

        number_of_slots = len(lengths)

        # Count the number of non-empty chains.
        nonempty_slots = sum(
            1 for length in lengths
            if length > 0
        )

        # Calculate the average length of non-empty chains.
        if nonempty_slots > 0:
            average_nonempty = sum(lengths) / nonempty_slots
        else:
            average_nonempty = 0.0

        return {
            "capacity": number_of_slots,
            "size": self._size,
            "load_factor": self._load_factor(),
            "max_chain_length": max(lengths) if lengths else 0,
            "avg_chain_length_nonempty": average_nonempty,
            "empty_slots": sum(
                1 for length in lengths
                if length == 0
            ),
        }


# Test the hash table.
if __name__ == "__main__":
    ht = HashTableChaining()

    # Test insert and search.
    ht.insert("apple", 1)
    ht.insert("banana", 2)
    ht.insert("cherry", 3)

    assert ht.search("apple") == 1
    assert ht.search("banana") == 2
    assert ht.search("missing") is None

    # Test updating an existing key.
    ht.insert("apple", 100)

    assert ht.search("apple") == 100
    assert len(ht) == 3

    # Test deleting a key.
    assert ht.delete("banana") is True
    assert ht.search("banana") is None
    assert ht.delete("banana") is False
    assert len(ht) == 2

    # Test automatic table growth.
    ht2 = HashTableChaining()
    number_of_items = 5000

    for i in range(number_of_items):
        ht2.insert(i, i * i)

    # Check that every item was inserted.
    assert len(ht2) == number_of_items

    # Check that every stored value is correct.
    for i in range(number_of_items):
        assert ht2.search(i) == i * i

    # Display statistics after inserting items.
    stats = ht2.chain_length_stats()

    print(
        "After inserting",
        number_of_items,
        "keys:",
        stats
    )

    # Make sure the load factor is within the limit.
    assert (
        stats["load_factor"]
        <= HashTableChaining.UPPER_LOAD_FACTOR + 1e-9
    )

    # Test automatic table shrinking.
    for i in range(number_of_items - 100):
        ht2.delete(i)

    # Display statistics after deleting items.
    stats_after_delete = ht2.chain_length_stats()

    print(
        "After deleting down to 100 keys:",
        stats_after_delete
    )

    # Confirm that 100 keys remain.
    assert len(ht2) == 100

    print("\nAll hash table tests passed.")