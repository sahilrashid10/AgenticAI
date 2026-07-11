from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

from langchain_groq import ChatGroq

from config.settings import (
    GROQ_API_KEY,
    MODEL_NAME
)

from config.prompts import (
    CUSTOMER_ONBOARDING_PROMPT,
    TASK_PROMPT,
    WELCOME_EMAIL_PROMPT
)

from tools.customer_tools import (
    validate_customer,
    customer_exists,
    save_customer
)

from models.customer import Customer
load_dotenv()


llm = ChatGroq(
    model=MODEL_NAME,
    api_key=GROQ_API_KEY,
    temperature=0
)
# no registration of the tools is needed, as the @tool decorator handles that automatically unlike in the semantic kernel version of the code. 
# The tools are automatically registered with the agent when they are imported.
tools = [
    validate_customer,
    customer_exists,
    save_customer
]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=CUSTOMER_ONBOARDING_PROMPT
)


def format_prompt(prompt_template: str, customer: Customer) -> str:
    return prompt_template.format(
        name=customer.name,
        company=customer.company
    )


def invoke_text_prompt(prompt_template: str, customer: Customer) -> str:
    response = llm.invoke([
        HumanMessage(content=format_prompt(prompt_template, customer))
    ])

    return response.content if hasattr(response, "content") else str(response)


def normalize_onboarding_response(response_text: str) -> str:
    response_lower = response_text.lower()

    if "customer already registered" in response_lower:
        return "Customer already registered."

    if "successfully saved" in response_lower or "saved successfully" in response_lower:
        return "Customer has been successfully saved."

    for line in response_text.splitlines():
        line = line.strip()
        if line.startswith("Invalid:"):
            return line

    return response_text.strip()


def onboarding_succeeded(response_text: str) -> bool:
    response_lower = response_text.lower()

    return "successfully saved" in response_lower or "saved successfully" in response_lower

customer = Customer(
    name=input("Customer Name: "),
    email=input("Customer Email: "),
    company=input("Company Name: ")
)


response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content":
f"""
Register this customer.

Name: {customer.name}
Email: {customer.email}
Company: {customer.company}
"""
            }
        ]
    }
)

onboarding_result = response["messages"][-1].content
onboarding_result = normalize_onboarding_response(onboarding_result)

print("\n========== Onboarding Result =========\n")
print(onboarding_result)

if onboarding_succeeded(onboarding_result):
    welcome_email = invoke_text_prompt(WELCOME_EMAIL_PROMPT, customer)
    task_list = invoke_text_prompt(TASK_PROMPT, customer)

    print("\n========== Welcome Email =========\n")
    print(welcome_email)

    print("\n========== Task Checklist =========\n")
    print(task_list)