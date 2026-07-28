import os

from dotenv import load_dotenv

from openai import AsyncOpenAI

from semantic_kernel import Kernel

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

load_dotenv()

kernel = Kernel()

client = AsyncOpenAI(

    api_key=os.getenv("GROQ_API_KEY"),

    base_url="https://api.groq.com/openai/v1"

)

kernel.add_service(

    OpenAIChatCompletion(

        ai_model_id="llama-3.3-70b-versatile",

        async_client=client

    )

)

async def ask_llm(question, context):
    prompt = f"""
You are a legal document assistant.

Answer ONLY using the provided context.

If the answer is not present, say:

"I could not find that information in the provided documents."

Context:

{context}

Question:

{question}
"""
    response = await kernel.invoke_prompt(prompt)
    return str(response)