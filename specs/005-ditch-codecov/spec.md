# Feature Specification: Ditch Codecov for a Self-Hosted Coverage Gate

**Feature Branch**: `700-ditch-codecov`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "Migrate the project's CI from Codecov to Hynek's 'ditch Codecov' pattern (GitHub issue #700): remove all Codecov usage and replace it with a single in-CI coverage job that combines per-matrix coverage data, publishes a report to the run summary, and fails the build when total coverage drops below the project's existing threshold."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Coverage gate without a third-party service (Priority: P1)

As a maintainer, when a pull request runs CI, I want total test coverage to be
computed from all Python-version test jobs and enforced against a threshold
entirely within GitHub Actions, so that a drop in coverage blocks the merge
without depending on Codecov.

**Why this priority**: This is the core value of the migration — replacing the
flaky external dependency with a self-contained gate. Without it, the feature
delivers nothing.

**Independent Test**: Open a PR; observe that the test matrix runs, a single
coverage job aggregates results, and the PR is blocked if aggregate coverage is
below the threshold and allowed when it is at or above it.

**Acceptance Scenarios**:

1. **Given** a PR whose aggregate coverage is at or above the threshold, **When** CI runs, **Then** the coverage job succeeds and the branch-protection summary reports success.
2. **Given** a PR whose aggregate coverage is below the threshold, **When** CI runs, **Then** the coverage job fails and the branch-protection summary reports failure, blocking merge.
3. **Given** the test matrix runs across multiple Python versions, **When** the coverage job aggregates results, **Then** the reported total reflects the combined coverage of all matrix jobs, not a single version.

---

### User Story 2 - Visible coverage report on every run (Priority: P2)

As a reviewer, I want a human-readable coverage summary attached to the CI run,
so that I can see the current coverage percentage and which areas are lacking
without leaving GitHub or logging into an external dashboard.

**Why this priority**: Codecov's main day-to-day value was visibility; the
replacement must preserve a readable report or reviewers lose insight.

**Independent Test**: Open any CI run for a PR and confirm a coverage report is
present in the run's summary view.

**Acceptance Scenarios**:

1. **Given** a completed CI run, **When** a reviewer opens the run summary, **Then** a markdown coverage report showing the total percentage is displayed.
2. **Given** the coverage gate fails, **When** a reviewer inspects the run, **Then** a downloadable detailed (HTML) coverage report is available to diagnose the shortfall.
3. **Given** the coverage gate passes, **When** the run completes, **Then** no detailed HTML report artifact is produced (kept only for failures to avoid clutter).

---

### User Story 3 - No residual Codecov footprint (Priority: P3)

As a maintainer, I want every trace of Codecov removed from the project's CI, so
that there are no dead steps, unused secrets references, or purposeless jobs left
behind after the migration.

**Why this priority**: Leftover configuration causes confusion and security
review noise, but it does not block the core gate from working.

**Independent Test**: Search the CI configuration for any Codecov reference and
confirm none remain; confirm the post-merge job that existed only to refresh the
Codecov baseline is gone.

**Acceptance Scenarios**:

1. **Given** the migrated CI configuration, **When** it is searched for Codecov references (action, steps, token), **Then** none are found.
2. **Given** the previous post-merge job existed solely to refresh the external coverage baseline, **When** the migration is complete, **Then** that job no longer exists.

---

### Edge Cases

