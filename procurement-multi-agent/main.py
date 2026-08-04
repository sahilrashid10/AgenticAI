import asyncio
import json

from dotenv import load_dotenv

from agents import (
    intake_agent,
    policy_agent,
    approval_agent,
    model_client
)

# Load environment variables from .env
load_dotenv()

# Sample purchase request
purchase_request = """
We need to purchase 20 Dell laptops for the new engineering team.
"""


async def main():

    # ==============================
    # Step 1: Intake Agent
    # ==============================
    intake_result = await intake_agent.run(
        task=purchase_request
    )

    # Get the JSON response from the Intake Agent
    intake_output = intake_result.messages[-1].content

    print("========== Intake Agent ==========")
    print(intake_output)

    # Convert JSON string into a Python dictionary
    purchase_data = json.loads(intake_output)

    print("\nPurchase Data (Python Dictionary)")
    print(type(purchase_data))
    print(purchase_data)

    # ==============================
    # Step 2: Policy Agent
    # ==============================

    # Convert dictionary back to JSON before sending it to another agent
    policy_result = await policy_agent.run(
        task=json.dumps(purchase_data, indent=4)
    )

    policy_output = policy_result.messages[-1].content

    print("\n========== Policy Agent ==========")
    print(policy_output)

    # Convert Policy JSON into Python dictionary
    policy_data = json.loads(policy_output)

    print("\nPolicy Data (Python Dictionary)")
    print(type(policy_data))
    print(policy_data)

    # ==============================
    # Step 3: Approval Agent
    # ==============================

    approval_input = f"""
Purchase JSON:
{json.dumps(purchase_data, indent=4)}

Policy JSON:
{json.dumps(policy_data, indent=4)}
"""

    approval_result = await approval_agent.run(
        task=approval_input
    )

    approval_output = approval_result.messages[-1].content

    print("\n========== Approval Agent ==========")
    print(approval_output)

    # Close the model client
    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())