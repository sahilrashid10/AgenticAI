import asyncio

from openai import AsyncOpenAI

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments

from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)

from config.settings import GROQ_API_KEY, MODEL_NAME
from config.prompts import (
    CUSTOMER_ONBOARDING_PROMPT,
    WELCOME_EMAIL_PROMPT,
    TASK_PROMPT,
)

from models.customer import Customer
from plugins.customer_plugin import CustomerPlugin


def normalize_onboarding_response(response):
    response_text = str(response)
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


async def main():

    client = AsyncOpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

    kernel = Kernel()

    kernel.add_service(
        OpenAIChatCompletion(
            service_id="chat",
            ai_model_id=MODEL_NAME,
            async_client=client
        )
    )

    onboarding_settings = OpenAIChatPromptExecutionSettings(
        temperature=0,
        function_choice_behavior=FunctionChoiceBehavior.Auto(
            auto_invoke=True,
            filters={"included_plugins": ["CustomerPlugin"]}
        )
    )

    generation_settings = OpenAIChatPromptExecutionSettings()

    kernel.add_plugin(
        CustomerPlugin(),
        plugin_name="CustomerPlugin"
    )

    try:
        customer = Customer(
            name=input("Customer Name: "),
            email=input("Customer Email: "),
            company=input("Company Name: ")
        )

        onboarding_args = KernelArguments(
            settings=onboarding_settings,
            name=customer.name,
            email=customer.email,
            company=customer.company
        )

        response = await kernel.invoke_prompt(
            CUSTOMER_ONBOARDING_PROMPT,
            arguments=onboarding_args
        )

        onboarding_result = normalize_onboarding_response(response)

        print("\n========== Onboarding Result ==========\n")
        print(onboarding_result)

        customer_saved = "successfully saved" in onboarding_result.lower()

        if not customer_saved:
            return

        generation_args = KernelArguments(
            settings=generation_settings,
            name=customer.name,
            email=customer.email,
            company=customer.company
        )

        welcome_email = await kernel.invoke_prompt(
            WELCOME_EMAIL_PROMPT,
            arguments=generation_args
        )

        task_list = await kernel.invoke_prompt(
            TASK_PROMPT,
            arguments=generation_args
        )

        print("\n========== Welcome Email ==========\n")
        print(welcome_email)

        print("\n========== Task Checklist ==========\n")
        print(task_list)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
