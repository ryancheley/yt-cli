<!--
Sync Impact Report
==================
Version change: TEMPLATE (unfilled) → 1.0.0
Bump rationale: Initial ratification of a concrete constitution from the
  unfilled template. MAJOR baseline established (1.0.0).

Modified principles:
  - [PRINCIPLE_1_NAME] → I. Code Quality
  - [PRINCIPLE_2_NAME] → II. Testing Standards (NON-NEGOTIABLE)
  - [PRINCIPLE_3_NAME] → III. User Experience Consistency
  - [PRINCIPLE_4_NAME] → IV. Performance Requirements
  - [PRINCIPLE_5_NAME] → (removed; constitution defines 4 principles per request)

Added sections:
  - Quality Gates & Tooling (replaces [SECTION_2_NAME])
  - Development Workflow (replaces [SECTION_3_NAME])

Removed sections:
  - Fifth principle slot (template provided 5; this constitution defines 4)

Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Constitution Check is generic; no edit needed)
  - ✅ .specify/templates/spec-template.md (no principle-specific references; no edit needed)
  - ✅ .specify/templates/tasks-template.md (task categories align with principles; no edit needed)

Follow-up TODOs: none
-->

# YouTrack CLI Constitution

## Core Principles

### I. Code Quality

All code MUST pass the project's automated quality gates before merge: `ruff`
for linting and formatting, and `ty` for type checking. Type checking is
performed with `ty` — never `mypy` or `pyright`. Pre-commit hooks
(`pre-commit run --all-files`) MUST pass with no bypasses; the `--no-verify`
flag and equivalent escape hatches are prohibited. Public functions and CLI
command handlers MUST carry type annotations. Dependencies are managed
exclusively through `uv` (`uv add`, `uv remove`, `uv sync`); `pip`, `poetry`,
and `conda` MUST NOT be used. Every functional change MUST update the
corresponding documentation in `docs/`.

**Rationale**: A CLI is only trustworthy if its internals are consistent and
verifiable. Enforcing a single toolchain and unbypassed gates keeps the
codebase reviewable and prevents drift between contributors and environments.

### II. Testing Standards (NON-NEGOTIABLE)

All tests MUST pass before any merge to `main`. The project uses `pytest` for
tests and `tox` for multi-version Python runs; `zizmor` reviews GitHub Actions.
New functionality MUST ship with tests that exercise real behavior — prefer
real objects over mocks, and use mocks only when a real dependency cannot be
driven in-process (justify each mock). Tests MUST be deterministic and
independent of external network state unless explicitly testing integration
against the configured `base_url`. A bug fix MUST include a regression test
that fails before the fix and passes after.

**Rationale**: The CLI mediates real operations against YouTrack; untested
paths become production incidents for users. Real-object testing catches the
integration mistakes that mocks routinely hide.

### III. User Experience Consistency

The CLI MUST present a coherent, ergonomic interface. Output for humans goes to
stdout and errors to stderr; commands that emit data MUST support both a
human-readable (rich-formatted) view and a machine-readable JSON view. Command,
subcommand, flag, and option naming MUST follow the existing conventions of the
CLI — new commands match the patterns already in use. User-facing output uses
`rich` for formatting and `pydantic` for validated input/output models. Error
messages MUST be actionable: state what failed and what the user can do about
it. Exit codes MUST be non-zero on failure. The `yt tutorial` command MUST be
reviewed and updated whenever the CLI API changes.

**Rationale**: Consistency is what lets users build muscle memory and scripts
on top of the tool. Predictable naming, dual human/JSON output, and clear
errors are the difference between a CLI people trust and one they fight.

### IV. Performance Requirements

Commands MUST remain responsive. Network calls to YouTrack MUST be the only
expected source of latency; local processing MUST NOT add perceptible delay.
List and search commands MUST support pagination and MUST NOT load unbounded
result sets fully into memory. The CLI MUST NOT make redundant API calls when a
single request or a batched request suffices. Long-running operations MUST
provide progress feedback (e.g. a `rich` progress indicator) rather than
appearing to hang. Performance-sensitive changes MUST state their expected
impact and MUST NOT regress the latency of existing commands without
justification recorded in the pull request.

**Rationale**: A command-line tool is judged by how fast it feels. Bounded
memory, no wasted round-trips, and visible progress keep the CLI usable
against large YouTrack instances and slow networks alike.

## Quality Gates & Tooling

The following gates are mandatory and MUST pass before code reaches `main`:

- `pre-commit run --all-files` after every file change, with no bypass.
- `uv run ruff` (lint + format) clean.
- `uv run ty` (type check) clean.
- `uv run pytest` green; `tox` green across supported Python versions.
- `zizmor` review clean for any change to GitHub Actions workflows.

All Python commands MUST be run through `uv` (`uv run …`). GitHub Actions checks
MUST always pass before merge and MUST NOT be bypassed or force-merged.

## Development Workflow

1. Every feature or fix corresponds to a GitHub issue.
2. A feature branch MUST be created before committing; pushing directly to
   `main` is prohibited even when permitted by GitHub.
3. The implementation plan for an issue is written to `scratch/issue-<id>.md`
   before code is written.
4. Commit messages MUST start with an emoji.
5. Pull requests MUST pass all checks; checks are never bypassed.
6. Once a PR passes it is squash-merged; the author then switches to `main` and
   pulls the merged changes.
7. Documentation in `docs/` is updated as part of the same change, not deferred.

## Governance

This constitution supersedes other ad-hoc practices for the YouTrack CLI. When a
practice conflicts with this document, this document wins.

Amendments require a pull request that updates this file, a clear statement of
what changed and why, and a version bump per the policy below. Versioning of the
constitution follows semantic versioning:

- **MAJOR**: Backward-incompatible governance changes, or removal/redefinition
  of a principle.
- **MINOR**: A new principle or section, or materially expanded guidance.
- **PATCH**: Clarifications, wording, and non-semantic refinements.

Compliance is verified at review time: every PR MUST be checked against these
principles and quality gates before merge. Complexity or deviation MUST be
justified in the PR description, and unjustified violations block the merge. For
day-to-day runtime development guidance, contributors consult `CLAUDE.md` and
the documentation in `docs/`.

**Version**: 1.0.0 | **Ratified**: 2026-06-20 | **Last Amended**: 2026-06-20
