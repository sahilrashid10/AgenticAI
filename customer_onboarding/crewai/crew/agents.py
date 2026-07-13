from crewai import Agent
from crewai import LLM

from config.settings import (
    LLM_API_KEY,
    LLM_PROVIDER,
    MODEL_NAME
)

from tools.customer_tools import (
    validate_customer,
    customer_exists,
    save_customer
)

llm_config = {
    "model": MODEL_NAME,
    "provider": LLM_PROVIDER,
    "temperature": 0,
}
if LLM_API_KEY:
    llm_config["api_key"] = LLM_API_KEY

llm = LLM(**llm_config)


validation_agent = Agent(

    role="Customer Validation Specialist",

    goal="Validate customer information before onboarding and return the exact reason when it fails.",

    backstory=(
        "You are responsible for checking whether customer information "
        "is valid before registration and explaining which field is wrong."
    ),

    tools=[
        validate_customer
    ],

    llm=llm,
# get everything as in steps on terminal(Steps agent performs while computing anything.)
    verbose=True
)


database_agent = Agent(

    role="Database Administrator",

    goal="Check existing customers and register new customers.",

    backstory=(
        "You manage customer records and ensure duplicates are avoided."
    ),

    tools=[
        customer_exists,
        save_customer
    ],

    llm=llm,

    verbose=True
)



email_agent = Agent(

    role="Customer Communication Specialist",

    goal="Generate professional onboarding emails and task lists.",

    backstory=(
        "You create onboarding communication for new customers."
    ),

    llm=llm,

    verbose=True
)