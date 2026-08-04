# Tasks: Ditch Codecov for a Self-Hosted Coverage Gate

**Feature**: `specs/005-ditch-codecov` | **Branch**: `700-ditch-codecov`
**Inputs**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/ci-coverage.md](./contracts/ci-coverage.md), [quickstart.md](./quickstart.md)

Tests: No unit-test tasks — this is CI configuration. Verification is by `zizmor`,
local combine mechanics, and the PR's own CI run (see quickstart).

**Note on parallelism**: nearly every task edits the single file
`.github/workflows/ci.yml`, so `[P]` is rare — sequential edits to one file are not
parallelizable. Tasks touching other files (README sweep, CHANGELOG) are marked
`[P]`.

## Phase 1: Setup

- [X] T001 Confirm working branch is `700-ditch-codecov` and read the current `.github/workflows/ci.yml` `test`, `coverage-baseline`, and `tests-complete` jobs to anchor edits.
- [X] T002 Confirm the threshold source of truth: `grep -n "fail_under" pyproject.toml` shows `[tool.coverage.report] fail_under = 60`; confirm `[tool.coverage.run] parallel = true` is present.

## Phase 2: Foundational (blocking prerequisites)

- [X] T003 Verify current SHA pins to use in `.github/workflows/ci.yml`: `actions/upload-artifact` → `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` (v7.0.1) and `actions/download-artifact` → `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` (v8.0.1); reuse existing repo pins for `actions/checkout` (v4) and `astral-sh/setup-uv` (v4). (Source: research R3.)
- [X] T004 Validate combine mechanics locally per quickstart §1: produce two `.coverage.<x>` files, `coverage combine`, `coverage report` — confirm combine merges and `coverage report` exits non-zero when under `fail_under=60` (proves threshold-from-config). Clean up `.coverage*` afterward.

## Phase 3: User Story 1 — Coverage gate without a third-party service (P1) 🎯 MVP

**Goal**: Aggregate coverage across the matrix is computed and enforced against
the threshold entirely in GitHub Actions; below-threshold PRs are blocked.

**Independent test**: Open the PR; the test matrix runs, the `coverage` job
aggregates all versions, and the `test` required check is red when aggregate < 60
and green when ≥ 60.

- [X] T005 [US1] In the `test` job of `.github/workflows/ci.yml`, remove the "Upload coverage to Codecov" step (the `codecov/codecov-action` step and its `CODECOV_TOKEN` env). (FR-001)
- [X] T006 [US1] In the `test` job, after the tox test step, add a step to rename the data file: `mv .coverage ".coverage.${{ matrix.python-version }}"`. (data-model: per-version artifact; research R1)
- [X] T007 [US1] In the `test` job, add an `actions/upload-artifact` step (v7.0.1 SHA) with `name: coverage-data-${{ matrix.python-version }}`, `path: .coverage.${{ matrix.python-version }}`, and `include-hidden-files: true`. (FR-003, FR-004; research R2)
- [X] T008 [US1] Add a new `coverage` job to `.github/workflows/ci.yml` with `name: coverage`, `needs: [test]`, `if: always() && github.event_name == 'pull_request'`, `runs-on: ubuntu-latest`; steps: `actions/checkout` (repo v4 SHA, `persist-credentials: false`) and `astral-sh/setup-uv` (repo v4 SHA). (FR-005; contract)
- [X] T009 [US1] In the `coverage` job, add an `actions/download-artifact` step (v8.0.1 SHA) with `pattern: coverage-data-*` and `merge-multiple: true`. (FR-006)
- [X] T010 [US1] In the `coverage` job, add the gate `run:` block: `uv tool install coverage`; `coverage combine`; then the enforcing `coverage report` (bare — threshold from `pyproject.toml`, NOT hardcoded). (FR-008, FR-009; research R4)
- [X] T011 [US1] Add `coverage` to the `tests-complete` job `needs:` list and add `COVERAGE_RESULT: ${{ needs.coverage.result }}` to its env, requiring `"$COVERAGE_RESULT" == "success"` in the pass/fail check. (FR-011; contract)

