"""
elementary_data_structures.py

Implements several basic data structures in Python:
- Dynamic array and matrix
- Array stack and queue
- Singly linked list
- Linked-list stack and queue
- Rooted tree
"""

from __future__ import annotations

from typing import Any, List, Optional


# Dynamic Array
class DynamicArray:
    """Simple resizable array."""

    def __init__(self):
        self._capacity = 1
        self._size = 0
        self._data: List[Any] = [None] * self._capacity

    def __len__(self):
        return self._size

    # Increase the array capacity.
    def _resize(self, new_capacity: int):
        new_data = [None] * new_capacity

        for index in range(self._size):
            new_data[index] = self._data[index]

        self._data = new_data
        self._capacity = new_capacity

    # Return the value at an index.
    def access(self, index: int):
        if not 0 <= index < self._size:
            raise IndexError("Array index out of bounds")

        return self._data[index]

    # Add a value to the end.
    def insert_end(self, value: Any):
        if self._size == self._capacity:
            self._resize(self._capacity * 2)

        self._data[self._size] = value
        self._size += 1

    # Add a value at a specific index.
    def insert_at(self, index: int, value: Any):
        if not 0 <= index <= self._size:
            raise IndexError("Insert index out of bounds")

        if self._size == self._capacity:
            self._resize(self._capacity * 2)

        # Shift values to the right.
        for position in range(self._size, index, -1):
            self._data[position] = self._data[position - 1]

        self._data[index] = value
        self._size += 1

    # Remove a value at a specific index.
    def delete_at(self, index: int):
        if not 0 <= index < self._size:
            raise IndexError("Delete index out of bounds")

        removed_value = self._data[index]

        # Shift values to the left.
        for position in range(index, self._size - 1):
            self._data[position] = self._data[position + 1]

        self._data[self._size - 1] = None
        self._size -= 1

        return removed_value

    # Remove the last value.
    def delete_end(self):
        return self.delete_at(self._size - 1)

    # Convert the dynamic array to a list.
    def to_list(self) -> List[Any]:
        return [
            self._data[index]
            for index in range(self._size)
        ]

    def __repr__(self):
        return f"DynamicArray({self.to_list()})"


# Matrix
class Matrix:
    """Simple matrix built with DynamicArray rows."""

    def __init__(
        self,
        rows: int,
        cols: int,
        fill=0,
    ):
        self.rows = rows
        self.cols = cols
        self._data: List[DynamicArray] = []

        for _ in range(rows):
            row = DynamicArray()

            for _ in range(cols):
                row.insert_end(fill)

            self._data.append(row)

    # Return a value from the matrix.
    def get(self, row: int, column: int):
        return self._data[row].access(column)

    # Update a value in the matrix.
    def set(
        self,
        row: int,
        column: int,
        value: Any,
    ):
        self._data[row]._data[column] = value

    # Add a new row.
    def add_row(self, fill=0):
        row = DynamicArray()

        for _ in range(self.cols):
            row.insert_end(fill)

        self._data.append(row)
        self.rows += 1

    # Add a new column.
    def add_column(self, fill=0):
        for row in self._data:
            row.insert_end(fill)

        self.cols += 1

    # Convert the matrix to a list.
    def to_list(self) -> List[List[Any]]:
        return [
            row.to_list()
            for row in self._data
        ]

    def __repr__(self):
        return "\n".join(
            str(row.to_list())
            for row in self._data
        )


# Array Stack
class ArrayStack:
    """Stack built with a DynamicArray."""

    def __init__(self):
        self._array = DynamicArray()

    # Add a value to the top.
    def push(self, value: Any):
        self._array.insert_end(value)

    # Remove the top value.
    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")

        return self._array.delete_end()

    # Return the top value.
    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty stack")

        return self._array.access(
            len(self._array) - 1
        )

    def is_empty(self) -> bool:
        return len(self._array) == 0

    def __len__(self):
        return len(self._array)


