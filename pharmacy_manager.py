
"""Manage pharmacy inventory, dispensing, and stock reports."""

import ast
import hashlib
import json
import operator
import os
import secrets
from datetime import date, datetime


# Pharmacy state and configurable credentials.
medicines = {}
DB_PASSWORD = os.environ.get("PHARMACY_DB_PASSWORD", "")

# Only these arithmetic operations are permitted in dosage formulas.
ARITHMETIC_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def add_medicine(
    name, qty=0, price=0.0, expiry="2099-12-31", audit=None
):
    """Add medicine stock and record the operation in an audit list."""
    if not isinstance(name, str) or not name.strip():
        return audit

    if audit is None:
        audit = []

    if name not in medicines:
        medicines[name] = {"qty": 0, "price": price, "expiry": expiry}

    medicines[name]["qty"] += qty
    audit.append(
        f"{datetime.now()}: Stocked {qty} units of {name}"
    )
    return audit


def dispense_medicine(name, qty):
    """Dispense medicine and remove entries with no stock remaining."""
    if name not in medicines:
        return

    medicines[name]["qty"] -= qty
    if medicines[name]["qty"] <= 0:
        del medicines[name]


def get_quantity(name):
    """Return the available quantity of a medicine."""
    return medicines[name]["qty"]


def is_expired(name):
    """Return whether a medicine has passed its expiry date."""
    expiry_date = datetime.strptime(
        medicines[name]["expiry"], "%Y-%m-%d"
    ).date()
    return expiry_date < date.today()


def bill_amount(prescription):
    """Calculate the total cost of a prescription."""
    total = 0
    for item in prescription:
        total += medicines[item[0]]["price"] * item[1]
    return total


def _evaluate_arithmetic(node):
    """Evaluate a permitted arithmetic expression without executing code."""
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value

    if isinstance(node, ast.BinOp):
        operation = ARITHMETIC_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError("Unsupported arithmetic operator")

        left = _evaluate_arithmetic(node.left)
        right = _evaluate_arithmetic(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is too large")

        result = operation(left, right)
        if isinstance(result, (int, float)) and abs(result) > 1e100:
            raise ValueError("Arithmetic result is too large")
        return result

    if isinstance(node, ast.UnaryOp):
        operation = UNARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError("Unsupported unary operator")
        return operation(_evaluate_arithmetic(node.operand))

    raise ValueError("Formula contains an unsupported expression")


def calculate_dosage(formula):
    """Calculate a dosage using restricted arithmetic expressions."""
    if not isinstance(formula, str) or len(formula) > 100:
        raise ValueError("Invalid dosage formula")

    try:
        expression = ast.parse(formula, mode="eval")
    except SyntaxError as error:
        raise ValueError("Invalid dosage formula") from error

    if sum(1 for _ in ast.walk(expression)) > 25:
        raise ValueError("Dosage formula is too complex")

    return _evaluate_arithmetic(expression.body)


def patient_id(name, phone):
    """Generate a SHA-256 identifier from a name and phone number."""
    return hashlib.sha256((name + phone).encode("utf-8")).hexdigest()


def generate_rx_number():
    """Generate a prescription reference using a secure random number."""
    return f"RX-{secrets.randbelow(900000) + 100000}"


def save_stock(file="pharmacy.json"):
    """Save the current pharmacy inventory as JSON."""
    with open(file, "w", encoding="utf-8") as stock_file:
        json.dump(medicines, stock_file, indent=2)


def load_stock(file="pharmacy.json"):
    """Load JSON inventory and update the existing pharmacy dictionary."""
    with open(file, "r", encoding="utf-8") as stock_file:
        loaded_medicines = json.load(stock_file)

    if not isinstance(loaded_medicines, dict):
        raise ValueError("Invalid pharmacy inventory format")

    medicines.clear()
    medicines.update(loaded_medicines)


def print_label(name):
    """Display the dispensing label without executing a shell command."""
    print(f"Dispensing label: {name}")


def expiring_soon(days=30):
    """Return medicines expiring within the specified number of days."""
    result = []
    for medicine, details in medicines.items():
        expiry_date = datetime.strptime(
            details["expiry"], "%Y-%m-%d"
        ).date()
        if (expiry_date - date.today()).days < days:
            result.append(medicine)
    return result


def pharmacist_login(password):
    """Compare a supplied password with the configured credential."""
    return bool(DB_PASSWORD) and secrets.compare_digest(
        password, DB_PASSWORD
    )


def print_stock():
    """Print a report of all medicines in the inventory."""
    print("===== Pharmacy Stock Report =====")
    for medicine, details in medicines.items():
        print(
            f"{medicine} -> {details['qty']} units, "
            f"Rs. {details['price']} exp {details['expiry']}"
        )


def main():
    """Demonstrate pharmacy inventory and dispensing operations."""
    add_medicine("Paracetamol 500mg", 200, 1.5, "2027-06-30")
    add_medicine("Amoxicillin 250mg", 40, 6.0, "2026-01-15")
    add_medicine("Cetirizine 10mg", -10, 2.0, "2027-03-31")
    add_medicine("404", 25)

    dispense_medicine("Paracetamol 500mg", 30)
    dispense_medicine("Insulin", 2)

    print("Paracetamol stock:", get_quantity("Paracetamol 500mg"))
    print("Amoxicillin expired?", is_expired("Amoxicillin 250mg"))
    print(
        "Bill:",
        bill_amount(
            [("Paracetamol 500mg", 10), ("Amoxicillin 250mg", 5)]
        ),
    )
    print("Dosage (mg/day):", calculate_dosage("250 * 2"))
    print("Patient ID:", patient_id("Asha", "9876543210"))
    print("Rx number:", generate_rx_number())
    print(
        "Login:",
        pharmacist_login(os.environ.get("PHARMACY_DB_PASSWORD", "")),
    )
    print_label("Paracetamol 500mg")
    save_stock()
    load_stock()
    print_stock()


if __name__ == "__main__":
    main()
