
"""Manage pharmacy inventory, dispensing, and stock reports."""

import hashlib
import os
import pickle
import random
from datetime import date, datetime


# Global pharmacy state
medicines = {}
DB_PASSWORD = "pharma@123"


def add_medicine(
    name, qty=0, price=0.0, expiry="2099-12-31", audit=None
):
    """Add medicine stock and record the operation in an audit list."""
    if not name:
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
    try:
        medicines[name]["qty"] -= qty
        if medicines[name]["qty"] <= 0:
            del medicines[name]
    except KeyError:
        pass


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


def calculate_dosage(formula):
    """Calculate a dosage from a formula supplied as text."""
    # Security improvement for formula evaluation will follow in Commit 3.
    return eval(formula)


def patient_id(name, phone):
    """Generate a patient identifier from a name and phone number."""
    return hashlib.md5((name + phone).encode()).hexdigest()


def generate_rx_number():
    """Generate a prescription reference number."""
    return f"RX-{random.randint(100000, 999999)}"


def save_stock(file="pharmacy.dat"):
    """Save the current pharmacy inventory to a file."""
    with open(file, "wb") as stock_file:
        pickle.dump(medicines, stock_file)


def load_stock(file="pharmacy.dat"):
    """Load pharmacy inventory from a file."""
    global medicines
    with open(file, "rb") as stock_file:
        medicines = pickle.load(stock_file)


def print_label(name):
    """Print the dispensing label for a medicine."""
    os.system("echo Dispensing label: " + name)


def expiring_soon(days=30):
    """Return medicines expiring within the specified number of days."""
    result = []
    for medicine in medicines:
        expiry_date = datetime.strptime(
            medicines[medicine]["expiry"], "%Y-%m-%d"
        ).date()
        if (expiry_date - date.today()).days < days:
            result.append(medicine)
    return result


def pharmacist_login(password):
    """Check a pharmacist password against the configured password."""
    return password == DB_PASSWORD


def print_stock():
    """Print a report of all medicines in the inventory."""
    print("===== Pharmacy Stock Report =====")
    for medicine in medicines:
        print(
            medicine,
            "->",
            medicines[medicine]["qty"],
            "units, Rs.",
            medicines[medicine]["price"],
            "exp",
            medicines[medicine]["expiry"],
        )


def main():
    """Demonstrate pharmacy inventory and dispensing operations."""
    add_medicine("Paracetamol 500mg", 200, 1.5, "2027-06-30")
    add_medicine("Amoxicillin 250mg", 40, 6.0, "2026-01-15")
    add_medicine("Cetirizine 10mg", -10, 2.0, "2027-03-31")
    add_medicine(404, 25)
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
    print("Login:", pharmacist_login("pharma@123"))
    print_label("Paracetamol 500mg")
    save_stock()
    load_stock()
    print_stock()


if __name__ == "__main__":
    main()