# Array Queue
class ArrayQueue:
    """Queue built with a circular array."""

    def __init__(self):
        self._capacity = 4
        self._data: List[Any] = [None] * self._capacity
        self._front = 0
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    # Increase the queue capacity.
    def _resize(self, new_capacity: int):
        new_data = [None] * new_capacity

        for index in range(self._size):
            old_index = (
                self._front + index
            ) % self._capacity

            new_data[index] = self._data[old_index]

        self._data = new_data
        self._capacity = new_capacity
        self._front = 0

    # Add a value to the back.
    def enqueue(self, value: Any):
        if self._size == self._capacity:
            self._resize(self._capacity * 2)

        back = (
            self._front + self._size
        ) % self._capacity

        self._data[back] = value
        self._size += 1

    # Remove the value at the front.
    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")

        value = self._data[self._front]
        self._data[self._front] = None

        self._front = (
            self._front + 1
        ) % self._capacity

        self._size -= 1

        return value

    # Return the value at the front.
    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty queue")

        return self._data[self._front]


# Linked List Node
class _Node:
    __slots__ = ("value", "next")

    def __init__(
        self,
        value: Any,
        next_node: Optional["_Node"] = None,
    ):
        self.value = value
        self.next = next_node


# Singly Linked List
class SinglyLinkedList:
    """Singly linked list with head and tail nodes."""

    def __init__(self):
        self._head: Optional[_Node] = None
        self._tail: Optional[_Node] = None
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    # Add a value to the front.
    def insert_front(self, value: Any):
        node = _Node(
            value,
            self._head
        )

        self._head = node

        if self._tail is None:
            self._tail = node

        self._size += 1

    # Add a value to the back.
    def insert_back(self, value: Any):
        node = _Node(value)

        if self._tail is None:
            self._head = node
            self._tail = node

        else:
            self._tail.next = node
            self._tail = node

        self._size += 1

    # Add a value at a specific index.
    def insert_at(
        self,
        index: int,
        value: Any,
    ):
        if not 0 <= index <= self._size:
            raise IndexError("Insert index out of bounds")

        if index == 0:
            self.insert_front(value)
            return

        if index == self._size:
            self.insert_back(value)
            return

        previous = self._head

        for _ in range(index - 1):
            previous = previous.next

        node = _Node(
            value,
            previous.next
        )

        previous.next = node
        self._size += 1

    # Remove the first value.
    def delete_front(self):
        if self.is_empty():
            raise IndexError("delete from empty list")

        value = self._head.value
        self._head = self._head.next

        if self._head is None:
            self._tail = None

        self._size -= 1

        return value

    # Remove a value at a specific index.
    def delete_at(self, index: int):
        if not 0 <= index < self._size:
            raise IndexError("Delete index out of bounds")

        if index == 0:
            return self.delete_front()

        previous = self._head

        for _ in range(index - 1):
            previous = previous.next

        target = previous.next
        previous.next = target.next

        if target is self._tail:
            self._tail = previous

        self._size -= 1

        return target.value

    # Find the first matching value.
    def search(self, value: Any) -> int:
        node = self._head
        index = 0

        while node is not None:
            if node.value == value:
                return index

            node = node.next
            index += 1

        return -1

    # Return all values as a list.
    def traverse(self) -> List[Any]:
        result = []
        node = self._head

        while node is not None:
            result.append(node.value)
            node = node.next

        return result

    def __repr__(self):
        return (
            f"SinglyLinkedList({self.traverse()})"
        )


# Linked List Stack
class LinkedListStack:
    """Stack built with a singly linked list."""

    def __init__(self):
        self._list = SinglyLinkedList()

    def push(self, value: Any):
        self._list.insert_front(value)

    def pop(self):
        return self._list.delete_front()

    def peek(self):
        if self._list.is_empty():
            raise IndexError("peek from empty stack")

        return self._list._head.value

    def is_empty(self) -> bool:
        return self._list.is_empty()

    def __len__(self):
        return len(self._list)


# Linked List Queue
class LinkedListQueue:
    """Queue built with a singly linked list."""

    def __init__(self):
        self._list = SinglyLinkedList()

    def enqueue(self, value: Any):
        self._list.insert_back(value)

    def dequeue(self):
        return self._list.delete_front()

    def peek(self):
        if self._list.is_empty():
            raise IndexError("peek from empty queue")

        return self._list._head.value

    def is_empty(self) -> bool:
        return self._list.is_empty()

    def __len__(self):
        return len(self._list)


# Tree Node
class TreeNode:
    __slots__ = (
        "value",
        "children",
        "parent",
    )

    def __init__(
        self,
        value: Any,
        parent: Optional["TreeNode"] = None,
    ):
        self.value = value
        self.children: List["TreeNode"] = []
        self.parent = parent


