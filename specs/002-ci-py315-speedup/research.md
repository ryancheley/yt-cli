# Phase 0 Research: Speed up the Python 3.15 CI test job

**Feature**: 002-ci-py315-speedup | **Date**: 2026-07-08

## R1. Root cause of the ~137s 3.15 job

**Decision**: Treat the slowness as dependency source-builds under the 3.15
prerelease, not test execution.

**Rationale**: The test suite runs in <2s locally; the ~90s gap between 3.15
(~137s) and stable versions (~40–55s) is install/build time. Python 3.15 is a
prerelease, so native-extension dependencies (e.g. `cryptography`,
`pydantic-core`) have no prebuilt cp315 wheels on PyPI yet and are compiled from
source under `tox-uv`. Stable versions download prebuilt wheels. The workflow
already carries a note that `cryptography` lacks free-threaded 3.15 wheels,
corroborating the wheel-gap theory.

**Alternatives considered**: Slow test execution (ruled out — <2s locally);
`setup-uv` cache miss as sole cause (contributing, but source builds dominate;
even a warm cache re-pays compilation on resolver differences for a prerelease).

## R2. Mechanism to remove 3.15 from the PR critical path

**Decision**: Drop `3.15` from the per-PR `test` matrix and run a dedicated
Python 3.15 job on pushes to `main` (post squash-merge). (Confirmed in spec
Clarifications, 2026-07-08.)

**Rationale**: Smallest, most reversible change that fully removes the long
pole. 3.14 (newest stable) already exercises the newest stable Python behavior
on every PR, so per-PR 3.15 gives no extra correctness confidence. Running 3.15
on every merge to `main` preserves early-warning coverage: any 3.15-specific
break surfaces as a failed run on `main`.

**Alternatives considered**:
- *Cache the built native-extension env per-PR*: keeps per-PR 3.15 but is
  cache-key fragile, still cold-builds on cache miss / upstream churn, and adds
  config complexity. Rejected per clarification.
- *Add a scheduled/cron 3.15 run*: more coverage, but post-merge-on-`main`
  already runs on every merge; a cron adds config for marginal benefit.
  Rejected per clarification.
- *Drop 3.15 entirely*: loses the early-warning signal. Rejected.

## R3. Branch-protection / required-check safety

**Decision**: No branch-protection change is required.

**Rationale**: Verified via `gh api .../branches/main/protection` that the
required status checks are `test`, `lint`, `type-check`, `security`. The `test`
context is the **summary** job `tests-complete` (`name: test`), which aggregates
`needs: [test, lint, type-check, security, documentation]` — it does **not**
name individual matrix legs like `test (3.15)`. Removing `3.15` from the matrix
therefore leaves the `test` required check intact and still reporting on PRs.
This satisfies FR-005 with no GitHub settings edit. (The summary-gate pattern
was designed precisely so matrix changes don't break required checks.)

## R4. Where the post-merge 3.15 job lives

**Decision**: Add a new job gated on `if: github.event_name == 'push'` that runs
`uvx --with tox-uv tox -e py315`, mirroring the existing `coverage-baseline`
push-only job's setup steps.

**Rationale**: `coverage-baseline` already establishes the "runs only on push to
`main`/`develop`, sets up uv + Python, runs tox" pattern. A sibling job reuses
that pattern verbatim with `python-version: "3.15"` + `allow-prereleases: true`
and `tox -e py315`. Keeping it a separate job (not folding 3.15 into
`coverage-baseline`'s matrix) avoids double Codecov uploads and keeps the
concern — "3.15 early warning" — clearly named and independently reversible.

**Alternatives considered**: Add `python-version` matrix to `coverage-baseline`
(would upload coverage twice and conflate coverage-baseline with 3.15 smoke
testing — rejected for clarity).

## R5. Reversibility when cp315 wheels ship

**Decision**: Record, in the workflow comments, that 3.15 lives in a post-merge
job and how to fold it back: add `"3.15"` to the `test` matrix and delete the
post-merge job.

**Rationale**: FR-006/FR-007 — a future maintainer should be able to undo this
in one obvious edit once prebuilt wheels make 3.15 as fast as stable versions.
