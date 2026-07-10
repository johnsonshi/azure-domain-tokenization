"""Shared pytest fixtures."""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def azure_md() -> str:
    return (FIXTURES / "azure_sample.md").read_text(encoding="utf-8")


@pytest.fixture
def general_md() -> str:
    return (FIXTURES / "general_sample.md").read_text(encoding="utf-8")


@pytest.fixture
def automation_md() -> str:
    return (FIXTURES / "automation_sample.md").read_text(encoding="utf-8")
