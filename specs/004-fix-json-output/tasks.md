# Tasks: Fix JSON Output Corruption

**Input**: Design documents from `specs/004-fix-json-output/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story this task belongs to ([US1], [US2], [US3])
- Exact file paths included in every description

---

## Phase 1: Setup

**Purpose**: Feature branch ready for work

- [x] T001 Create feature branch `004-fix-json-output` from main

---

## Phase 2: Foundational — Regression Test (Blocking)

**Purpose**: Write the failing test first so correctness is verifiable before and after every fix

**⚠️ CRITICAL**: T002 must be written and confirmed to fail before any fix task begins

- [x] T002 Add a regression test in `tests/test_console.py` (or a new `tests/test_json_output.py` if that file doesn't exist) using Click's `CliRunner` that invokes `yt issues list --format json` with a mocked API response containing a list with square-bracket values, captures stdout, asserts `json.loads(output)` succeeds without raising `json.JSONDecodeError`, and asserts no Rich markup warning text appears in the captured output. Confirm the test FAILS on the current (unfixed) code before proceeding.

**Checkpoint**: Failing regression test committed — story phases can now begin

---

## Phase 3: User Story 1 — Fix `issues.py` JSON output paths (P1) 🎯 MVP

**Goal**: Every `--format json` path in `youtrack_cli/commands/issues.py` writes valid, pipeable JSON

**Independent test**: `uv run pytest tests/ -k "json_output" -v` passes

- [x] T003 [US1] In `youtrack_cli/commands/issues.py` line ~656, replace `console.print(json.dumps(issues, indent=2))` with `click.echo(json.dumps(issues, indent=2))` (issues list JSON path)
- [x] T004 [P] [US1] In `youtrack_cli/commands/issues.py` line ~969, replace `console.print(json.dumps(issues, indent=2))` with `click.echo(json.dumps(issues, indent=2))` (issues get JSON path)
- [x] T005 [P] [US1] In `youtrack_cli/commands/issues.py` line ~1364, replace `console.print(json.dumps(comments, indent=2))` with `click.echo(json.dumps(comments, indent=2))` (comments list JSON path)
- [x] T006 [P] [US1] In `youtrack_cli/commands/issues.py` line ~1562, replace `console.print(json.dumps(attachments, indent=2))` with `click.echo(json.dumps(attachments, indent=2))` (attachments list JSON path)
- [x] T007 [P] [US1] In `youtrack_cli/commands/issues.py` line ~1682, replace `console.print(json.dumps(links, indent=2))` with `click.echo(json.dumps(links, indent=2))` (links list JSON path)
- [x] T008 [P] [US1] In `youtrack_cli/commands/issues.py` line ~1764, replace `console.print(json.dumps(link_types, indent=2))` with `click.echo(json.dumps(link_types, indent=2))` (link-types JSON path)
- [x] T009 [US1] Confirm regression test from T002 now passes: `uv run pytest tests/ -k "json_output" -v`

---

## Phase 4: User Story 2 — Fix all remaining command files (P2)

**Goal**: `--format json` produces valid JSON across every affected subcommand outside `issues.py`

**Independent test**: Each file's JSON output passes `python -m json.tool` (see quickstart.md)

- [x] T010 [US2] In `youtrack_cli/commands/users.py`, replace all 4 occurrences of `console.print(json.dumps(..., indent=2))` with `click.echo(json.dumps(..., indent=2))` at lines ~222 (`users`), ~535 (`groups`), ~587 (`roles`), ~678 (`teams`)
- [x] T011 [P] [US2] In `youtrack_cli/commands/projects.py`, replace all 3 occurrences of `console.print(json.dumps(..., indent=2))` with `click.echo(json.dumps(..., indent=2))` at lines ~216 (`projects`), ~280 (`project`), ~573 (`custom_fields`)
- [x] T012 [P] [US2] In `youtrack_cli/commands/articles.py`, replace all 5 occurrences of `console.print(json.dumps(..., indent=2))` with `click.echo(json.dumps(..., indent=2))` at lines ~679 (`articles`), ~821 (`articles`), ~882 (`draft_articles`), ~1244 (`comments`), ~1491 (`attachments`)
- [x] T013 [P] [US2] In `youtrack_cli/main.py`, replace both occurrences of `console.print(json.dumps(audit_data, indent=2, default=str))` with `click.echo(json.dumps(audit_data, indent=2, default=str))` at lines ~416 and ~2056

---

## Phase 5: User Story 3 — Verify human-readable output unchanged (P3)

**Goal**: Table/Rich-formatted output paths are completely unaffected by the changes above

**Independent test**: Full pytest suite passes with zero regressions

- [x] T014 [US3] Run the full test suite `uv run pytest` and confirm all pre-existing tests pass with no regressions introduced by Phase 3 and Phase 4 changes
- [x] T015 [P] [US3] Run `uv run pre-commit run --all-files` and confirm ruff and ty report no issues across all modified files

---

## Final Phase: Polish & Merge

**Purpose**: Quality gates and PR

- [x] T016 Run `uv run ruff check youtrack_cli/commands/issues.py youtrack_cli/commands/users.py youtrack_cli/commands/projects.py youtrack_cli/commands/articles.py youtrack_cli/main.py` and fix any lint errors
- [x] T017 Run `uv run ty check` across the repo and resolve any type errors
- [x] T018 Run `uv run pytest` one final time to confirm full suite green
- [ ] T019 Create PR targeting `main`, referencing issue #756, with description of root cause and fix

---

## Dependencies

```
T001 → T002 → T003-T008 (parallel within US1) → T009
                                                    ↓
                              T010, T011, T012, T013 (parallel within US2)
                                                    ↓
                                           T014, T015 (parallel within US3)
                                                    ↓
                                        T016 → T017 → T018 → T019
```

## Implementation Strategy

**MVP** (Story 1 only): T001 → T002 → T003–T009 — delivers a working `yt issues list/get/comments/attachments/links --format json` with a regression test. Shippable as a fix for the most-reported paths.

**Full fix**: Continue through US2 (T010–T013) and US3 (T014–T015) to cover all 20 sites.

## Parallel Execution

Within US1 (after T002 passes): T004, T005, T006, T007, T008 are all independent edits to different line ranges in `issues.py` — can be done in any order or simultaneously.

Within US2 (after US1 complete): T011, T012, T013 touch different files — fully parallel with T010.
