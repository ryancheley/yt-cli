# Quickstart / Validation Guide: Python 3.15 CI cadence change

**Feature**: 002-ci-py315-speedup

This change is entirely in `.github/workflows/ci.yml`. Validate it by inspecting
the workflow locally and observing CI behavior on a PR and on `main`.

## Prerequisites

- `uv` installed (repo already uses it).
- On the feature branch `ci-py315-speedup-736`.

## Local validation (before pushing)

1. **Workflow security lint** (constitution: zizmor must stay clean):
   ```sh
   uvx zizmor .github/workflows/
   ```
   Expected: no new findings.

2. **YAML sanity** — confirm the two edits landed:
   ```sh
   # 3.15 removed from the per-PR test matrix:
   grep -n 'python-version: \["3.10"' .github/workflows/ci.yml   # line should NOT contain "3.15"
   # a push-only 3.15 job exists running tox -e py315:
   grep -n 'tox -e py315' .github/workflows/ci.yml
   ```
   Expected: matrix line ends at `"3.14t"`; a `tox -e py315` line exists in a
   `github.event_name == 'push'` job.

3. **Tox env exists** (the job invokes `tox -e py315`):
   ```sh
   uvx --with tox-uv tox -l | grep -x py315 || echo "py315 env resolves from generative config"
   ```
   Note: envs are generated from the version list in `tox.ini`/`pyproject.toml`;
   `tox -e py315` works as long as 3.15 is a declared env (it already is, since
   the per-PR job invoked `py315` before this change).

## CI validation (after pushing)

- **On the PR** (SC-001, SC-002): the `test` matrix shows legs for
  3.10, 3.11, 3.12, 3.13, 3.14, 3.14t — **no** `test (3.15)` leg. The slowest
  test leg finishes in ~40–60s. The required `test` check reports success.
- **After squash-merge to `main`** (SC-003): a `test-py315` job runs on the push
  and executes the suite on Python 3.15. A green run confirms 3.15 coverage is
  retained off the PR path. (To prove failure visibility, a deliberate
  3.15-only break would show this job red on `main`.)
- **Required check (SC-004)**: a normal green PR is mergeable; no check is stuck
  "expected" waiting on a job that no longer runs.

## Reversal (when cp315 wheels ship upstream)

1. Add `"3.15"` back to the `test` job matrix `python-version` list.
2. Delete the `test-py315` push-only job.
3. Update the matrix comment. Re-run `uvx zizmor .github/workflows/`.
