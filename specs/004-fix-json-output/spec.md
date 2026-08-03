# Feature Specification: Fix JSON Output Corruption

**Feature Branch**: `004-fix-json-output`

**Created**: 2026-08-03

**Status**: Draft

**Input**: User description: "Fix --format json producing Rich markup errors and invalid JSON output on issues/comments commands. Root cause: console.print(json.dumps(...)) passes JSON through Rich's markup parser which chokes on [ and ] array literals. Fix by replacing with click.echo(json.dumps(...)) across ~6 spots in youtrack_cli/commands/issues.py (lines 656, 969, 1364, 1562, 1682, 1764). Also check other command files for the same pattern. GitHub issue: #756"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - JSON output is valid and pipeable (Priority: P1)

A user runs any `yt` command with `--format json` and pipes the result to `jq`
or another JSON tool. The tool receives well-formed JSON with no interleaved
warning messages.

**Why this priority**: The `--format json` flag exists to enable scripting and
tool integration. Corrupted output breaks every downstream consumer; fixing
this is the entire purpose of the feature.

**Independent Test**: Run `yt issues list --format json | jq .` against a live
or mocked YouTrack instance — the command must exit 0 and `jq` must parse the
output without error.

**Acceptance Scenarios**:

1. **Given** a YouTrack instance with issues, **When** `yt issues list --format json` is run, **Then** stdout contains only valid JSON with no Rich markup warnings.
2. **Given** issues with descriptions that contain square brackets (e.g. `[bug]`), **When** `yt issues list --format json` is run, **Then** the square brackets appear verbatim in the JSON output without causing parse errors.
3. **Given** any JSON-format command is piped to `jq .`, **When** the command completes, **Then** `jq` exits 0 and pretty-prints the result.

---

### User Story 2 - All affected subcommands are fixed consistently (Priority: P2)

A user who scripts against multiple `yt` subcommands expects `--format json` to
behave identically across `issues list`, `issues get`, `issues comments list`,
`issues attachments list`, `issues links list`, and any other subcommand that
offers JSON output — including commands outside of `issues.py`.

**Why this priority**: Fixing only some of the call sites would leave silent
landmines and give users false confidence in the fix.

**Independent Test**: Run `--format json` on each affected subcommand in turn
and assert valid JSON output for each.

**Acceptance Scenarios**:

1. **Given** `yt issues get <ID> --format json`, **When** run, **Then** valid JSON only on stdout.
2. **Given** `yt issues comments list <ID> --format json`, **When** run, **Then** valid JSON only on stdout.
3. **Given** `yt issues attachments list <ID> --format json`, **When** run, **Then** valid JSON only on stdout.
4. **Given** `yt issues links list <ID> --format json`, **When** run, **Then** valid JSON only on stdout.
5. **Given** any other command file that uses the same `console.print(json.dumps(...))` pattern, **When** `--format json` is run, **Then** valid JSON only on stdout.

---

### User Story 3 - No regression in human-readable output (Priority: P3)

A user who normally runs commands without `--format json` continues to see
Rich-formatted, coloured table output unchanged.

**Why this priority**: The fix must be surgical — only the machine-readable
path changes.

**Independent Test**: Run `yt issues list` (no `--format` flag) and confirm
Rich-formatted table output still appears.

**Acceptance Scenarios**:

1. **Given** `yt issues list` with no format flag, **When** run, **Then** Rich-formatted table output appears as before.
2. **Given** `yt issues list --format table`, **When** run, **Then** output is unchanged from pre-fix behaviour.

---

### Edge Cases

- What happens when issue descriptions or comments contain Rich markup-like strings such as `[bold]` or `[red]`? They must appear verbatim in JSON output.
- What happens when the JSON payload is empty or null? Output should be `null` or `[]` — valid JSON — not a blank line or a Rich warning.
- What happens when stdout is not a terminal (piped)? Output must still be valid JSON (no colour-stripping artefacts or partial writes).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every code path in the CLI that serialises data as JSON for `--format json` MUST write to stdout using a mechanism that does not pass the JSON string through Rich's markup parser.
- **FR-002**: The fix MUST cover all instances of `console.print(json.dumps(...))` in `youtrack_cli/commands/issues.py` (identified at lines 656, 969, 1364, 1562, 1682, 1764) and any equivalent occurrences in other command files.
- **FR-003**: The replacement output mechanism MUST write directly to stdout without markup interpretation, colour injection, or any Rich formatting.
- **FR-004**: Human-readable output paths (table, CSV, Rich-formatted text) MUST NOT be altered by this change.
- **FR-005**: A regression test MUST be added that asserts the JSON output of at least one affected command is valid JSON (parseable without error) and contains no Rich markup warning text.
- **FR-006**: All existing tests MUST continue to pass after the change.

### Key Entities

- **JSON output path**: The code branch executed when `format == "json"` in a command handler — currently uses `console.print(json.dumps(...))`, must use `click.echo(json.dumps(...))`.
- **Rich console**: The application-wide Rich `Console` instance used for human-readable output — must not be used for machine-readable output.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `yt issues list --format json | jq .` exits 0 with no error output on stderr for a standard issues listing.
- **SC-002**: JSON output from all affected subcommands is parseable by the Python standard `json` module without raising `json.JSONDecodeError`.
- **SC-003**: No Rich markup warning text (e.g. "markup" or "unescaped") appears on stdout or stderr when `--format json` is used.
- **SC-004**: All pre-existing tests pass (zero regressions).
- **SC-005**: At least one new automated test fails before the fix and passes after (regression guard).

## Assumptions

- `click.echo()` is the correct replacement — it writes directly to stdout with no markup processing and is already a project dependency.
- The fix is purely a call-site substitution; no new abstractions or helpers are needed.
- Commands outside `youtrack_cli/commands/issues.py` that use the same anti-pattern (e.g. `articles.py`, `projects.py`, `boards.py`) will be audited and fixed in the same change.
- The `ndjson` format path (which uses `click.echo(json.dumps(issue))`) is already correct and does not need to change.
- No changes to CLI flag names, option signatures, or public API are required.
