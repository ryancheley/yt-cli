# Implementation Plan: Remediate four security findings (#740–#743)

**Branch**: `security-fixes-740-743` | **Date**: 2026-07-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-security-fixes/spec.md`

## Summary

Four independent, low-risk fixes to existing YouTrack CLI security findings:
- **#740** (path traversal): sanitize the server-supplied attachment filename in
  the article download command so writes stay in the working directory.
- **#741** (cleartext transport): warn (stderr) when authenticating against an
  `http://` base URL before the token is sent; still proceed (warn-only).
- **#742** (shell hardening): run tutorial example commands via
  `create_subprocess_exec` with a parsed argv list instead of
  `create_subprocess_shell(shell=True)`; remove the dead shell path.
- **#743** (process): add `SECURITY.md` disclosure policy.

Three behavioral fixes ship with regression tests (constitution: NON-NEGOTIABLE).

## Technical Context

**Language/Version**: Python (project targets 3.10–3.14; run via `uv`)

**Primary Dependencies**: `click`, `rich`, `httpx`, `pydantic` (all existing —
no new dependencies)

**Storage**: N/A (config `.env` / keyring already exist; untouched here)

**Testing**: `pytest` with real objects (constitution II); `tox` for the matrix.
New tests colocated under `tests/`.

**Target Platform**: Local CLI on developer machines (single-user install)

**Project Type**: Single-project Python CLI

**Performance Goals**: No performance impact; changes are on error/edge paths.

**Constraints**: Threat model = single-user local install; remote/network
inputs in scope, local-user file-permission isolation out of scope. No new
dependencies. No CLI-surface breakage for the happy path.

**Scale/Scope**: 3 source files touched + 1 new doc + 3 test files (or additions
to existing test modules). ~small diffs each.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Code Quality**: `ruff` + `ty` clean; changes are typed; deps via `uv`;
  docs updated (SECURITY.md is itself doc; review `docs/` for any auth/download
  pages needing a note). ✅ PASS.
- **II. Testing Standards (NON-NEGOTIABLE)**: Each behavioral fix (FR-001,
  FR-003, FR-005) gets a regression test that fails before and passes after,
  using real objects (drive the command/executor/helper directly; the download
  test injects a crafted filename via the manager result — mock only the remote
  boundary, justified). ✅ PASS.
- **III. UX Consistency**: Warnings go to stderr; error/exit behavior unchanged;
  the `http://` warning is actionable ("token sent in cleartext"). Happy-path
  output unchanged. ✅ PASS.
- **IV. Performance**: Edge/error-path only; no latency change. ✅ PASS.
- **Workflow**: Feature branch `security-fixes-740-743`; issues #740–#743;
  squash-merge after green. ✅ PASS.

No violations. Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/003-security-fixes/
├── plan.md              # This file
├── spec.md              # Spec (+ Clarifications)
├── research.md          # Phase 0 — approach decisions per finding
├── quickstart.md        # Phase 1 — validation guide
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 (/speckit-tasks)
```

Not generated (justified): `data-model.md` — the "entities" (filename, base URL)
are inputs, not persisted models. `contracts/` — no new/changed external
interface; behavior changes only.

### Source Code (repository root)

```text
youtrack_cli/commands/articles.py      # #740 sanitize server filename
youtrack_cli/auth.py                   # #741 warn on http:// (verify path)
youtrack_cli/tutorial/executor.py      # #742 exec instead of shell
youtrack_cli/tutorial/core.py          # #742 remove/convert dead shell path
SECURITY.md                            # #743 new file
tests/…                                # regression tests for #740/#741/#742
```

**Structure Decision**: Four independent edits, one per finding, each mappable
to its own user story. No shared refactor needed. Order by severity: #740 →
#741 → #742 → #743. See research.md for the specific approach per finding.

## Complexity Tracking

No constitution violations — section intentionally empty.
