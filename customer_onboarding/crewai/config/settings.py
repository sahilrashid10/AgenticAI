import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CUSTOMERS_FILE = DATA_DIR / "customers.json"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
LLM_API_KEY = os.getenv(
	"LLM_API_KEY",
	os.getenv(
		"GEMINI_API_KEY",
		os.getenv(
			"GOOGLE_API_KEY",
			os.getenv("OPENAI_API_KEY", os.getenv("ANTHROPIC_API_KEY", "")),
		),
	),
)
