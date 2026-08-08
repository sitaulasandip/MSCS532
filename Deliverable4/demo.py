# Demo of the inspection pipeline using the four data structures.

from inspection_system import (
    InspectionRegistry,
    StationQueue,
    TriageQueue,
    SKUTrie,
)


# Set up the SKUs needed for shipment.

needed_skus = SKUTrie()
for sku in ["AB1001", "AB1002", "AC2050"]:
    needed_skus.insert(sku)

registry = InspectionRegistry()
intake_queue = StationQueue()
triage = TriageQueue()


# Sample units arriving at intake.

incoming_units = [
    ("SN-0001", True, "AB1001"),   # Normal unit with needed SKU.
    ("SN-0002", False, "AC2050"),  # No memory and needed SKU.
    ("SN-0003", True, "ZZ9999"),   # SKU not needed.
    ("SN-0004", True, "AB10"),     # Possible partial SKU read.
]

for serial_number, _, _ in incoming_units:
    intake_queue.enqueue(serial_number)

unit_info = {
    serial_number: (has_memory, sku)
    for serial_number, has_memory, sku in incoming_units
}


def process_data_wipe(serial_number: str, has_memory: bool) -> bool:
    # Simulate the data wipe stage.
    if not has_memory:
        return True

    return True


def assign_grade(serial_number: str) -> str:
    # Assign a condition grade to the unit.
    grade_by_serial = {
        "SN-0001": "B",
        "SN-0002": "A",
        "SN-0003": "C",
        "SN-0004": "B",
    }

    return grade_by_serial.get(serial_number, "B")


def shipment_priority(sku: str, needed_skus: SKUTrie) -> int:
    # Give needed SKUs higher priority.
    return 1 if needed_skus.contains(sku) else 0


def process_functional_test(serial_number: str) -> bool:
    # Simulate the functional test.
    return serial_number != "SN-0003"


print("=== Stage 1: Data wipe + intake ===")

while len(intake_queue) > 0:
    serial_number = intake_queue.dequeue()
    has_memory, sku = unit_info[serial_number]

    registry.start_unit(serial_number, "intake")

    wipe_passed = process_data_wipe(
        serial_number,
        has_memory,
    )

    registry.update_stage(
        serial_number,
        "data_wipe",
        wipe_passed,
    )

    grade = assign_grade(serial_number)
    registry.set_grade(serial_number, grade)

    priority = shipment_priority(
        sku,
        needed_skus,
    )

    triage.push(
        serial_number,
        priority,
    )

    print(
        f"{serial_number}: data_wipe={wipe_passed}, "
        f"memory_device={has_memory}, "
        f"grade={grade} (recorded only), "
        f"shipment_priority={priority}"
    )


print(
    "\n=== Stage 2: Triage "
    "(processed by shipment need, needed SKUs first) ==="
)

triaged_order = []

while len(triage) > 0:
    serial_number = triage.pop_highest_priority()
    triaged_order.append(serial_number)

print("Processing order:", triaged_order)


print("\n=== Stage 3: Functional test ===")

for serial_number in triaged_order:
    passed = process_functional_test(serial_number)

    registry.update_stage(
        serial_number,
        "functional_test",
        passed,
    )

    print(
        f"{serial_number}: functional_test={passed}"
    )


print(
    "\n=== Stage 4: Inventory vs. packout routing "
    "+ packout validation ==="
)

for serial_number in triaged_order:
    record = registry.get_record(serial_number)
    _, sku = unit_info[serial_number]

    sku_is_needed = needed_skus.contains(sku)
    sku_prefix_plausible = needed_skus.has_prefix(sku)
    all_stages_passed = all(record.stage_results.values())

    if not sku_is_needed:
        if sku_prefix_plausible:
            decision = (
                "HOLD - SKU prefix matches a needed code, "
                "possible OCR misread"
            )
        else:
            decision = (
                "INVENTORY - SKU not currently needed for shipment"
            )

    elif not all_stages_passed:
        decision = (
            "REJECTED - failed one or more required stages"
        )

    else:
        decision = (
            "PACKOUT - accessories check + all stages passed"
        )

    print(
        f"{serial_number}: sku={sku}, "
        f"grade={record.grade}, "
        f"stage_results={record.stage_results} "
        f"-> {decision}"
    )

    registry.close_unit(serial_number)


# Test a few edge cases.

print("\n=== Edge cases ===")

print(
    "Empty triage queue pop:",
    triage.pop_highest_priority(),
)

print(
    "Empty station queue dequeue:",
    intake_queue.dequeue(),
)

try:
    registry.update_stage(
        "SN-9999",
        "data_wipe",
        True,
    )
except KeyError as exc:
    print(
        "Update on unknown serial correctly raised:",
        exc,
    )

try:
    registry.set_grade(
        "SN-9999",
        "A",
    )
except KeyError as exc:
    print(
        "Grading an unknown serial correctly raised:",
        exc,
    )