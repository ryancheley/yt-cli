# Implementation Plan: Speed up the Python 3.15 CI test job

**Branch**: `ci-py315-speedup-736` | **Date**: 2026-07-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-ci-py315-speedup/spec.md`

## Summary

Python 3.15 is a prerelease with no prebuilt native-extension wheels, so its
per-PR `test` job compiles dependencies from source and takes ~137s — ~3x the
stable versions and the long pole on every PR. Remove `3.15` from the per-PR
`test` matrix and instead run a dedicated Python 3.15 job on pushes to `main`
(post squash-merge), preserving early-warning coverage off the PR critical path.
Single-file change to `.github/workflows/ci.yml`; no branch-protection edit is
needed because the required `test` check is the summary aggregation job, not an
individual matrix leg.

## Technical Context

**Language/Version**: N/A (CI configuration change; affects GitHub Actions YAML)

**Primary Dependencies**: GitHub Actions (`actions/setup-python`,
`astral-sh/setup-uv`), `tox` / `tox-uv`, `uv`

**Storage**: N/A

**Testing**: The change is validated by CI behavior itself — PR runs (no 3.15
leg) and push-to-`main` runs (3.15 job present). Existing `pytest`/`tox` suite
is unchanged.

**Target Platform**: `ubuntu-latest` GitHub-hosted runners

**Project Type**: Single-project Python CLI (change is confined to CI config)

**Performance Goals**: Per-PR test gate's slowest job under ~60s (down from
~137s); ~1.5 min removed from the PR critical path.

**Constraints**: Must keep stable-version coverage (3.10–3.14, 3.14t) on every
PR; must keep the `test` required check reporting; must keep 3.15 exercised on
every merge to `main`; must be reversible in one obvious edit.

**Scale/Scope**: One file (`.github/workflows/ci.yml`); ~1 line removed from the
matrix + ~1 new job (~20 lines) + comment updates.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Code Quality**: No application code changes. `zizmor` reviews GitHub
  Actions — the workflow security job (`uvx zizmor .github/workflows/`) must
  stay clean for the new job. Pinned action SHAs reused from existing steps.
  ✅ PASS.
- **II. Testing Standards (NON-NEGOTIABLE)**: No test code changes; the full
  `pytest`/`tox` suite still runs — on 3.10–3.14/3.14t per PR and on 3.15 per
  merge to `main`. Total test coverage of the code is unchanged; only the
  *cadence* of the 3.15 leg moves. This is a CI-timing change, not a coverage
  reduction (spec SC-002). ✅ PASS.
- **III. User Experience Consistency**: No CLI surface change. ✅ N/A.
- **IV. Performance Requirements**: This *improves* CI responsiveness (the
  spirit of the principle) without regressing any runtime latency. Performance
  impact stated here and to be restated in the PR. ✅ PASS.
- **Workflow**: Change lives on feature branch `ci-py315-speedup-736`, tied to
  issue #736; `docs/` reviewed for CI references (see Phase 1). ✅ PASS.

No violations. Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/002-ci-py315-speedup/
├── plan.md              # This file
├── spec.md              # Feature spec (+ Clarifications)
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output (validation guide)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

Not generated (justified): `data-model.md` — no data entities; this is a CI
config change. `contracts/` — no external/API/CLI interface changes.

### Source Code (repository root)

```text
.github/workflows/ci.yml   # ONLY file changed
```

**Structure Decision**: Single-file CI change. Two edits to `ci.yml`:
1. Remove `"3.15"` from the `test` job's `strategy.matrix.python-version`,
   updating the adjacent comment to explain 3.15 now runs post-merge and how to
   fold it back when cp315 wheels ship.
2. Add a push-only job (`if: github.event_name == 'push'`) named e.g.
   `test-py315` that sets up uv + Python 3.15 (`allow-prereleases: true`) and
   runs `uvx --with tox-uv tox -e py315`, mirroring the existing
   `coverage-baseline` job's step structure.

## Complexity Tracking

No constitution violations — section intentionally empty.
