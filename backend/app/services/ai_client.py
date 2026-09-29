from google import genai
from google.genai import types

from app.core.config import settings

_client = genai.Client(api_key=settings.google_api_key)


def ask_ai(system_prompt: str, user_message: str, max_tokens: int = 500) -> str:
    response = _client.models.generate_content(
        model=settings.ai_model,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text
