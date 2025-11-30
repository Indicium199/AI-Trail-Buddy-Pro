from dotenv import load_dotenv
import os

# Explicitly load .env from the repo root
load_dotenv(dotenv_path="AI-Trail-Buddy-Pro/.env")

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print("✅ GEMINI_API_KEY loaded successfully!")
    print("Key (first 4 chars):", api_key[:4], "...")
else:
    print("❌ GEMINI_API_KEY not found. Check your .env file.")

