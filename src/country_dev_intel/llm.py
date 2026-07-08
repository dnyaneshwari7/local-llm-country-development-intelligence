from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import request
from urllib.error import URLError


@dataclass
class OllamaClient:
    base_url: str = "http://localhost:11434"
    timeout_seconds: int = 120

    def is_available(self, timeout_seconds: int = 2) -> bool:
        try:
            with request.urlopen(f"{self.base_url.rstrip('/')}/api/tags", timeout=timeout_seconds):
                return True
        except (OSError, URLError):
            return False

    def generate(self, model: str, prompt: str, temperature: float = 0.1) -> str:
        payload = json.dumps(
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature},
            }
        ).encode("utf-8")
        req = request.Request(
            f"{self.base_url.rstrip('/')}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8")
        return json.loads(body)["response"]


def parse_json_response(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json\n", "", 1)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("LLM response did not contain a JSON object.")
    return json.loads(text[start : end + 1])
