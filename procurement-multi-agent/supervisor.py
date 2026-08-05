import json
import re

from agents import (
    intake_agent,
    policy_agent,
    approval_agent,
    risk_agent,
    judge_agent,
)
from tools import (
    get_company_policy,
    search_vendor,
    get_budget,
)


class ProcurementSupervisor:

    @staticmethod
    def _load_json_response(raw_content, label):
        if not raw_content or not raw_content.strip():
            raise ValueError(f"{label} returned an empty response instead of JSON.")

        cleaned_content = raw_content.strip()

        if cleaned_content.startswith("```"):
            cleaned_content = re.sub(r"^```(?:json)?\s*", "", cleaned_content)
            cleaned_content = re.sub(r"\s*```$", "", cleaned_content).strip()

        try:
            return json.loads(cleaned_content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned_content, re.DOTALL)
            if match:
                return json.loads(match.group(0))

            raise ValueError(
                f"{label} did not return valid JSON. Raw output: {raw_content!r}"
            )

    async def process_request(self, purchase_request):

        # ==============================
        # Intake Agent
        # ==============================
        intake_result = await intake_agent.run(task=purchase_request)

        intake_output = intake_result.messages[-1].content

        print("========== Intake Agent ==========")
        print(intake_output)

        purchase_data = self._load_json_response(intake_output, "Intake agent")

        # ==============================
        # Fetch External Data
        # ==============================

        company_policy = get_company_policy()

        vendor_info = search_vendor(
            purchase_data["vendor"]
        )

        # ==============================
        # Policy Agent
        # ==============================

        policy_input = f"""
        Purchase JSON:
        {json.dumps(purchase_data, indent=4)}

        Company Policy:
        {json.dumps(company_policy, indent=4)}

        Vendor Information:
        {json.dumps(vendor_info, indent=4)}
        """

        policy_result = await policy_agent.run(
            task=policy_input
        )

        policy_output = policy_result.messages[-1].content

        print("\n========== Policy Agent ==========")
        print(policy_output)

        policy_data = self._load_json_response(policy_output, "Policy agent")

        # ==============================
        # Approval Agent
        # ==============================

        budget_info = get_budget()
        approval_input = f"""
        Purchase JSON:
        {json.dumps(purchase_data, indent=4)}

        Policy Report:
        {json.dumps(policy_data, indent=4)}

        Budget Information:
        {json.dumps(budget_info, indent=4)}
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