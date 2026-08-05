# Tasks: Listing comments for issues with no comments (#768)

**Feature**: `006-fix-empty-comments` | **Branch**: `006-fix-empty-comments-768`
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

**Fix**: Add event-loop affinity to `HTTPClientManager._ensure_client` so the shared httpx
client is recreated (with a fresh lock) when reused on a different event loop — the true
cause of the "Event loop is closed" error when `yt issues comments list` calls
`asyncio.run()` once per issue.

## Phase 1: Setup

*(No setup tasks — existing project, no new dependencies.)*

## Phase 2: Foundational

*(No blocking prerequisites — single localized fix.)*

## Phase 3: User Story 1 & 2 — Empty-comment listing works, single and batched (Priority: P1)

**Goal**: Listing comments for issues with zero comments succeeds — for one issue and for a
batch of issue IDs from stdin — with no "Event loop is closed" error.

**Independent test**: Run the regression test (fails on `main`, passes after fix); manually
run `printf 'A\nB\n' | yt issues comments list` where one of A/B has no comments and confirm
exit 0 with no traceback.

- [X] T001 [US1] Add a failing regression test in `tests/test_client.py` (in
  `TestHTTPClientManager`): construct one `HTTPClientManager`, call
  `asyncio.run(manager._ensure_client())` twice, and assert the two returned clients are
  **distinct objects** (`c1 is not c2`) — i.e. the client is rebound to the new event loop.
  Confirm it FAILS against current code (returns the same object).
- [X] T002 [US1] In `youtrack_cli/client.py` `HTTPClientManager.__init__`, add
  `self._client_loop: asyncio.AbstractEventLoop | None = None` next to `self._client`.
- [X] T003 [US1] In `youtrack_cli/client.py` `HTTPClientManager._ensure_client`, before the
  existing `is None / is_closed` check, get the running loop
  (`asyncio.get_running_loop()`); if it differs from `self._client_loop`, drop the stale
  client (`self._client = None`), create a fresh `self._lock = asyncio.Lock()`, and set
  `self._client_loop` to the running loop. Add a `ponytail:` comment noting the abandoned
  dead-loop client's connections are inert for a short-lived CLI. Confirm T001 now PASSES.
- [X] T004 [US1] Run the full comment-list command test suite
  (`uv run pytest tests/test_issues.py -k comments_list -q`) and confirm **no regressions**
  (the fix does not touch the command; all existing assertions still pass).

## Phase 4: Polish & Cross-Cutting

- [X] T005 Add a short note to `docs/troubleshooting.rst` that listing comments for issues
  with no comments (including batches piped via stdin) now succeeds, resolving the prior
  "Event loop is closed" error.
- [X] T006 Write the implementation plan to `scratch/issue-768.md` (per project workflow).
- [X] T007 Run gates: `uv run pre-commit run --all-files`, `uv run ty check`,
  `uv run pytest -q`. All must pass with no bypass.

## Dependencies

- T001 (failing test) → T002 → T003 (fix, makes T001 pass) → T004 (no regressions).
- T005–T007 after the fix is green. T007 is the final gate before PR.

## Parallel opportunities

- T005 (docs) and T006 (scratch plan) are independent of each other and of the code fix —
  can be done in parallel `[P]` once T003 lands.

## Implementation strategy (MVP)

MVP = T001→T004: the regression test plus the `_ensure_client` guard. That alone satisfies
all functional requirements (FR-001…FR-006) and success criteria (SC-001…SC-004). T005–T007
are finishing/compliance steps.
