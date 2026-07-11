from pathlib import Path
import json


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "customers.json"


def load_customers():
    if not DB_PATH.exists() or DB_PATH.stat().st_size == 0:
        return []

    with open(DB_PATH, "r") as file:
        return json.load(file)


def save_customers(customers):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(DB_PATH, "w") as file:
        json.dump(customers, file, indent=4)


def customer_exists(email):
    customers = load_customers()

    for customer in customers:
        if customer["email"].lower() == email.lower():
            return True

    return False


def save_customer(customer):
    customers = load_customers()
    customers.append(customer)
    save_customers(customers)

    return "Customer saved successfully."
