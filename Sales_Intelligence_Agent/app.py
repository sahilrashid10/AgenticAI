import json
import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./Sales_Intelligence_Agent/chroma_db")

collection = client.get_or_create_collection(
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

for record in documents:
    print(record)

# Think of it as a tiny AI model trained for understanding sentence meaning.
# Example:
# Azure Migration
# ↓
# [0.21, -0.44, 0.17, ...]
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# It returns a vector with 384 numbers.
# Those numbers are what ChromaDB searches.
sample_text = documents[0]

embedding = embedding_model.encode(sample_text)

print(type(embedding))
print(len(embedding))
print(embedding[:10])