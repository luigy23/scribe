"""Thin wrapper around the Ollama HTTP API used by Scribe.

The public Ollama Python package handles streaming for us; this module adds:
- a `ready()` check that distinguishes "server down" from "model not pulled",
- a uniform `chat()` interface returning plain strings,
- a `stream_chat()` generator that yields tokens as they arrive.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

import httpx
import ollama

DEFAULT_MODEL = os.environ.get("SCRIBE_MODEL", "qwen2.5-coder:7b")
DEFAULT_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

log = logging.getLogger(__name__)


class OllamaUnavailableError(RuntimeError):
    """Raised when the Ollama server is not reachable."""


class ModelNotPulledError(RuntimeError):
    """Raised when the configured model is not present locally."""


@dataclass(slots=True)
class ChatMessage:
    role: str  # "system", "user", "assistant"
    content: str


class OllamaClient:
    def __init__(self, model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST, timeout: float = 120.0):
        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout
        self._client = ollama.Client(host=self.host, timeout=timeout)

    # ----------------------------- introspection ----------------------------- #

    def ready(self) -> tuple[bool, str]:
        """Return (ready, message)."""
        try:
            with httpx.Client(timeout=2.0) as http:
                http.get(self.host)
        except (httpx.RequestError, httpx.HTTPError):
            return False, f"Ollama server unreachable at {self.host}. Start it with `ollama serve`."

        try:
            installed = {m["model"] for m in self._client.list()["models"]}
        except Exception as exc:  # pragma: no cover - network edge case
            return False, f"Could not list Ollama models: {exc}"

        if not any(name.startswith(self.model.split(":")[0]) for name in installed):
            return (
                False,
                f"Model '{self.model}' is not pulled. Run: ollama pull {self.model}",
            )
        return True, f"OK — {self.model} ready at {self.host}"

    # --------------------------------- chat ---------------------------------- #

    def chat(self, messages: Iterable[ChatMessage], temperature: float = 0.2) -> str:
        payload = [{"role": m.role, "content": m.content} for m in messages]
        try:
            response = self._client.chat(
                model=self.model,
                messages=payload,
                options={"temperature": temperature},
                stream=False,
            )
        except ollama.ResponseError as exc:
            if "not found" in str(exc).lower():
                raise ModelNotPulledError(
                    f"Model '{self.model}' is not pulled. Run: ollama pull {self.model}"
                ) from exc
            raise
        except (httpx.ConnectError, httpx.RequestError) as exc:
            raise OllamaUnavailableError(
                f"Ollama server unreachable at {self.host}. Start it with `ollama serve`."
            ) from exc
        return response["message"]["content"]

    def stream_chat(
        self, messages: Iterable[ChatMessage], temperature: float = 0.2
    ) -> Iterator[str]:
        payload = [{"role": m.role, "content": m.content} for m in messages]
        try:
            for chunk in self._client.chat(
                model=self.model,
                messages=payload,
                options={"temperature": temperature},
                stream=True,
            ):
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
        except ollama.ResponseError as exc:
            if "not found" in str(exc).lower():
                raise ModelNotPulledError(
                    f"Model '{self.model}' is not pulled. Run: ollama pull {self.model}"
                ) from exc
            raise
        except (httpx.ConnectError, httpx.RequestError) as exc:
            raise OllamaUnavailableError(
                f"Ollama server unreachable at {self.host}. Start it with `ollama serve`."
            ) from exc
