from semantic_kernel import Kernel

from config.settings import GITHUB_TOKEN, MODEL_NAME

from plugins.customer_plugin import CustomerPlugin

from models.customer import Customer

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings

from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior


import asyncio
from openai import AsyncOpenAI

async def main():

    client = AsyncOpenAI(
        api_key=GITHUB_TOKEN,
        base_url="https://models.github.ai/inference"
)
    kernel = Kernel()

    kernel.add_service(
        OpenAIChatCompletion(
            service_id="chat",
            ai_model_id=MODEL_NAME,
            async_client=client
        )
    )

    settings = OpenAIChatPromptExecutionSettings(
        # this value is from 0 to 1, more the value more the randomness in the output, less the value more deterministic the output will be.
        # temperature=0.2, not changing when using the github model, as it is not working as expected, so using the default value of 1
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    kernel.add_plugin(
        CustomerPlugin(),
        plugin_name="CustomerPlugin"
    )
    customer = Customer(
        name="Sahil Rashid",
        email="sahil@gmail.com",
        company="MAQ Software"
    )

    # testing the plugin function
        # plugin = CustomerPlugin()

        # validation_result = plugin.validate_customer(
        #     customer.name,
        #     customer.email,
        #     customer.company
        # )

        # print(validation_result)

    prompt = f"""
    You are a Customer Onboarding Assistant.

    A customer wants to register.

    Customer Details:

    Name: {customer.name}
    Email: {customer.email}
    Company: {customer.company}

    First validate the customer using the available plugin.

    If validation fails,
    return only the validation error.

    If validation succeeds,

    1. Draft a welcome email.
    2. Generate an internal onboarding task list.
    """
    response = await kernel.invoke_prompt(
        prompt,
        settings=settings
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())