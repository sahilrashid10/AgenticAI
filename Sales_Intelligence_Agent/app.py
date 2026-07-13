import chromadb

client = chromadb.PersistentClient(path="./Sales_Intelligence_Agent/chroma_db")

collection = client.get_or_create_collection(
    name="sales-memory"
)

print("Collection created successfully!")