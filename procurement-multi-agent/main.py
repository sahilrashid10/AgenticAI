import asyncio
import os

from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Load variables from .env
load_dotenv()

# Create the model client
model_client = OpenAIChatCompletionClient(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "structured_output": True,
        "family": "llama"
    }
)
# Create a simple AI agent
assistant = AssistantAgent(
    name="assistant",
    model_client=model_client,
    system_message="You are a helpful AI assistant."
)

async def main():
    response = await assistant.run(
        task="Say hello and introduce yourself in one sentence."
    )

    print(response.messages[-1].content)

    await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())