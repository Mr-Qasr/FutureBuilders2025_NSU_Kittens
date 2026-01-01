"""Simple OpenAI-style client for local LLM servers (e.g. Ollama)."""

import requests
from typing import Optional, Dict, Any
from src.core.logger import logger


class LLMClient:
    def __init__(self, endpoint: str, model: str, api_key: str | None = None):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.api_key = api_key

    def chat(self, messages: list[dict[str, str]], extra: Optional[Dict[str, Any]] = None) -> Optional[str]:
        if not self.endpoint or not self.model:
            logger.warning("LLMClient called without endpoint or model")
            return None

        body: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if extra:
            body.update(extra)

        headers: Dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            resp = requests.post(self.endpoint, json=body, headers=headers, timeout=60)
            if not resp.ok:
                logger.error("LLM error (%s): %s", self.model, resp.text[:300])
                return None
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.exception("LLM request failed for model %s: %s", self.model, e)
            return None
