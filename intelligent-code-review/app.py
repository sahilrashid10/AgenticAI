import asyncio

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion


async def main():

    kernel = Kernel()

    kernel.add_service(
        OllamaChatCompletion(
            ai_model_id="llama3.2:3b",
            service_id="ollama",
        )
    )

    function = kernel.add_function(
        plugin_name="Reviewer",
        function_name="review",
        prompt="""
You are a senior Python reviewer.

Review the following code.

{{$input}}
""",
    )

    result = await kernel.invoke(
        function,
        input="""
def add(a,b):
 return a+b
"""
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())