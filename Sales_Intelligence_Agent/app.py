from ast import arguments
import json
from dotenv import load_dotenv
import os
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

vector_client = chromadb.PersistentClient(path="./Sales_Intelligence_Agent/chroma_db")

collection = vector_client.get_or_create_collection(
    name="sales-memory"
)

with open("./Sales_Intelligence_Agent/data/crm_data.json", "r") as f:
    crm_data = json.load(f)

documents = []
ids = []

for record in crm_data:
    document = f"""
Customer: {record['customer']}
Company: {record['company']}
Interest: {record['interest']}
Budget: {record['budget']}
"""

    documents.append(document.strip())
    ids.append(record["id"])

# for record in documents:
#     print(record)

# Think of it as a tiny AI model trained for understanding sentence meaning.
# Example:
# Azure Migration
# ↓
# [0.21, -0.44, 0.17, ...]
print("1. Loading model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# It returns a vector with 384 numbers.



# checking how the embedding looks like
# print(type(embedding))
# print(len(embedding))
# print(embedding[:10])


print("2. Creating embeddings...")
embeddings = embedding_model.encode(documents).tolist()

print("3. Adding to ChromaDB...")
collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings
)

print("4. Done")
print("Documents stored successfully!")


# Asking the questions to the model to find the most relevant documents based on the embeddings.
query = "Which customer is interested in Azure?"

query_embedding = embedding_model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=2
)

# results = {
#     "ids": [
#         ["1","2"]
#     ],

#     "documents": [
#         [
#             "Customer: John...",
#             "Customer: Alice..."
#         ],
            # ["Customer: John...",
#             "Customer: Alice..."]
#     ],

#     "distances":[
#         [
#             0.74,
#             0.91
#         ]
#     ]
# }
retrieved_documents = results["documents"][0]

context = "\n\n".join(retrieved_documents)

print("Retrieved Context")
print("-" * 40)
print(context)


from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from openai import AsyncOpenAI
from semantic_kernel.functions import KernelArguments
import asyncio

async def main():
    groq_client = AsyncOpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

    kernel = Kernel()

    kernel.add_service(
        OpenAIChatCompletion(
            service_id="chat",
            ai_model_id=MODEL_NAME,
            async_client=groq_client
        )
    )

    settings = OpenAIChatPromptExecutionSettings(
        temperature=0
    )

    prompt = f"""
You are a Sales Intelligence Assistant.
Answer ONLY using the CRM context below.
CRM Context:

{context}
User Question:

{query}
If the answer is not present in the CRM context, say:
"I couldn't find that information."
    """
    arguments = KernelArguments(
    settings=settings
    )
    response = await kernel.invoke_prompt(
        prompt,
        arguments=arguments
    )
    print("\nFinal Answer")
    print("-" * 40)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())