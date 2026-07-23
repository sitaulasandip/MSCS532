"""
demo.py

Demonstrates how the data structures in inspection_system.py
work together in a small inspection pipeline.

The process includes:
1. Data wipe
2. Triage based on shipment need
3. Functional testing
4. Inventory or packout routing
5. Edge case testing
"""

from inspection_system import (
    InspectionRegistry,
    StationQueue,
    TriageQueue,
    SKUTrie,
)


# Add the SKUs needed for the current shipment.
needed_skus = SKUTrie()

for sku in ["AB1001", "AB1002", "AC2050"]:
    needed_skus.insert(sku)


# Create the data structures.
registry = InspectionRegistry()
intake_queue = StationQueue()
triage_queue = TriageQueue()


# Format: serial number, has memory, SKU
incoming_units = [
    ("SN-0001", True, "AB1001"),
    ("SN-0002", False, "AC2050"),
    ("SN-0003", True, "ZZ9999"),
    ("SN-0004", True, "AB10"),
]


# Add all units to the intake queue.
for serial_number, _, _ in incoming_units:
    intake_queue.enqueue(serial_number)


# Store unit information by serial number.
unit_info = {
    serial_number: (has_memory, sku)
    for serial_number, has_memory, sku in incoming_units
}


# Simulate the data wipe stage.
def process_data_wipe(
    serial_number: str,
    has_memory: bool,
) -> bool:
    # Units without memory do not need a wipe.
    if not has_memory:
        return True

    # Simulate a successful data wipe.
    return True


# Assign a cosmetic grade.
def assign_grade(serial_number: str) -> str:
    grade_by_serial = {
        "SN-0001": "B",
        "SN-0002": "A",
        "SN-0003": "C",
        "SN-0004": "B",
    }

    return grade_by_serial.get(
        serial_number,
        "B"
    )


# Set priority based on shipment need.
def shipment_priority(
    sku: str,
    needed_skus: SKUTrie,
) -> int:
    if needed_skus.contains(sku):
        return 1

    return 0


# Simulate the functional test.
def process_functional_test(
    serial_number: str,
) -> bool:
    # SN-0003 is used as the failed test case.
    return serial_number != "SN-0003"


print("=== Stage 1: Data wipe and intake ===")

# Process every unit in the intake queue.
while len(intake_queue) > 0:
    serial_number = intake_queue.dequeue()

    has_memory, sku = unit_info[serial_number]

    # Start the inspection record.
    registry.start_unit(
        serial_number,
        "intake"
    )

    # Run and save the data wipe result.
    wipe_passed = process_data_wipe(
        serial_number,
        has_memory
    )

    registry.update_stage(
        serial_number,
        "data_wipe",
        wipe_passed
    )

    # Save the cosmetic grade.
    grade = assign_grade(serial_number)

    registry.set_grade(
        serial_number,
        grade
    )

    # Add the unit to triage using shipment priority.
    priority = shipment_priority(
        sku,
        needed_skus
    )

    triage_queue.push(
        serial_number,
        priority
    )

    print(
        f"{serial_number}: "
        f"data_wipe={wipe_passed}, "
        f"memory_device={has_memory}, "
        f"grade={grade}, "
        f"shipment_priority={priority}"
    )


print(
    "\n=== Stage 2: Triage "
    "(needed SKUs processed first) ==="
)

triaged_order = []

# Remove units from the priority queue.
while len(triage_queue) > 0:
    serial_number = (
        triage_queue.pop_highest_priority()
    )

    triaged_order.append(serial_number)

print("Processing order:", triaged_order)


print("\n=== Stage 3: Functional test ===")

# Run the functional test on each unit.
for serial_number in triaged_order:
    passed = process_functional_test(
        serial_number
    )

    registry.update_stage(
        serial_number,
        "functional_test",
        passed
    )

    print(
        f"{serial_number}: "
        f"functional_test={passed}"
    )


print(
    "\n=== Stage 4: Inventory or packout routing "
    "and validation ==="
)

# Decide the final route for each unit.
for serial_number in triaged_order:
    record = registry.get_record(
        serial_number
    )

    _, sku = unit_info[serial_number]

    # Check the SKU against the shipment plan.
    sku_is_needed = needed_skus.contains(sku)
    sku_prefix_matches = needed_skus.has_prefix(sku)

    # Check whether all inspection stages passed.
    all_stages_passed = all(
        record.stage_results.values()
    )

    if not sku_is_needed:
        if sku_prefix_matches:
            decision = (
                "HOLD - SKU prefix matches a needed code, "
                "possible OCR misread"
            )
        else:
            decision = (
                "INVENTORY - SKU not currently needed "
                "for shipment"
            )

    elif not all_stages_passed:
        decision = (
            "REJECTED - failed one or more required stages"
        )

    else:
        decision = (
            "PACKOUT - accessories check and "
            "all stages passed"
        )

    print(
        f"{serial_number}: "
        f"sku={sku}, "
        f"grade={record.grade}, "
        f"stage_results={record.stage_results} "
        f"-> {decision}"
    )

    # Close the inspection record.
    registry.close_unit(serial_number)


print("\n=== Edge cases ===")

# Test empty queue behavior.
print(
    "Empty triage queue pop:",
    triage_queue.pop_highest_priority()
)

print(
    "Empty station queue dequeue:",
    intake_queue.dequeue()
)


# Test updating an unknown serial number.
try:
    registry.update_stage(
        "SN-9999",
        "data_wipe",
        True
    )

except KeyError as error:
    print(
        "Update on unknown serial correctly raised:",
        error
    )


# Test grading an unknown serial number.
try:
    registry.set_grade(
        "SN-9999",
        "A"
    )

except KeyError as error:
    print(
        "Grading an unknown serial correctly raised:",
        error
    )