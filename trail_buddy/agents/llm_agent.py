import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class LlmAgent:
    """Wrapper for Google Gemini API (gemini-2.5-flash-lite) for local use."""

    def __init__(self, model_name="gemini-2.5-flash-lite"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY is missing from .env")
        self.client = genai.Client(api_key=api_key)
        self.model = model_name

    def ask_gemini(self, prompt: str, max_output_tokens: int = 500) -> str:
        """Send prompt to Gemini synchronously."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(max_output_tokens=max_output_tokens)
            )
            text = getattr(response, "text", "")
            logger.info("LLM received prompt, length=%d", len(prompt))
            return text.strip() if text else ""
        except Exception as e:
            logger.error("LLM error: %s", e)
            return ""
