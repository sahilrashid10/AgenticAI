from langchain_core.tools import tool

from utils.logger import log


@tool("validate_customer", description="Validate a customer record")
def validate_customer(
    name: str,
    email: str,
    company: str
) -> str:

    log("Validating customer")
    if "@" not in email:
        return "Invalid: Email address is not valid."

    return "Customer record is valid."


@tool("save_customer", description="Save a validated customer")
def save_customer(
    name: str,
    email: str,
    company: str
) -> str:

    from utils.database import save_customer as save_customer_record

    log("Saving customer")

    customer = {
        "name": name,
        "email": email,
        "company": company
    }

    return save_customer_record(customer)


@tool("customer_exists", description="Check if a customer already exists")
def customer_exists(
    email: str
) -> str:

    from utils.database import customer_exists as customer_exists_record

    if customer_exists_record(email):
        return "Customer already exists."

    return "Customer does not exist."