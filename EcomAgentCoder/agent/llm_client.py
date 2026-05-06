import os
import requests
from dotenv import load_dotenv


class LLMClient:

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        self.base_url = os.getenv(
            "DEEPSEEK_BASE_URL",
            "https://api.deepseek.com/chat/completions",
        ).strip()
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

        if not self.api_key:
            raise RuntimeError(
                "DEEPSEEK_API_KEY is missing. Please create .env and set your API key."
            )

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }

        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=120,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"LLM request failed: status={response.status_code}, body={response.text}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]