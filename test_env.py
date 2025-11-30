from dotenv import load_dotenv
import os

# load the .env file from the repo root
from pathlib import Path
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print("✅ GEMINI_API_KEY loaded successfully!")
    print("Key (first 4 chars):", api_key[:4], "...")
else:
    print("❌ GEMINI_API_KEY not found. Check your .env file.")
