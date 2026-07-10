# Quickstart / Validation Guide: Security fixes #740–#743

**Feature**: 003-security-fixes

## Prerequisites

- `uv` installed; on branch `security-fixes-740-743`.

## Automated validation

```sh
# Full suite incl. new regression tests for #740/#741/#742
uv run pytest -q

# Lint + types (constitution gates)
uv run ruff check .
uv run ruff format --check .
uv run ty
```

Expected: all green, including the three new regression tests. Each new test
fails on `main` (pre-fix) and passes on this branch.

## Manual spot-checks

### #740 — attachment path traversal
- With a server/attachment whose filename contains `../`, run
  `yt articles attach download <article> <attachment>` (no `--output`).
- Expected: file saved in the current directory under the bare name; nothing
  written to a parent directory. A normal filename (`report.pdf`) is unchanged.

### #741 — cleartext base URL warning
- `yt auth login --base-url http://localhost:8080 --token <t>` (or verify).
- Expected: a visible warning on stderr that the token will be sent over
  cleartext HTTP; the command still proceeds. `https://` shows no warning.

### #742 — tutorial executor no shell
- Run a tutorial and execute a step's example command.
- Expected: command runs and output shows, as before. Internally the executor
  uses `create_subprocess_exec` (no shell); shell metacharacters in a command
  string are treated as literal args (no secondary command runs).

### #743 — security policy
- Confirm `SECURITY.md` exists at repo root and documents a private reporting
  channel, response expectations, and supported versions. On GitHub it appears
  under the Security tab / "Report a vulnerability".

## Reference

Approach and rationale per finding: [research.md](./research.md). Requirements
and acceptance scenarios: [spec.md](./spec.md).
