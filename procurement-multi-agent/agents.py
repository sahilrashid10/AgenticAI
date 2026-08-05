import os
import sys
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from mcp_tools import get_mcp_tools

from prompts import (
    INTAKE_PROMPT,
    POLICY_PROMPT,
    APPROVAL_PROMPT,
    RISK_PROMPT,
    JUDGE_PROMPT
)
from autogen_ext.tools.mcp import (
    McpWorkbench,
    StdioServerParams,
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

policy_workbench = McpWorkbench(
    StdioServerParams(
        command=sys.executable,
        args=[str(Path(__file__).with_name("mcp_server.py"))],
    )
)

# the system message is like a script to an movie actor for different roles.
intake_agent = AssistantAgent(
    name="IntakeAgent",
    model_client=model_client,
    system_message=INTAKE_PROMPT,
)
# only this policy agent uses mcp
async def create_policy_agent():

    tools = await get_mcp_tools()

    return AssistantAgent(
        name="PolicyAgent",
        model_client=model_client,
        system_message=POLICY_PROMPT,
        tools=tools,
        reflect_on_tool_use=True,
    )

approval_agent = AssistantAgent(
    name="ApprovalAgent",
    model_client=model_client,
    system_message=APPROVAL_PROMPT,
)

risk_agent = AssistantAgent(
    name="RiskAgent",
    model_client=model_client,
    system_message=RISK_PROMPT,
)

judge_agent = AssistantAgent(
    name="JudgeAgent",
    model_client=model_client,
    system_message=JUDGE_PROMPT,
)