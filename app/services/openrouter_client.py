"""
app/services/openrouter_client.py

Thin, well-documented wrapper around the OpenRouter API. This is the
ONLY file in the codebase that should ever call OpenRouter directly —
routers call this service, never the HTTP API itself. That indirection
is what lets you swap providers later without touching endpoint code.

OpenRouter speaks the OpenAI-compatible /chat/completions schema, so
this client builds standard OpenAI-style message dicts (including the
multimodal `content: [{type: "text"...}, {type: "image_url"...}]`
format for vision).
"""

from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.core.config import settings


class OpenRouterClient:
    def __init__(self) -> None:
        self._base_url = settings.openrouter_base_url
        self._headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            # OpenRouter uses these two headers for its public leaderboard/
            # rate-limit attribution — harmless to omit, good practice to set.
            "HTTP-Referer": "https://anqa.app",
            "X-Title": settings.app_name,
        }

    @staticmethod
    def build_user_message(text: str, image_urls: list[str] | None = None) -> dict:
        """
        Builds one user message, switching automatically between plain-text
        and multimodal content shapes depending on whether images are present.
        """
        if not image_urls:
            return {"role": "user", "content": text}

        content: list[dict[str, Any]] = []
        if text:
            content.append({"type": "text", "text": text})
        for url in image_urls:
            content.append({"type": "image_url", "image_url": {"url": url}})
        return {"role": "user", "content": content}

    def _pick_model(self, has_images: bool) -> str:
        return settings.vision_model if has_images else settings.default_model

    async def chat_completion(
        self,
        messages: list[dict],
        has_images: bool = False,
        temperature: float = 0.7,
    ) -> dict:
        """Non-streaming completion. Returns the full parsed JSON response."""
        payload = {
            "model": self._pick_model(has_images),
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers,
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def chat_completion_stream(
        self,
        messages: list[dict],
        has_images: bool = False,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming completion. Yields text deltas as they arrive so the
        router can forward them to the client over SSE in real time.
        """
        payload = {
            "model": self._pick_model(has_images),
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/chat/completions",
                headers=self._headers,
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data = line.removeprefix("data: ").strip()
                    if data == "[DONE]":
                        break
                    yield data  # caller parses the JSON chunk & extracts delta


# Singleton instance — imported by routers/services that need to talk to the LLM
openrouter_client = OpenRouterClient()
