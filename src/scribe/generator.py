"""README generator orchestrator.

Iterates the section templates, calls Ollama for each prose section, and
assembles the final markdown. Deterministic sections (badges, project tree)
do not hit the LLM.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass

from .analyzer import RepoFacts
from .llm import ChatMessage, OllamaClient
from .prompts import PROMPT_BY_SECTION, SECTION_ORDER, SYSTEM_PROMPT
from .templates import render_badges, render_project_structure

log = logging.getLogger(__name__)


@dataclass
class GenerationEvent:
    section: str
    status: str  # "start" | "delta" | "done"
    payload: str = ""


ProgressCallback = Callable[[GenerationEvent], None]


class ReadmeGenerator:
    def __init__(self, client: OllamaClient):
        self.client = client

    # -------------------------- public API -------------------------- #

    def generate(
        self,
        facts: RepoFacts,
        sections: list[str] | None = None,
        on_progress: ProgressCallback | None = None,
        temperature: float = 0.2,
    ) -> str:
        """Return the assembled README as one markdown string."""
        chunks: list[str] = []
        for section in sections or list(SECTION_ORDER):
            chunk = self._render_section(section, facts, temperature)
            chunks.append(chunk)
            if section == "title":
                badges = render_badges(facts)
                if badges:
                    chunks.append(f"\n<div align=\"center\">\n\n{badges}\n\n</div>\n")
            if section == "development":
                tree = render_project_structure(facts)
                if tree:
                    chunks.append(tree)
            if on_progress:
                on_progress(GenerationEvent(section=section, status="done", payload=chunk))
        return "\n\n".join(chunk.strip() for chunk in chunks if chunk and chunk.strip()) + "\n"

    def stream(
        self,
        facts: RepoFacts,
        sections: list[str] | None = None,
        temperature: float = 0.2,
    ) -> Iterator[GenerationEvent]:
        """Yield events as each section is generated, token-by-token for prose
        sections. The final assembled README is the concatenation of all
        section payloads + deterministic blocks."""
        for section in sections or list(SECTION_ORDER):
            yield GenerationEvent(section=section, status="start")
            buffer: list[str] = []
            for delta in self._stream_section(section, facts, temperature):
                buffer.append(delta)
                yield GenerationEvent(section=section, status="delta", payload=delta)
            full = "".join(buffer)
            yield GenerationEvent(section=section, status="done", payload=full)
            if section == "title":
                badges = render_badges(facts)
                if badges:
                    yield GenerationEvent(
                        section="badges",
                        status="done",
                        payload=f"<div align=\"center\">\n\n{badges}\n\n</div>",
                    )
            if section == "development":
                tree = render_project_structure(facts)
                if tree:
                    yield GenerationEvent(section="project_structure", status="done", payload=tree)

    # -------------------------- internal -------------------------- #

    def _render_section(self, section: str, facts: RepoFacts, temperature: float) -> str:
        prompt_fn = PROMPT_BY_SECTION.get(section)
        if prompt_fn is None:
            log.warning("Unknown section '%s'", section)
            return ""
        messages = [
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt_fn(facts)),
        ]
        return self.client.chat(messages, temperature=temperature).strip()

    def _stream_section(self, section: str, facts: RepoFacts, temperature: float) -> Iterator[str]:
        prompt_fn = PROMPT_BY_SECTION.get(section)
        if prompt_fn is None:
            return
        messages = [
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt_fn(facts)),
        ]
        yield from self.client.stream_chat(messages, temperature=temperature)