- **A matrix test job fails or is cancelled**: the coverage job still runs (it must not be skipped by an upstream failure) and reports on whatever coverage data was produced; the overall run still fails because the failing test job fails the branch-protection summary.
- **No coverage data is available** (e.g., all test jobs failed before producing data): the coverage job surfaces a clear failure rather than silently passing.
- **Coverage is exactly at the threshold**: treated as passing (the threshold is inclusive).
- **A new Python version is added to or removed from the matrix**: the coverage job aggregates whatever per-version data artifacts exist without configuration changes tied to specific version numbers.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: CI MUST NOT use Codecov in any form — the Codecov action, its upload steps, and any Codecov token reference MUST be removed.
- **FR-002**: The post-merge job whose sole purpose was refreshing the external coverage baseline MUST be removed.
- **FR-003**: Each per-Python-version test job MUST publish its raw coverage data as a run artifact uniquely identified by that Python version.
- **FR-004**: Coverage data artifacts MUST be captured even though the underlying coverage data files are hidden (dotfile) names.
- **FR-005**: A single coverage-aggregation job MUST run after the test matrix and MUST run even when one or more test jobs fail (so it always reports).
- **FR-006**: The coverage-aggregation job MUST retrieve all per-version coverage data artifacts and combine them into a single aggregate result.
- **FR-007**: The coverage-aggregation job MUST publish a human-readable (markdown) coverage report to the CI run summary.
- **FR-008**: The coverage-aggregation job MUST fail when aggregate coverage is below the project's configured threshold, and MUST pass when it is at or above it.
- **FR-009**: The enforced threshold MUST be the project's existing `[tool.coverage.report] fail_under` value (currently **60**), NOT 100%. The coverage-aggregation job MUST derive the threshold from the project's existing coverage configuration rather than hardcoding a number in the CI definition, so the gate stays in sync if the configured value changes.
- **FR-010**: When and only when the coverage gate fails, the job MUST publish a detailed (HTML) coverage report as a downloadable artifact.
- **FR-011**: The coverage-aggregation job MUST be included in the branch-protection summary job's dependencies and pass/fail evaluation so that it gates merges to the protected branch.
- **FR-012**: All GitHub Actions used MUST remain pinned to specific commit SHAs, and the CI configuration MUST continue to pass the existing GitHub Actions security review (zizmor).
- **FR-013**: Existing non-coverage CI behavior (lint, type-check, security, documentation jobs, and the post-merge early-warning job for the prerelease Python version) MUST remain unchanged.

### Key Entities

- **Per-version coverage data artifact**: the raw coverage measurement produced by one Python-version test job, uniquely named so multiple versions can coexist in one run and later be combined.
- **Aggregate coverage result**: the single combined measurement derived from all per-version artifacts; the basis for both the summary report and the pass/fail gate.
- **Coverage summary report**: the human-readable markdown rendering of the aggregate result, shown in the run summary.
- **Detailed coverage report**: the drill-down (HTML) rendering, retained only on gate failure for diagnosis.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero Codecov references remain anywhere in the CI configuration (verifiable by search returning no matches).
- **SC-002**: On every PR run, reviewers can read the total coverage percentage directly in the CI run summary without visiting any external service.
- **SC-003**: A PR that reduces aggregate coverage below the threshold is blocked from merging by a failing required check.
- **SC-004**: A PR at or above the threshold merges without any coverage-related failure.
- **SC-005**: The reported coverage percentage reflects all Python versions in the matrix combined, and changes appropriately when a version's tests contribute more or less coverage.
- **SC-006**: The CI security review passes with no new findings introduced by the migration.
- **SC-007**: On a failing-coverage run, a detailed report artifact is downloadable; on a passing run, it is absent.

## Assumptions

- The project's test tooling already records coverage in a combinable form across parallel runs, so aggregating per-version data yields a correct total.
- The aggregate gate is governed by `[tool.coverage.report] fail_under = 60`; the coverage tool reads this from the project's configuration, so the CI job does not restate the number. The separate pytest per-run `--cov-fail-under=50` stays as-is (it guards each local/CI test run; the aggregate gate is the stricter 60).
- The migration is limited to the coverage/Codecov concern; unrelated CI jobs and their triggers are out of scope and remain as-is.
- Branch protection is configured to require the summary check, so adding the coverage job to that summary is sufficient to gate merges (no separate repository-settings change is required as part of this feature).
- Publishing coverage on pull-request runs is sufficient; refreshing a default-branch baseline is no longer needed once the external service is removed.
