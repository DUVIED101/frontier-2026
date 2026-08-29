"""The demo CLI's deterministic surface (T-2): argument and file errors exit
cleanly with a usage message and never reach the model. The happy path makes a
model call and is exercised live (checkpoint 2026-08-29), not unit-mocked (T-3)."""

from __future__ import annotations

from src.advanced.cli import main


def test_cli_requires_exactly_one_argument() -> None:
    assert main([]) == 2


def test_cli_rejects_a_missing_file_without_calling_the_model() -> None:
    assert main(["/nonexistent/posting.txt"]) == 2
