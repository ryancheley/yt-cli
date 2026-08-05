# Implementation Plan: Listing comments for issues with no comments

**Branch**: `006-fix-empty-comments-768` | **Date**: 2026-08-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-fix-empty-comments/spec.md`

## Summary

`yt issues comments list` calls `asyncio.run(issue_manager.list_comments(issue_id))` **once per issue inside a Python `for` loop** (`youtrack_cli/commands/issues.py:1392-1396`). Each `asyncio.run()` creates and tears down its own event loop. The project's HTTP layer keeps a **global** `httpx.AsyncClient` singleton (`youtrack_cli/client.py` `HTTPClientManager._ensure_client`) that is only recreated when `is_closed` — it has no event-loop affinity check. From the second issue onward the cached client (and its keep-alive connection pool, bound to the first, now-closed loop) is reused on a fresh loop; when httpx tears down a pooled connection it calls into the dead loop → `RuntimeError: Event loop is closed`. It surfaced on a no-comment issue because that response is where the pooled connection happened to be closed, but the trigger is the multi-`asyncio.run` batch, not the comment count.

**Approach**: Give the shared HTTP client **event-loop affinity**. `_ensure_client` records the loop its client/lock were created on; when it runs on a different running loop (a later `asyncio.run()`), it drops the stale client and recreates the client **and** its `asyncio.Lock` on the current loop. Every network call routes through `_ensure_client`, so this one guard fixes the reported bug and any future cross-loop reuse, with no change to the command or its output. (A command-level single-`asyncio.run()` rewrite was considered but rejected — it churns the existing comment-list test suite for a larger diff; see research.md.)

## Technical Context

**Language/Version**: Python 3.13 (project targets 3.11+)

**Primary Dependencies**: click, httpx, rich, pydantic

**Storage**: N/A

**Testing**: pytest (real-object preference per constitution); `ty` for type checking; `ruff` for lint/format

**Target Platform**: CLI (cross-platform)

**Project Type**: Single-project CLI

**Performance Goals**: No new network calls; batch shares one event loop (fewer loop setup/teardown cycles than before)

**Constraints**: No new dependencies; preserve existing table/JSON output shape exactly

**Scale/Scope**: One command handler (`list_issue_comments`) plus a regression test and a docs note

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Code Quality**: PASS — change is localized; `ruff` + `ty` run via pre-commit; `docs/` updated in the same change.
- **II. Testing Standards (NON-NEGOTIABLE)**: PASS — a regression test drives `_ensure_client` under two sequential real `asyncio.run()` calls and asserts the client is recreated on the new loop (same object before the fix, distinct after). No mocks; fails before / passes after.
- **III. UX Consistency**: PASS — output (table + JSON) is unchanged; empty comments already render as an empty table via `display_comments_table`. Errors still go to stderr with non-zero exit.
- **IV. Performance**: PASS — same number of API calls; strictly fewer event-loop create/destroy cycles.

No violations → Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/006-fix-empty-comments/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output (validation guide)
├── spec.md
└── checklists/
    └── requirements.md
```

`data-model.md` and `contracts/` are **N/A**: no new data entities and no change to the command's public contract (same args, same table/JSON output).

### Source Code (repository root)

```text
youtrack_cli/
├── client.py            # HTTPClientManager._ensure_client — add event-loop affinity (THE FIX)
├── commands/issues.py   # list_issue_comments (unchanged)
└── managers/issues.py   # list_comments (unchanged)

tests/
└── test_client.py       # regression: client recreated across sequential asyncio.run loops

docs/troubleshooting.rst # note empty-comment listing / prior "Event loop is closed" symptom
```

**Structure Decision**: Single-project CLI. The only production edit is
`youtrack_cli/client.py:HTTPClientManager._ensure_client` (plus a `_client_loop` field in
`__init__`). This is the shared chokepoint all network calls route through, so the guard
fixes every caller at once and leaves the command and existing tests untouched.

## Complexity Tracking

No constitution violations; section intentionally empty.
