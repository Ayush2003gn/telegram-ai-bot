from __future__ import annotations

import json
import re
import httpx
from app.schemas import ParsedIntent


class GeminiService:  # name kept to avoid changing main.py
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    async def parse_message(self, message_text: str) -> ParsedIntent:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # REQUIRED by OpenRouter
            "HTTP-Referer": "http://localhost",
            "X-Title": "Telegram AI Bot",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Extract intent and return ONLY valid JSON:\n"
                        "{"
                        '"type":"task or event",'
                        '"title":"string",'
                        '"date":"YYYY-MM-DD or null",'
                        '"time":"HH:MM or null"'
                        "}"
                    ),
                },
                {
                    "role": "user",
                    "content": message_text,
                },
            ],
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(self.url, headers=headers, json=payload)

        # 🔴 IMPORTANT: show real OpenRouter error if any
        if response.status_code != 200:
            print("OPENROUTER ERROR:", response.status_code, response.text)
            response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        json_text = self._extract_json(content)
        return ParsedIntent.model_validate(json.loads(json_text))

    @staticmethod
    def _extract_json(text: str) -> str:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON found in response: {text}")
        return match.group(0)