# Rooted Tree
class RootedTree:
    """General tree with linked nodes."""

    def __init__(self, root_value: Any):
        self.root = TreeNode(root_value)

    # Add a child to a parent node.
    def add_child(
        self,
        parent: TreeNode,
        value: Any,
    ) -> TreeNode:
        child = TreeNode(
            value,
            parent
        )

        parent.children.append(child)

        return child

    # Find the first matching node.
    def find(
        self,
        value: Any,
    ) -> Optional[TreeNode]:
        queue = [self.root]

        while queue:
            node = queue.pop(0)

            if node.value == value:
                return node

            queue.extend(node.children)

        return None

    # Find the depth of a node.
    def depth(self, node: TreeNode) -> int:
        depth = 0

        while node.parent is not None:
            node = node.parent
            depth += 1

        return depth

    # Traverse the tree using BFS.
    def bfs_traverse(self) -> List[Any]:
        result = []
        queue = [self.root]

        while queue:
            node = queue.pop(0)
            result.append(node.value)
            queue.extend(node.children)

        return result

    # Traverse the tree using DFS.
    def dfs_traverse(self) -> List[Any]:
        result = []

        def visit(node: TreeNode):
            result.append(node.value)

            for child in node.children:
                visit(child)

        visit(self.root)

        return result


# Test the program.
if __name__ == "__main__":

    # Test DynamicArray.
    array = DynamicArray()

    for value in [1, 2, 3]:
        array.insert_end(value)

    array.insert_at(1, 99)

    assert array.to_list() == [
        1,
        99,
        2,
        3,
    ]

    array.delete_at(1)

    assert array.to_list() == [
        1,
        2,
        3,
    ]

    print("DynamicArray tests passed.")

    # Test Matrix.
    matrix = Matrix(
        2,
        2,
        fill=0
    )

    matrix.set(
        0,
        0,
        5
    )

    matrix.add_row()
    matrix.add_column()

    assert matrix.get(0, 0) == 5
    assert matrix.rows == 3
    assert matrix.cols == 3

    print("Matrix tests passed.")

    # Test ArrayStack.
    array_stack = ArrayStack()

    for value in [1, 2, 3]:
        array_stack.push(value)

    assert array_stack.pop() == 3
    assert array_stack.pop() == 2

    print("ArrayStack tests passed.")

    # Test ArrayQueue.
    array_queue = ArrayQueue()

    for value in [1, 2, 3]:
        array_queue.enqueue(value)

    assert array_queue.dequeue() == 1
    assert array_queue.dequeue() == 2

    print("ArrayQueue tests passed.")

    # Test LinkedListStack.
    linked_stack = LinkedListStack()

    for value in [1, 2, 3]:
        linked_stack.push(value)

    assert linked_stack.pop() == 3
    assert linked_stack.pop() == 2

    print("LinkedListStack tests passed.")

    # Test LinkedListQueue.
    linked_queue = LinkedListQueue()

    for value in [1, 2, 3]:
        linked_queue.enqueue(value)

    assert linked_queue.dequeue() == 1
    assert linked_queue.dequeue() == 2

    print("LinkedListQueue tests passed.")

    # Test SinglyLinkedList.
    linked_list = SinglyLinkedList()

    linked_list.insert_back(1)
    linked_list.insert_back(2)
    linked_list.insert_front(0)
    linked_list.insert_at(2, 99)

    assert linked_list.traverse() == [
        0,
        1,
        99,
        2,
    ]

    assert linked_list.search(99) == 2

    linked_list.delete_at(2)

    assert linked_list.traverse() == [
        0,
        1,
        2,
    ]

    print("SinglyLinkedList tests passed.")

    # Test RootedTree.
    tree = RootedTree("root")

    node_a = tree.add_child(
        tree.root,
        "A"
    )

    node_b = tree.add_child(
        tree.root,
        "B"
    )

    tree.add_child(
        node_a,
        "A1"
    )

    tree.add_child(
        node_a,
        "A2"
    )

    tree.add_child(
        node_b,
        "B1"
    )

    assert tree.bfs_traverse() == [
        "root",
        "A",
        "B",
        "A1",
        "A2",
        "B1",
    ]

    assert tree.dfs_traverse() == [
        "root",
        "A",
        "A1",
        "A2",
        "B",
        "B1",
    ]

    assert tree.depth(
        tree.find("A1")
    ) == 2

    print("RootedTree tests passed.")

    print(
        "\nAll data structure tests passed."
    )