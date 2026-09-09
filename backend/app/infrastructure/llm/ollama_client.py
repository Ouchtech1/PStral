"""Minimal Ollama client with explicit resource budgets and error handling."""

import json
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings


class LLMError(RuntimeError):
    pass


class LLMUnavailable(LLMError):
    pass


@dataclass(frozen=True)
class StreamChunk:
    content: str = ""
    done: bool = False
    done_reason: str | None = None


class OllamaClient:
    def __init__(self) -> None:
        timeout = httpx.Timeout(settings.CHAT_TIMEOUT_SECONDS, connect=5.0, read=settings.CHAT_TIMEOUT_SECONDS)
        self._client = httpx.AsyncClient(base_url=settings.OLLAMA_BASE_URL.rstrip("/"), timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    def _payload(self, messages: list[dict[str, str]], max_tokens: int, *, stream: bool, response_format: dict | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": settings.OLLAMA_MODEL,
            "messages": messages,
            "stream": stream,
            "keep_alive": settings.OLLAMA_KEEP_ALIVE,
            "think": False,
            "options": {
                "temperature": 0.1,
                "top_k": 50,
                "top_p": 1.0,
                "repeat_penalty": 1.05,
                "num_ctx": settings.MODEL_CONTEXT_TOKENS,
                "num_predict": max_tokens,
                "num_thread": settings.OLLAMA_NUM_THREADS,
            },
        }
        if response_format:
            payload["format"] = response_format
        return payload

    async def model_is_available(self) -> bool:
        try:
            response = await self._client.get("/api/tags", timeout=5.0)
            response.raise_for_status()
            names = {model.get("name") for model in response.json().get("models", [])}
            return settings.OLLAMA_MODEL in names
        except (httpx.HTTPError, ValueError):
            return False

    async def chat_stream(self, system_prompt: str, messages: list[dict[str, str]]) -> AsyncGenerator[StreamChunk, None]:
        full_messages = [{"role": "system", "content": system_prompt}, *messages]
        try:
            async with self._client.stream(
                "POST", "/api/chat", json=self._payload(full_messages, settings.CHAT_OUTPUT_TOKENS, stream=True)
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise LLMError("Réponse non lisible du moteur local.") from exc
                    if data.get("error"):
                        raise LLMError("Le moteur local a refusé la génération.")
                    message = data.get("message") or {}
                    yield StreamChunk(
                        content=message.get("content", ""),
                        done=bool(data.get("done")),
                        done_reason=data.get("done_reason"),
                    )
        except httpx.ConnectError as exc:
            raise LLMUnavailable("Le moteur IA local est indisponible.") from exc
        except httpx.TimeoutException as exc:
            raise LLMUnavailable("Le moteur IA local a dépassé le délai autorisé.") from exc
        except httpx.HTTPStatusError as exc:
            raise LLMUnavailable("Le moteur IA local a renvoyé une erreur.") from exc
        except httpx.HTTPError as exc:
            raise LLMUnavailable("La communication avec le moteur IA local a échoué.") from exc

    async def chat_json(self, system_prompt: str, user_message: str, response_format: dict[str, Any]) -> dict[str, Any]:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]
        try:
            response = await self._client.post(
                "/api/chat",
                json=self._payload(messages, settings.SQL_OUTPUT_TOKENS, stream=False, response_format=response_format),
            )
            response.raise_for_status()
            data = response.json()
            if data.get("done_reason") == "length":
                raise LLMError("La sélection SQL a été tronquée.")
            content = (data.get("message") or {}).get("content")
            if not isinstance(content, str):
                raise LLMError("Le moteur local n'a pas produit de sélection SQL.")
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMError("Le moteur local n'a pas respecté le format SQL attendu.") from exc
        except httpx.ConnectError as exc:
            raise LLMUnavailable("Le moteur IA local est indisponible.") from exc
        except httpx.TimeoutException as exc:
            raise LLMUnavailable("Le moteur IA local a dépassé le délai autorisé.") from exc
        except httpx.HTTPStatusError as exc:
            raise LLMUnavailable("Le moteur IA local a renvoyé une erreur.") from exc
        except httpx.HTTPError as exc:
            raise LLMUnavailable("La communication avec le moteur IA local a échoué.") from exc
