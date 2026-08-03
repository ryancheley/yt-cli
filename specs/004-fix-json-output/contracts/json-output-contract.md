# CLI Contract: `--format json` Output

**Feature**: 004-fix-json-output | **Date**: 2026-08-03

## Contract

Any `yt` subcommand that accepts `--format json` MUST:

1. Write **only** valid JSON to stdout — no interleaved text, warnings, or ANSI codes.
2. Produce output that is parseable by `python -m json.tool` and `jq` without error.
3. Exit with code 0 on success; exit non-zero and write error details to stderr on failure.
4. NOT write status/progress messages to stdout when `--format json` is active (existing `MACHINE_READABLE_FORMATS` guard in `console.py` already enforces this).

## Affected Commands

| Command | Flag |
|---------|------|
| `yt issues list` | `--format json` |
| `yt issues get <ID>` | `--format json` |
| `yt issues comments list <ID>` | `--format json` |
| `yt issues attachments list <ID>` | `--format json` |
| `yt issues links list <ID>` | `--format json` |
| `yt issues link-types` | `--format json` |
| `yt users list` | `--format json` |
| `yt users groups` | `--format json` |
| `yt users roles` | `--format json` |
| `yt users teams` | `--format json` |
| `yt projects list` | `--format json` |
| `yt projects get <ID>` | `--format json` |
| `yt projects custom-fields <ID>` | `--format json` |
| `yt articles list` | `--format json` |
| `yt articles get <ID>` | `--format json` |
| `yt articles comments list <ID>` | `--format json` |
| `yt articles attachments list <ID>` | `--format json` |

## Out of Scope

- `ndjson` format (already correct — uses `click.echo`)
- `csv` format (not a JSON concern)
- `console.print_json(data=...)` calls in `boards.py`, `time_tracking.py`, `common.py` — these use Rich's dedicated JSON printer and are not implicated in the bug
