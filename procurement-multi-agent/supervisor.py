import json

from agents import (
    intake_agent,
    policy_agent,
    approval_agent,
    risk_agent,
    judge_agent,
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

        # ==============================
        # Risk Agent
        # ==============================

        risk_result = await risk_agent.run(
            task=approval_input
        )

        risk_output = risk_result.messages[-1].content

        print("\n========== Risk Agent ==========")
        print(risk_output)

        # ==============================
        # Judge Agent
        # ==============================

        judge_input = f"""
        Purchase JSON:
        {json.dumps(purchase_data, indent=4)}

        Policy JSON:
        {json.dumps(policy_data, indent=4)}

        Approval Decision:
        {approval_output}

        Risk Assessment:
        {risk_output}
        """

        judge_result = await judge_agent.run(
            task=judge_input
        )

        judge_output = judge_result.messages[-1].content

        print("\n========== Judge Agent ==========")
        print(judge_output)

        return judge_output