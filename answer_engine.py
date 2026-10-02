"""Answer generation via OpenRouter (OpenAI-compatible API)."""
from openai import OpenAI

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    SYSTEM_PROMPT,
)


class AnswerEngine:
    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
        )

    def answer(self, question: str) -> str:
        resp = self.client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
