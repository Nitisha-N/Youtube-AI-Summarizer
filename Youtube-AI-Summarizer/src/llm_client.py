import google.generativeai as genai
from typing import Optional


class GeminiClient:
    """Wrapper around Gemini API with retry logic and error handling."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash",
                 temperature: float = 0.4, max_tokens: int = 2048):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate text from a prompt with optional system context."""
        try:
            config = genai.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )

            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            else:
                full_prompt = prompt

            response = self.model.generate_content(full_prompt, generation_config=config)

            if not response or not response.text:
                raise ValueError("Empty response from model.")

            return response.text.strip()

        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}")
