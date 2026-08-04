# Implementation Plan: Ditch Codecov for a Self-Hosted Coverage Gate

**Branch**: `700-ditch-codecov` | **Date**: 2026-08-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-ditch-codecov/spec.md`

## Summary

Remove Codecov from `.github/workflows/ci.yml` and replace it with an in-CI
coverage gate. Each per-Python-version `test` job renames its `.coverage` data
to a unique `.coverage.<version>` and uploads it as a hidden-file artifact
`coverage-data-<version>`. A new `coverage` job (`needs: test`, `if: always()`)
downloads all `coverage-data-*` artifacts (`merge-multiple`), runs
`coverage combine`, writes a markdown report to `$GITHUB_STEP_SUMMARY`, and fails
if aggregate coverage is below `[tool.coverage.report] fail_under = 60` (read from
`pyproject.toml`, not hardcoded). On failure it uploads the HTML report. The
`coverage` job is added to the `tests-complete` summary so branch protection gates
on it. The post-merge `coverage-baseline` job (existed only to feed Codecov) is
deleted. All actions stay SHA-pinned; the change must pass `zizmor`.

## Technical Context

**Language/Version**: GitHub Actions workflow YAML; coverage tooling is Python
`coverage`/`pytest-cov` (coverage 7.x, pinned in `uv.lock`).

**Primary Dependencies**: `actions/checkout@v4`, `astral-sh/setup-uv@v4`,
`actions/upload-artifact@v7.0.1`, `actions/download-artifact@v8.0.1`, `uv tool
install coverage`, `tox`/`tox-uv`.

**Storage**: GitHub Actions run artifacts (per-version coverage data; HTML report
on failure). No persistent storage.

**Testing**: Validation is by CI behavior — a green run at/above threshold and a
red `coverage` job below threshold. Local dry-run via `act` optional; primary
verification is the PR's own CI plus `zizmor`.

**Target Platform**: `ubuntu-latest` GitHub-hosted runners.

**Project Type**: CLI project; this feature touches CI configuration only.

**Performance Goals**: Coverage job adds ~1 short job after the matrix; no impact
on the critical path beyond one extra sequential job that runs coverage combine
(seconds).

**Constraints**: All actions SHA-pinned; `checkout` with
`persist-credentials: false`; must pass `zizmor .github/workflows/`; threshold not
hardcoded (derived from `pyproject.toml`).

**Scale/Scope**: One workflow file (`ci.yml`); matrix of 6 Python versions
(`3.10, 3.11, 3.12, 3.13, 3.14, 3.14t`).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Code Quality**: No application code changes. Docs: no `docs/` user-facing
  change needed (CI-internal), but the repo README/badges must not reference
  Codecov after removal — checked in tasks. `uv` remains the toolchain. ✅
- **II. Testing Standards (NON-NEGOTIABLE)**: No test code changes; the feature
  *is* a test/coverage gate. `zizmor` (GitHub Actions review) must pass — an
  explicit acceptance item. The gate must not weaken existing enforcement. ✅
- **III. UX Consistency**: Reviewer-facing coverage visibility is preserved via
  the run-summary markdown report (replaces the Codecov PR comment/dashboard). ✅
- **IV. Performance**: Negligible CI time change; no runtime impact. ✅

No violations. Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/005-ditch-codecov/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (jobs/artifacts entities)
├── quickstart.md        # Phase 1 output (how to validate)
├── contracts/
│   └── ci-coverage.md   # Phase 1 output (job graph + artifact contract)
├── spec.md
└── tasks.md             # /speckit-tasks output (not created here)
```

### Source Code (repository root)

```text
.github/workflows/
└── ci.yml               # Only file changed: edit `test` job, add `coverage`
                         # job, update `tests-complete`, delete `coverage-baseline`

pyproject.toml           # Read-only here: [tool.coverage.report] fail_under = 60
                         # supplies the threshold; [tool.coverage.run] parallel = true
README.md                # Remove any Codecov badge/reference (verify)
```

**Structure Decision**: Single-file CI change plus a badge/reference sweep. No
new source modules. `pyproject.toml` is the source of truth for the threshold and
is not modified.

## Complexity Tracking

> No Constitution Check violations — section intentionally empty.
