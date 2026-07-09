import os

from attrs import validate
from dotenv import load_dotenv

from langchain_groq import ChatGroq

from langchain.agents import (
    create_tool_calling_agent,
    AgentExecutor
)

from langchain_core.prompts import ChatPromptTemplate

from tools.customer_tools import (
    validate_customer,
    check_customer_exists,
    store_customer
)

from config.settings import (
    GROQ_API_KEY,
    MODEL_NAME
)

from config.prompts import SYSTEM_PROMPT

from models.customer import Customer


load_dotenv()


llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=MODEL_NAME,
    temperature=0
)

# no registration of the tools is needed, as the @tool decorator handles that automatically unlike in the semantic kernel version of the code. 
# The tools are automatically registered with the agent when they are imported.
tools = [
    validate_customer,
    check_customer_exists,
    store_customer
]


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ]
)

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)
# the agent knows how to think and this executor
# will handle the execution of the agent's actions, including calling the appropriate tools and managing the conversation flow.
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

# Why verbose=True?
# This is one of my favorite LangChain features.
# Instead of only seeing:
# Customer saved.
# You'll see something like:
# Entering AgentExecutor...
# Thought:...


customer = Customer(
    name="Sahil Rashid",
    email="sahil@gmail.com",
    company="MAQ Software"
)


user_input = f"""
Register this customer.

Name: {customer.name}
Email: {customer.email}
Company: {customer.company}
"""
# invoke returns a dictionary thats why we don't print just the output.
response = agent_executor.invoke(
    {
        "input": user_input
    }
)

print(response["output"])