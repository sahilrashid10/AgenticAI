import asyncio
import os

from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Load variables from .env
load_dotenv()


purchase_request = """
We need to purchase 20 Dell laptops for the new engineering team.
"""

from agents import (
    intake_agent,
    policy_agent,
    approval_agent,
    model_client
)
async def main():

    intake_result = await intake_agent.run(
        task=purchase_request
    )

    intake_output = intake_result.messages[-1].content

    print("========== Intake Agent ==========")
    print(intake_output)


    policy_result = await policy_agent.run(
        task=intake_output
    )

    policy_output = policy_result.messages[-1].content

    print("\n========== Policy Agent ==========")
    print(policy_output)


    approval_input = f"""
Purchase Request Analysis

{intake_output}

Policy Report

{policy_output}
"""

    approval_result = await approval_agent.run(
        task=approval_input
    )

    print("\n========== Approval Agent ==========")
    print(approval_result.messages[-1].content)

    await model_client.close()
    
if __name__ == "__main__":
    asyncio.run(main())