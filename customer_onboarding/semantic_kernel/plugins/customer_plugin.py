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

        if not name.strip():
            return "Invalid: Customer name is required."

        if not company.strip():
            return "Invalid: Company name is required."

        if "@" not in email:
            return "Invalid: Email address is not valid."

        return "Customer record is valid."