**Checkpoint**: US1 delivers the MVP — a working, merge-gating aggregate coverage
check with no Codecov. (US2/US3 add visibility and cleanup.)

## Phase 4: User Story 2 — Visible coverage report on every run (P2)

**Goal**: A readable coverage report is attached to every CI run; a detailed HTML
report is available only when the gate fails.

**Independent test**: Open a CI run's Summary → a markdown coverage table is shown;
on a failing run an `html-report` artifact is downloadable, on a passing run it is
absent.

- [X] T012 [US2] In the `coverage` job `run:` block (before the enforcing report), add `coverage html --skip-covered --skip-empty` and `coverage report --format=markdown >> "$GITHUB_STEP_SUMMARY" || true` so the summary is always written even when the gate later fails. (FR-007; research R4)
- [X] T013 [US2] In the `coverage` job, add a final `actions/upload-artifact` step (v7.0.1 SHA) guarded by `if: failure()` with `name: html-report` and `path: htmlcov` (uploads the detailed report only on gate failure). (FR-010)

**Checkpoint**: US2 complete — reviewers get run-summary visibility and
failure-only HTML drill-down.

## Phase 5: User Story 3 — No residual Codecov footprint (P3)

**Goal**: Every trace of Codecov is gone, including the purposeless post-merge job.

**Independent test**: `grep -ri codecov .github README.md` returns nothing; the
`coverage-baseline` job no longer exists.

- [X] T014 [US3] Delete the entire `coverage-baseline` job from `.github/workflows/ci.yml` (it existed only to refresh the Codecov baseline). Leave the `test-py315` push job untouched. (FR-002; research R8)
- [X] T015 [P] [US3] Sweep for stray Codecov references in functional files: confirm `README.md` has no Codecov badge and remove it if present. Do NOT touch historical mentions in `CHANGELOG.md` or old specs. (FR-001; research R9)

**Checkpoint**: US3 complete — no functional Codecov footprint remains.

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T016 Run `uvx zizmor .github/workflows/` and confirm no new findings; confirm every `uses:` in `ci.yml` is a full SHA with a `# vX` comment and `checkout` uses `persist-credentials: false`. (FR-012)
- [X] T017 [P] Add a `CHANGELOG.md` entry under the appropriate version noting the migration from Codecov to an in-CI coverage gate.
- [X] T018 Verify SC-001 (`grep -ri codecov .github README.md` → empty) and FR-013 (lint, type-check, security, documentation, and `test-py315` jobs are byte-for-byte unchanged aside from the intended edits) via `git diff`.
- [ ] T019 Push the branch, open the PR, and validate on the live run per quickstart §2 (per-version artifacts exist, `coverage` job combines + summarizes + gates green, no `html-report` on green, `test` required check green). Post-merge, confirm `coverage-baseline` no longer runs on push (quickstart §4).

## Dependencies & Execution Order

- **Setup (T001–T002)** → **Foundational (T003–T004)** → **US1 (T005–T011)** → **US2 (T012–T013)** → **US3 (T014–T015)** → **Polish (T016–T019)**.
- US1 is the MVP and must land first; US2 extends the same `coverage` job; US3 is independent cleanup and could technically be done in parallel with US2 but touches the same file, so keep sequential.
- T004 (local mechanics) should pass before writing the `coverage` job (T008–T010).
- T015 and T017 touch files other than `ci.yml` → marked `[P]`.

## Parallel Opportunities

- Limited: the core edits all live in `.github/workflows/ci.yml` (sequential).
- `[P]` tasks: **T015** (README sweep) and **T017** (CHANGELOG entry) can run
  alongside the `ci.yml` edits since they touch different files.

## Implementation Strategy

1. **MVP first**: complete Phase 1–3 (US1) → a functioning, merge-gating coverage
   check with Codecov removed from the `test` job. This alone closes the core of
   issue #700.
2. **Increment**: add US2 (visibility) then US3 (cleanup).
3. **Validate**: Polish phase runs `zizmor`, checks the diff scope, and confirms
   behavior on the live PR run.
