"""Integration tests for the generator orchestrator with a stub LLM."""

from __future__ import annotations

from scribe.analyzer import RepoFacts
from scribe.generator import GenerationEvent, ReadmeGenerator


def test_generator_assembles_all_sections(stub_client, example_facts: RepoFacts):
    gen = ReadmeGenerator(stub_client)  # type: ignore[arg-type]
    readme = gen.generate(example_facts)
    assert readme.startswith("# Demo")
    assert "## Overview" in readme
    assert "## Features" in readme
    assert "## Installation" in readme
    assert "## License" in readme
    # Deterministic blocks should appear:
    assert "## Project structure" in readme  # from render_project_structure
    assert "shields.io" in readme  # from render_badges


def test_generator_can_run_subset(stub_client, example_facts: RepoFacts):
    gen = ReadmeGenerator(stub_client)  # type: ignore[arg-type]
    readme = gen.generate(example_facts, sections=["title", "features"])
    assert "# Demo" in readme
    assert "## Features" in readme
    assert "## Overview" not in readme


def test_generator_stream_emits_events(stub_client, example_facts: RepoFacts):
    gen = ReadmeGenerator(stub_client)  # type: ignore[arg-type]
    events = list(gen.stream(example_facts, sections=["title"]))
    statuses = [e.status for e in events]
    assert "start" in statuses
    assert "delta" in statuses
    assert "done" in statuses
    deltas = [e.payload for e in events if e.status == "delta"]
    assert "".join(deltas).startswith("# Demo")
