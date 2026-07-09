from utils.logger import log
from semantic_kernel.functions import kernel_function
class CustomerPlugin:

# decorator function: only these functions will be exposed to the kernel when registering the plugin
    @kernel_function(
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
    
    @kernel_function(
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
    
    @kernel_function(
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
    