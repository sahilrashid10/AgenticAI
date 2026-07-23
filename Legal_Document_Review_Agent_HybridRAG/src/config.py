import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "chroma_db")
