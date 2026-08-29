"""Pre-run guard: a tagged run refuses a dirty working tree before any model call.

A tagged results file is a source of record; the third dirty-tree incident of the
weekend (six of twenty committed results files record git_dirty, two of them pasted
into REPRODUCTION.md) showed the after-the-run warning fires only once the money is
spent. Untracked files under eval/results/ are exempt: they are the harness's own
prior outputs, never inputs, and a fresh-clone verifier accumulates them by
following REPRODUCTION.md — refusing on those would break CN-2.
"""

from __future__ import annotations

import sys

import pytest

from eval import run_eval

MODIFIED_TRACKED_FILE = " M src/advanced/solve.py"
UNTRACKED_INPUT_FILE = "?? eval/cases/case-33-new-archetype.json"
UNTRACKED_RESULTS_FILES = (
    "?? eval/results/20990101-000000.json",
    "?? eval/results/20990101-000000.md",
)


def test_modified_tracked_file_blocks_a_tagged_run() -> None:
    porcelain = MODIFIED_TRACKED_FILE + "\n"
    assert run_eval.blocking_dirt(porcelain) == [MODIFIED_TRACKED_FILE]


def test_untracked_results_files_do_not_block_a_tagged_run() -> None:
    porcelain = "\n".join(UNTRACKED_RESULTS_FILES) + "\n"
    assert run_eval.blocking_dirt(porcelain) == []


def test_untracked_file_outside_results_blocks_a_tagged_run() -> None:
    porcelain = "\n".join((*UNTRACKED_RESULTS_FILES, UNTRACKED_INPUT_FILE)) + "\n"
    assert run_eval.blocking_dirt(porcelain) == [UNTRACKED_INPUT_FILE]


def test_clean_tree_blocks_nothing() -> None:
    assert run_eval.blocking_dirt("") == []


def test_tagged_dirty_run_refuses_before_loading_cases_or_calling_models(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        run_eval, "git_status_porcelain", lambda: MODIFIED_TRACKED_FILE + "\n"
    )

    def cases_reached(*args: object, **kwargs: object) -> None:
        raise AssertionError("guard failed: the run proceeded past the refusal point")

    monkeypatch.setattr(run_eval, "load_cases", cases_reached)
    monkeypatch.setattr(sys, "argv", ["run_eval.py", "--tag", "final"])
    assert run_eval.main() == 2
    out = capsys.readouterr().out
    assert "REFUSED" in out
    assert MODIFIED_TRACKED_FILE in out
    assert "no model call" in out.lower()


def test_untagged_dirty_run_is_not_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        run_eval, "git_status_porcelain", lambda: MODIFIED_TRACKED_FILE + "\n"
    )

    class ProceededPastGuard(Exception):
        pass

    def cases_reached(*args: object, **kwargs: object) -> None:
        raise ProceededPastGuard

    monkeypatch.setattr(run_eval, "load_cases", cases_reached)
    monkeypatch.setattr(sys, "argv", ["run_eval.py"])
    with pytest.raises(ProceededPastGuard):
        run_eval.main()
