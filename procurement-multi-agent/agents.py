import os

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

from prompts import (
    INTAKE_PROMPT,
    POLICY_PROMPT,
    APPROVAL_PROMPT
)

load_dotenv()

# shared model client just like employees work in one company, these 3 agents work in one company and share the same model client
model_client = OpenAIChatCompletionClient(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "structured_output": True,
        "family": "llama",
    },
)

# the system message is like a script to an movie actor for different roles.
intake_agent = AssistantAgent(
    name="IntakeAgent",
    model_client=model_client,
    system_message=INTAKE_PROMPT,
)

policy_agent = AssistantAgent(
    name="PolicyAgent",
    model_client=model_client,
    system_message=POLICY_PROMPT,
)

approval_agent = AssistantAgent(
    name="ApprovalAgent",
    model_client=model_client,
    system_message=APPROVAL_PROMPT,
)