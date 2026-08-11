from typing import Iterator

from google import genai
from google.genai import types

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("llm_client")


class GeminiClient:
    """Client wrapper for Google Gemini LLM API using modern google-genai SDK."""

    def __init__(
        self, api_key: str = settings.GOOGLE_API_KEY, model_name: str = settings.GEMINI_LLM_MODEL
    ):
        self.api_key = api_key
        self.model_name = model_name
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("GeminiClient initialized without GOOGLE_API_KEY.")

    def generate_response(
        self,
        prompt: str,
        system_instruction: str = None,
        temperature: float = 0.2,
        top_p: float = 0.9,
    ) -> str:
        """Generates a synchronous response from Gemini LLM."""
        if not self.client:
            raise ValueError("GOOGLE_API_KEY is missing. Please set it in .env file.")

        config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=top_p,
            system_instruction=system_instruction,
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API ({self.model_name}): {e}")
            # Try fallback model if primary fails
            if self.model_name != "gemini-2.5-flash":
                logger.info("Attempting fallback call with gemini-2.5-flash...")
                try:
                    fallback_res = self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                        config=config,
                    )
                    return fallback_res.text
                except Exception as fb_err:
                    logger.error(f"Fallback call failed: {fb_err}")
            raise e

    def generate_stream(
        self,
        prompt: str,
        system_instruction: str = None,
        temperature: float = 0.2,
        top_p: float = 0.9,
    ) -> Iterator[str]:
        """Streams response tokens from Gemini LLM."""
        if not self.client:
            yield "\n\n*[System Error: GOOGLE_API_KEY is missing. Please set it in .env file.]*"
            return

        config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=top_p,
            system_instruction=system_instruction,
        )

        try:
            response_stream = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Streaming error with Gemini model ({self.model_name}): {e}")
            yield f"\n\n*[System Error: Failed to generate response with Gemini API - {str(e)}]*"
