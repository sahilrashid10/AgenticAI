import json

from agents import (
    intake_agent,
    policy_agent,
    approval_agent,
)


class ProcurementSupervisor:

    async def process_request(self, purchase_request):

        # ==============================
        # Intake Agent
        # ==============================
        intake_result = await intake_agent.run(task=purchase_request)

        intake_output = intake_result.messages[-1].content

        print("========== Intake Agent ==========")
        print(intake_output)

        purchase_data = json.loads(intake_output)

        # ==============================
        # Policy Agent
        # ==============================
        policy_result = await policy_agent.run(
            task=json.dumps(purchase_data, indent=4)
        )

        policy_output = policy_result.messages[-1].content

        print("\n========== Policy Agent ==========")
        print(policy_output)

        policy_data = json.loads(policy_output)

        # ==============================
        # Approval Agent
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

        return approval_output