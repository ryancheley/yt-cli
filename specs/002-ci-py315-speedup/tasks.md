# Tasks: Speed up the Python 3.15 CI test job

**Feature**: 002-ci-py315-speedup | **Branch**: `ci-py315-speedup-736` | **Issue**: #736

**Input**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [quickstart.md](./quickstart.md)

**Scope note**: This feature changes exactly one file, `.github/workflows/ci.yml`.
There is no application/test code to write; "tests" here are CI-behavior
observations, not `pytest` cases. Tasks are kept minimal per the plan.

## Phase 1: Setup

- [X] T001 Confirm on branch `ci-py315-speedup-736` and that `.github/workflows/ci.yml` is the only target; re-read the `test` job matrix (line ~29) and the push-only `coverage-baseline` job (line ~189) in `.github/workflows/ci.yml` to anchor the two edits.

## Phase 2: Foundational

_None._ No blocking prerequisites — the two user stories touch independent parts
of the same file and can be applied in one pass.

---

## Phase 3: User Story 1 — Faster PR feedback (Priority: P1) 🎯 MVP

**Goal**: Remove the ~90s Python 3.15 long pole from every PR by dropping it from
the per-PR `test` matrix, while keeping stable-version coverage unchanged.

**Independent test**: Open a PR; the `test` matrix shows legs for 3.10–3.14 and
3.14t but **no** `test (3.15)`; slowest test leg ~40–60s; required `test` check
reports success.

- [X] T002 [US1] In `.github/workflows/ci.yml`, remove `"3.15"` from the `test` job's `strategy.matrix.python-version` list (line ~29) so it ends at `"3.14t"`.
- [X] T003 [US1] In `.github/workflows/ci.yml`, update the comment above the matrix (lines ~26–28) to explain that 3.15 was moved to a post-merge job because it is a prerelease with no prebuilt native-extension wheels (source builds cost ~90s), and note the one-line reversal (add `"3.15"` back + delete the post-merge job) once cp315 wheels ship. Keep the existing 3.15t note accurate.

**Checkpoint**: PR runs no longer include a 3.15 leg (satisfies SC-001, SC-002,
SC-004; FR-001, FR-002, FR-005, FR-006, FR-007).

---

## Phase 4: User Story 2 — Preserve early warning for Python 3.15 (Priority: P2)

**Goal**: Keep exercising Python 3.15 on every push to `main` so 3.15-specific
breakage is still detected off the PR critical path.

**Independent test**: After a merge to `main`, a `test-py315` job runs on the
push and executes the suite on Python 3.15; a 3.15-only break shows the job red.

- [X] T004 [US2] In `.github/workflows/ci.yml`, add a new job `test-py315` gated on `if: github.event_name == 'push'`, mirroring the `coverage-baseline` job's steps (checkout with `persist-credentials: false`, `astral-sh/setup-uv` with cache, `actions/setup-python` with `python-version: "3.15"` and `allow-prereleases: true`), running `uvx --with tox-uv tox -e py315`. Reuse the exact pinned action SHAs already in the file. Add a short comment stating this is the post-merge 3.15 early-warning run (see US1 comment for reversal).

**Checkpoint**: 3.15 runs on every push to `main` (satisfies SC-003; FR-003,
FR-004).

---

## Phase 5: Polish & Validation

- [X] T005 Run `uvx zizmor .github/workflows/` and confirm no new findings for the added job (constitution: GitHub Actions security gate must stay clean).
- [X] T006 Run the local checks from [quickstart.md](./quickstart.md) (grep assertions that 3.15 is gone from the matrix and that a `tox -e py315` push job exists); confirm YAML is well-formed.
- [X] T007 Review `docs/` and `README.md` for any statement about the CI Python-version matrix that names 3.15 as a per-PR version; update if present (per constitution: docs updated with the change). If none exists, note "no doc reference" in the PR.

---

## Dependencies

- **T001** (setup) before all.
- **US1 (T002–T003)** and **US2 (T004)** are independent edits to the same file;
  do US1 first (MVP) then US2, or both together.
- **Phase 5 (T005–T007)** after US1 and US2 are applied.

## Parallel opportunities

Minimal — all edits are in one file, so they are applied sequentially to avoid
conflicting edits. T005, T006, T007 (validation/docs) are independent of each
other and can be done in any order once the edits land. [P] not marked because
the edit tasks share `ci.yml`.

## Implementation strategy

- **MVP = User Story 1** (T002–T003): removing 3.15 from the per-PR matrix alone
  delivers the entire performance win the issue asks for. If US2 were deferred,
  the only loss is 3.15 early-warning coverage.
- **Full delivery**: US1 + US2 + Phase 5 — the intended scope, matching the
  clarified decision (post-merge on `main`, no cron, no per-PR caching).
