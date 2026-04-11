import google.generativeai as genai
from typing import Optional


class GeminiClient:
    """Wrapper around the Gemini API with configuration and error handling."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.4,
        max_tokens: int = 2048,
    ):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str) -> str:
        """Send a prompt and return the response text."""
        try:
            config = genai.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
            response = self.model.generate_content(prompt, generation_config=config)

            if not response or not response.text:
                raise ValueError("Empty response received from the model.")

            return response.text.strip()

        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {str(e)}")
