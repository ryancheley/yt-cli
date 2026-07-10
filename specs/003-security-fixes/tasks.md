# Tasks: Remediate four security findings (#740–#743)

**Feature**: 003-security-fixes | **Branch**: `security-fixes-740-743`

**Input**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [quickstart.md](./quickstart.md)

**Note**: The four user stories are independent (different files) and can be done
in any order or in parallel. Tests are REQUIRED (constitution II): each
behavioral fix ships a regression test that fails before and passes after.

## Phase 1: Setup

- [X] T001 Confirm branch `security-fixes-740-743`; read the current code at the three sites to anchor edits: `youtrack_cli/commands/articles.py` (download, ~L1391-1405), `youtrack_cli/auth.py` (`verify_credentials`, ~L375-423), `youtrack_cli/tutorial/executor.py` (~L87-89, L157-183) and `youtrack_cli/tutorial/core.py` (`_execute_command`, ~L357-384).

## Phase 2: Foundational

_None._ No shared prerequisite; each story is self-contained.

---

## Phase 3: User Story 1 — Safe attachment download (#740, Priority: P1) 🎯 MVP

**Goal**: Sanitize the server-supplied attachment filename so a malicious
filename cannot write outside the working directory.

**Independent test**: Download with a server filename of `../../pwned`; file
lands at `<cwd>/pwned`, nothing written outside.

- [X] T002 [P] [US1] Add a regression test in `tests/test_articles.py` (new test class/functions) that invokes the article `attach download` command with the remote boundary (`ArticleManager.download_attachment`) returning `filename="../../pwned"` and no `--output`, using `tmp_path` as cwd; assert the file is written to `tmp_path/pwned` and NOT to `tmp_path.parent`. Add a second case for an absolute filename (`/tmp/evil`) and a normal filename (`report.pdf`, unchanged). Test must FAIL before T003.
- [X] T003 [US1] In `youtrack_cli/commands/articles.py` download command, replace the no-`--output` branch `output_path = Path(filename)` with a sanitized name: `safe = Path(filename).name; output_path = Path(safe) if safe and safe not in (".", "..") else Path(f"attachment_{attachment_id}")`. Leave the explicit `--output` branch unchanged. Re-run T002 → passes.

**Checkpoint**: #740 fixed (SC-001; FR-001, FR-002).

---

## Phase 4: User Story 2 — Cleartext base URL warning (#741, Priority: P2)

**Goal**: Warn (stderr) before sending the token to an `http://` base URL;
proceed anyway (warn-only).

**Independent test**: `warn_if_insecure_url("http://x")` emits a warning;
`https://x` emits none.

- [X] T004 [P] [US2] Add a regression test in `tests/test_auth.py` that calls the new `warn_if_insecure_url` helper (or `verify_credentials` path) with an `http://` base URL and asserts a cleartext warning is emitted (capture console/stderr), and asserts NO warning for an `https://` URL. Test must FAIL before T005.
- [X] T005 [US2] In `youtrack_cli/auth.py`, add `warn_if_insecure_url(base_url: str) -> None` that uses `urllib.parse.urlparse` and, when scheme == "http", prints a Rich-styled warning to stderr that the API token will be sent in cleartext. Call it near the start of `verify_credentials()` (before the request). Warn-only; do not block. Re-run T004 → passes.

**Checkpoint**: #741 fixed (SC-002; FR-003, FR-004).

---

## Phase 5: User Story 3 — Tutorial executor without a shell (#742, Priority: P3)

**Goal**: Execute tutorial example commands via `create_subprocess_exec` (argv),
not `create_subprocess_shell(shell=True)`; remove the dead shell path.

**Independent test**: Executing a command containing `;`/`&&` produces no
secondary effect (sentinel file not created).

- [X] T006 [P] [US3] Add a regression test in `tests/tutorial/` (e.g. `test_executor.py`) that runs `ClickCommandExecutor` against a command whose string contains a shell metacharacter payload attempting to create a sentinel file in `tmp_path` (e.g. `yt --version; touch pwned`), and asserts the sentinel file is NOT created (no shell interpretation). Test must FAIL before T007 (with shell=True the sentinel would appear).
- [X] T007 [US3] In `youtrack_cli/tutorial/executor.py`, change `_execute_via_subprocess` to build argv via the existing `parse_command()` and call `asyncio.create_subprocess_exec("yt", *args, stdout=PIPE, stderr=PIPE, env=env)` instead of `create_subprocess_shell(..., shell=True)`. Keep `is_command_allowed` as a UX filter (add a comment that it is no longer the security boundary). Re-run T006 → passes.
- [X] T008 [US3] In `youtrack_cli/tutorial/core.py`, verify `_execute_command` (the `shell=True` path, ~L357-384) is unused (`grep -rn "_execute_command" youtrack_cli/`); if unused, delete it; if used, convert it to `create_subprocess_exec` the same way. Ensure no remaining `shell=True` in `youtrack_cli/tutorial/`.

**Checkpoint**: #742 fixed (SC-003; FR-005, FR-006, FR-007).

---

## Phase 6: User Story 4 — Security disclosure policy (#743, Priority: P4)

**Goal**: Add a discoverable vulnerability disclosure policy.

**Independent test**: `SECURITY.md` exists at repo root with a private reporting
channel, response expectations, and supported versions.

- [X] T009 [P] [US4] Create `SECURITY.md` at repo root: private reporting channel (GitHub Private Vulnerability Reporting and/or maintainer contact), expected response time and coordinated-disclosure window, and a Supported Versions statement. Reference enabling GitHub Private Vulnerability Reporting in repo settings.

**Checkpoint**: #743 fixed (SC-004; FR-008).

---

## Phase 7: Polish & Validation

- [X] T010 Run `uv run pytest -q` (all green incl. new tests), `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty` (constitution gates). Fix any lint/type issues introduced.
- [X] T011 Review `docs/` for any article-download or auth pages that should mention the sanitized filename behavior or the cleartext warning; update if present (constitution: docs updated with change). If none apply, note "no doc change needed".
- [X] T012 Run `git grep -n "shell=True" youtrack_cli/` to confirm no residual shell execution remains in the tutorial package.

---

## Dependencies

- **T001** before all.
- Within each story, the test precedes its implementation (TDD): T002→T003,
  T004→T005, T006→T007→T008.
- **US1–US4 are mutually independent** (different files) and may proceed in
  parallel.
- **Phase 7 (T010–T012)** after all stories.

## Parallel opportunities

- The four test-writing tasks (T002, T004, T006, T009) touch different files and
  are all `[P]` — can be written together.
- The four stories can each be implemented independently; only Phase 7
  validation must wait for all.

## Implementation strategy

- **MVP = User Story 1 (#740)**: the highest-severity, remotely-influenced
  file-write fix. Delivers the most security value alone.
- **Full delivery**: all four stories + Phase 7. Each maps 1:1 to a GitHub
  issue (#740–#743) for clean traceability in the PR.
