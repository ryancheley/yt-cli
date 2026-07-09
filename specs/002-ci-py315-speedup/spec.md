# Feature Specification: Speed up the Python 3.15 CI test job

**Feature Branch**: `ci-py315-speedup-736`

**Created**: 2026-07-08

**Status**: Draft

**Input**: User description: "CI: Python 3.15 test job is ~3x slower (~137s vs ~45s) than other matrix versions and is the long pole on every PR (issue #736). The 3.15 prerelease likely builds native-extension deps from source because no prebuilt wheels exist yet. Goal: reduce the wall-clock cost 3.15 adds to every PR's critical path without losing meaningful test coverage."

## Clarifications

### Session 2026-07-08

- Q: How should Python 3.15 be handled to remove it from the per-PR critical
  path? → A: Post-merge on `main` — drop 3.15 from the per-PR matrix and run it
  as a job on pushes to `main` (after squash-merge). Smallest reversible change;
  no scheduled/cron run and no per-PR build caching.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Faster PR feedback (Priority: P1)

A contributor opens a pull request. They wait for the CI test matrix to go
green before merging. Today the Python 3.15 job takes ~137s while every other
version finishes in ~40–55s, so 3.15 is the long pole and dictates how long the
contributor waits for the test gate.

**Why this priority**: This is the entire point of the issue — the 3.15 job
adds ~1.5 minutes to the critical path of every PR with no added coverage
benefit (3.14 already exercises the newest stable Python behavior).

**Independent Test**: Open a PR and observe the CI run. The test gate's
wall-clock time (slowest matrix job) is materially lower than the current
~137s, and coverage for supported stable Python versions is unchanged.

**Acceptance Scenarios**:

1. **Given** a PR is opened, **When** the CI test gate runs, **Then** the
   slowest test job completes in a time comparable to the other versions
   (not ~3x slower).
2. **Given** the CI test gate passes, **When** a maintainer reviews coverage,
   **Then** coverage across supported stable Python versions (3.10–3.14) is
   unchanged from before this change.

---

### User Story 2 - Preserve early warning for Python 3.15 (Priority: P2)

A maintainer wants to keep learning early whether the project works on the
in-development Python 3.15, so upgrades aren't a surprise when 3.15 ships — but
without paying that cost on every single PR.

**Why this priority**: Dropping 3.15 entirely would remove a useful early
signal. The value is in keeping the signal while moving its cost off the
per-PR hot path.

**Independent Test**: Confirm that Python 3.15 is still exercised by CI on some
cadence (e.g. on `main` and/or on a schedule), and that a 3.15-specific
failure is still surfaced to maintainers.

**Acceptance Scenarios**:

1. **Given** the project's code breaks specifically on Python 3.15, **When**
   the reduced-cadence 3.15 job runs, **Then** the failure is visible to
   maintainers (a failed run they can see).
2. **Given** a normal PR with no 3.15-specific breakage, **When** CI runs,
   **Then** the contributor is not blocked waiting on the slow 3.15 build.

---

### Edge Cases

- **What happens when upstream ships prebuilt 3.15 wheels?** The change must
  not make it harder to fold 3.15 back into the fast per-PR matrix later; the
  reduced cadence (if chosen) is reversible with a small edit.
- **What happens when the 3.15 job fails on a scheduled/main run?** Maintainers
  must be able to see the failure; it must not silently pass or be hidden.
- **What happens when 3.15 is a genuine required check today?** Branch
  protection / required-check configuration must not be left pointing at a job
  name that no longer runs on PRs (which would block every PR indefinitely).
- **What happens to the free-threaded 3.15t note already in the workflow?** The
  existing comment explaining why 3.15t is omitted must remain accurate.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CI configuration MUST reduce the wall-clock time that Python
  3.15 testing adds to the critical path of an individual pull request.
- **FR-002**: The CI configuration MUST continue to test the project against
  all currently-supported stable Python versions (3.10 through 3.14, including
  the 3.14 free-threaded variant) on every pull request, with unchanged
  coverage reporting.
- **FR-003**: The project MUST continue to exercise Python 3.15 in CI on pushes
  to `main` (post squash-merge) so that 3.15-specific breakage is still
  detected, even though 3.15 no longer runs on individual pull requests.
- **FR-004**: A Python 3.15 failure detected by the reduced-cadence job MUST be
  visible to maintainers as a failed CI run.
- **FR-005**: The change MUST NOT leave the branch-protection required-check
  set referencing a job that no longer runs on pull requests, so that PRs are
  not blocked waiting on a check that can never report.
- **FR-006**: The change MUST be reversible — folding Python 3.15 back into the
  per-PR matrix once upstream prebuilt wheels exist MUST require only a small,
  obvious configuration edit.
- **FR-007**: The reasoning for the chosen approach (why 3.15 is treated
  differently, and how to undo it later) MUST be recorded in the workflow so a
  future maintainer understands it without archaeology.

### Key Entities

- **CI test matrix**: The set of Python versions the test suite runs against on
  each pull request. Currently 3.10, 3.11, 3.12, 3.13, 3.14, 3.14t, 3.15.
- **Reduced-cadence 3.15 run**: A CI execution of the test suite on Python 3.15
  that runs less often than per-PR (e.g. post-merge on `main` and/or
  scheduled), providing early-warning coverage off the PR critical path.
- **Required-check set**: The branch-protection configuration naming which CI
  jobs must pass before a PR can merge.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The slowest job in the per-PR test gate completes in
  approximately the time of the other matrix versions (target: under ~60s,
  versus ~137s today), removing the ~1.5-minute 3.15 penalty from the PR
  critical path.
- **SC-002**: Stable-version coverage is unchanged: the same Python versions
  (3.10–3.14 and 3.14t) run on every PR and report coverage as before.
- **SC-003**: Python 3.15 is still executed by CI on every push to `main`, and
  a deliberately introduced 3.15-only failure produces a visible failed run.
- **SC-004**: No pull request is blocked by a required check that no longer
  runs; the merge gate for a normal green PR reports success without the 3.15
  job.

## Assumptions

- Python 3.15 is currently a prerelease with incomplete prebuilt-wheel
  coverage; the slowness is dominated by source builds of native-extension
  dependencies, not by test execution (tests run in <2s locally). The plan
  phase will confirm the dominant cost before choosing a fix.
- 3.14 (the newest stable) provides sufficient "newest Python" coverage for
  per-PR gating, so per-PR 3.15 testing is not required for correctness
  confidence today.
- Moving 3.15 to post-merge-on-`main` is the accepted trade-off (see
  Clarifications): early-warning coverage on every merge, off the PR critical
  path. Scheduled/cron runs and per-PR build caching were considered and not
  chosen.
- The repository's branch-protection required checks are configured against the
  summary `test` gate job; changes must keep that gate reporting correctly for
  PRs.
