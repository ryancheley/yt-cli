# Tasks: Fix State Filter Returning Incorrect Issues

**Feature**: `specs/001-fix-state-filter` | **Branch**: `fix-state-filter-721`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Bug fix scope — small, well-understood change. Tests requested per Constitution II
(regression test required). No new dependencies, no data model, no contract change.

## Phase 1: Setup

_No setup required — existing project, no new dependencies (Constitution I: `uv` only, nothing to add)._

## Phase 2: Foundational

- [X] T001 Add a small helper `escape_query_value(value: str) -> str` that wraps a filter value in YouTrack curly braces (`{value}`), stripping surrounding whitespace and avoiding double-wrapping if already brace-wrapped, in `youtrack_cli/utils.py`.

## Phase 3: User Story 1 — Filter issues by a multi-word state (Priority: P1)

**Goal**: `list --state 'In Progress'` returns only issues in that exact state.

**Independent Test**: Query built for a multi-word state is brace-escaped so YouTrack treats it as one atomic term; issues only mentioning the words in text are excluded.

- [X] T002 [P] [US1] Add regression test asserting `IssueManager.list_issues(state="In Progress")` composes a query containing `State: {In Progress}` (not a bare trailing `Progress` term), in `tests/test_issues.py` (or the existing issues test module). Test MUST fail before T004.
- [X] T003 [P] [US1] Add regression test asserting the legacy `IssueClient.list_issues(state="In Progress")` composes `state:{In Progress}`, in the same test module.
- [X] T004 [US1] In `youtrack_cli/managers/issues.py` (`IssueManager.list_issues`, ~line 649), apply `escape_query_value(state)` when building the `State:` filter term.
- [X] T005 [US1] In `youtrack_cli/issues.py` (`IssueClient.list_issues`, ~line 284), apply `escape_query_value(state)` when building the `state:` filter term.

## Phase 4: User Story 2 — Single-word state filtering still works (Priority: P2)

**Goal**: Single-word states (e.g. `Open`) remain correct after escaping.

**Independent Test**: `list --state Open` returns only "Open" issues.

- [X] T006 [P] [US2] Add regression test asserting a single-word state (`Open`) composes `State: {Open}` and returns correctly, in the same test module.

## Phase 5: Polish & Cross-Cutting

- [X] T007 Run `uv run pytest`, `uv run ruff check`, `uv run ruff format`, and `uv run ty` — all must pass (Constitution I & II gates).
- [X] T008 Verify no `docs/` update is needed (no CLI surface change); confirm help-text examples in `youtrack_cli/commands/issues.py` remain valid.

## Dependencies

- T001 (helper) blocks T004, T005.
- Tests T002, T003, T006 should be written to fail first (TDD, Constitution II), then pass after T004/T005.
- T007 runs last.

## Parallel Opportunities

- T002, T003, T006 are independent test additions ([P], different assertions, same-or-different files — coordinate if same file).
- T004 and T005 touch different files and can proceed in parallel once T001 exists.

## MVP Scope

User Story 1 (T001–T005) is the MVP — it resolves issue #721. US2 (T006) guards against regression.
