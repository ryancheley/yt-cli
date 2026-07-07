# Implementation Plan: Fix State Filter Returning Incorrect Issues

**Branch**: `fix-state-filter-721` | **Date**: 2026-07-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-fix-state-filter/spec.md`

## Summary

The `yt issues list --state '<value>'` filter builds a YouTrack query of the form
`State: In Progress`. YouTrack parses the unescaped multi-word value as
`State: In` **AND** free-text `Progress`, so it matches any issue whose text
mentions "Progress". The fix wraps the state value in YouTrack's curly-brace
escaping (`State: {In Progress}`) at every point where the `state:` filter term
is constructed from a user-supplied value, so multi-word states are treated as a
single atomic filter term.

## Technical Context

**Language/Version**: Python 3.9+ (project targets multiple versions via `tox`)

**Primary Dependencies**: `click`, `rich`, `pydantic`, `httpx` (existing; none added)

**Storage**: N/A (stateless CLI over YouTrack REST API)

**Testing**: `pytest` (real-object preference per constitution)

**Target Platform**: Cross-platform CLI

**Project Type**: Single-project CLI

**Performance Goals**: No change; fix is pure query-string construction, no extra API calls

**Constraints**: Must not regress single-word state filtering or query composition with project/assignee/free-text filters

**Scale/Scope**: Two query-construction sites; ~1 small helper + escaping calls

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Code Quality**: PASS — small change, will pass `ruff`/`ty`; docs unaffected (no CLI surface change), but example in help text remains valid. No new dependencies (`uv` only).
- **II. Testing (NON-NEGOTIABLE)**: PASS — adds a regression test that fails before / passes after, exercising the query built for a multi-word state (real objects, no network).
- **III. UX Consistency**: PASS — no flag/naming change; output behavior becomes correct. No new user-facing surface.
- **IV. Performance**: PASS — no additional API calls; pure string handling.

No violations. Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/001-fix-state-filter/
├── plan.md              # This file
├── spec.md              # Feature spec
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 validation guide
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # /speckit-tasks output (not created here)
```

Note: `data-model.md` and `contracts/` are intentionally omitted — this is a bug
fix with no new data entities and no change to the CLI command contract.

### Source Code (repository root)

```text
youtrack_cli/
├── managers/issues.py   # LIVE path: IssueManager.list_issues builds "State: {state}"  (line ~649)
├── issues.py            # Legacy IssueClient.list_issues builds "state:{state}"          (line ~284)
└── utils.py             # Candidate home for a small escape helper (or inline)

tests/
└── (existing issue tests) # Add regression test for multi-word state query construction
```

**Structure Decision**: Single-project layout (existing). The change touches the
two sites where a `state:` filter term is composed from user input, plus one new
regression test.

## Complexity Tracking

No constitution violations — section intentionally empty.
