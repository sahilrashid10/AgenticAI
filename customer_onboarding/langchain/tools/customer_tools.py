from langchain_core.tools import tool
from utils.logger import log

@tool(
        description="Validate a customer record",
        name="validate_customer"
    )
def validate_customer(
        self,
        name: str,
        email: str,
        company: str
    ) -> str:

        log("Validating customer")
        if "@" not in email:
            return "Invalid: Email address is not valid."

        return "Customer record is valid."
    
@tool(
        description="Save a validated customer",
        name="save_customer"
    )
def save_customer(
        self,
        name: str,
        email: str,
        company: str
    ) -> str:

        from utils.database import save_customer
        log("Saving customer")

        customer = {
            "name": name,
            "email": email,
            "company": company
        }

        return save_customer(customer)
    
@tool(
        description="Check if a customer already exists",
        name="customer_exists"
    )
def customer_exists(
        self,
        email: str
    ) -> str:

        from utils.database import customer_exists

        if customer_exists(email):
            return "Customer already exists."

        return "Customer does not exist."