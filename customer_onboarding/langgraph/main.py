from graph.workflow import graph

from graph.state import CustomerState

from models.customer import Customer

from pydantic import ValidationError


while True:
    name = input("Customer Name: ").strip()
    email = input("Customer Email: ").strip()
    company = input("Company Name: ").strip()

    if not name:
        print("Customer name cannot be empty.")
        continue

    if not email:
        print("Customer email cannot be empty.")
        continue

    if not company:
        print("Company name cannot be empty.")
        continue

    try:
        customer = Customer(name=name, email=email, company=company)
        break
    except ValidationError:
        print("Customer email must be valid.")

state: CustomerState = {

    "customer": customer,

    "valid": False,

    "exists": False,

    "saved": False,

    "welcome_email": "",

    "task_list": "",

    "error": ""

}

result = graph.invoke(state)

if result["error"]:
    print(result["error"])
else:
    print(result["welcome_email"])

    print()

    print(result["task_list"])