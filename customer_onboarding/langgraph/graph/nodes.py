from graph.state import CustomerState

from utils.database import (
    customer_exists,
    save_customer
)

from config.prompts import (
    WELCOME_EMAIL_PROMPT,
    TASK_PROMPT
)

from langchain_groq import ChatGroq

from config.settings import (
    GROQ_API_KEY,
    MODEL_NAME
)

# The LLM is no longer "the brain."
# It's just another object that one node can use.
# Huge mindset shift.
llm = ChatGroq(
    model=MODEL_NAME,
    api_key=GROQ_API_KEY,
    temperature=0
)


def validate_node(state: CustomerState):

    customer = state["customer"]

    if "@" not in customer.email:

        state["error"] = "Invalid email address."

        state["valid"] = False

    else:

        state["valid"] = True

    return state


def exists_node(state: CustomerState):

    customer = state["customer"]

    state["exists"] = customer_exists(customer.email)
    if state["exists"]:
        state["error"] = "Customer already exists."

    return state


def exists_error_node(state: CustomerState):

    return state


def save_node(state: CustomerState):

    customer = state["customer"]

    result = save_customer(
        {
            "name": customer.name,
            "email": customer.email,
            "company": customer.company
        }
    )

    state["saved"] = "successfully" in result.lower()

    return state


def email_node(state: CustomerState):

    customer = state["customer"]

    prompt = WELCOME_EMAIL_PROMPT.format(
        name=customer.name,
        company=customer.company
    )

    response = llm.invoke(prompt)

    state["welcome_email"] = response.content

    return state

def checklist_node(state: CustomerState):

    customer = state["customer"]

    prompt = TASK_PROMPT.format(
        name=customer.name,
        company=customer.company
    )

    response = llm.invoke(prompt)

    state["task_list"] = response.content

    return state


def validation_error_node(state: CustomerState):

    return state