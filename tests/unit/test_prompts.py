"""Unit tests for the prompt templates."""

from __future__ import annotations

from scribe.analyzer import RepoFacts
from scribe.prompts import (
    PROMPT_BY_SECTION,
    SECTION_ORDER,
    prompt_features,
    prompt_installation,
    prompt_title,
)


def test_section_order_is_complete():
    expected = {
        "title", "description", "features", "tech_stack",
        "installation", "usage", "development", "license",
    }
    assert set(SECTION_ORDER) == expected
    assert set(PROMPT_BY_SECTION.keys()) == expected


def test_prompt_title_includes_project_name(example_facts: RepoFacts):
    rendered = prompt_title(example_facts)
    assert "demo" in rendered
    assert "H1" in rendered
    assert "tagline" in rendered


def test_prompt_features_mentions_frameworks(example_facts: RepoFacts):
    rendered = prompt_features(example_facts)
    assert "Frameworks detected: Flask" in rendered


def test_prompt_installation_includes_package_manager(example_facts: RepoFacts):
    rendered = prompt_installation(example_facts)
    assert "pip" in rendered


def test_prompt_license_branches(example_facts: RepoFacts):
    from scribe.prompts import prompt_license

    facts_with = example_facts
    rendered_with = prompt_license(facts_with)
    assert "MIT" in rendered_with

    facts_with.has_license = False
    facts_with.license_name = None
    rendered_without = prompt_license(facts_with)
    assert "LICENSE file" in rendered_without
