from pydantic import BaseModel, Field

from crewai.tools.base_tool import BaseTool

from utils.logger import log


class ValidateCustomerArgs(BaseModel):
    name: str = Field(..., description="Customer name")
    email: str = Field(..., description="Customer email address")
    company: str = Field(..., description="Customer company name")


class SaveCustomerArgs(BaseModel):
    name: str = Field(..., description="Customer name")
    email: str = Field(..., description="Customer email address")
    company: str = Field(..., description="Customer company name")


class CustomerExistsArgs(BaseModel):
    email: str = Field(..., description="Customer email address")


class ValidateCustomerTool(BaseTool):
    name: str = "validate_customer"
    description: str = "Validate a customer record and explain exactly why it fails."
    args_schema: type[BaseModel] = ValidateCustomerArgs

    def _run(self, name: str, email: str, company: str) -> str:
        log("Validating customer")

        if not name.strip():
            return "Validation failed: customer name is missing."

        if not email.strip():
            return "Validation failed: customer email is missing."

        if "@" not in email:
            return "Validation failed: customer email format is invalid."

        if not company.strip():
            return "Validation failed: company name is missing."

        return "Validation passed: customer record is valid."


class SaveCustomerTool(BaseTool):
    name: str = "save_customer"
    description: str = "Save a validated customer."
    args_schema: type[BaseModel] = SaveCustomerArgs

    def _run(self, name: str, email: str, company: str) -> str:
        from utils.database import save_customer as save_customer_record

        log("Saving customer")

        customer = {
            "name": name,
            "email": email,
            "company": company
        }

        return save_customer_record(customer)


class CustomerExistsTool(BaseTool):
    name: str = "customer_exists"
    description: str = "Check if a customer already exists."
    args_schema: type[BaseModel] = CustomerExistsArgs

    def _run(self, email: str) -> str:
        from utils.database import customer_exists as customer_exists_record

        if customer_exists_record(email):
            return "Customer already exists."

        return "Customer does not exist."


validate_customer = ValidateCustomerTool()
save_customer = SaveCustomerTool()
customer_exists = CustomerExistsTool()