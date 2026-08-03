# Research: Fix JSON Output Corruption

**Date**: 2026-08-03 | **Feature**: 004-fix-json-output

## Findings

### Decision: Use `click.echo()` for all machine-readable JSON output

**Rationale**: `click.echo()` writes a string directly to stdout (or the configured stream) with no markup processing, no colour injection, and no Rich involvement. It is already a project dependency (Click is the CLI framework) and is already used correctly in the `ndjson` streaming path (`click.echo(json.dumps(issue))`). Using it for the `--format json` path makes all machine-readable output paths consistent.

**Alternatives considered**:

| Option | Verdict | Reason rejected |
|--------|---------|-----------------|
| `console.print(json.dumps(...), markup=False, highlight=False)` | Rejected | Still routes through Rich's console; adds kwargs to every call site; `highlight=False` needed to avoid syntax colouring on some Rich versions |
| `console.print_json(data=...)` | Rejected for this pattern | Rich's `print_json` applies syntax highlighting and may emit ANSI codes even in non-TTY (version-dependent); semantically wrong for a pipeable stream |
| `sys.stdout.write(json.dumps(...) + "\n")` | Rejected | `click.echo` already wraps this with cross-platform newline handling; no benefit to going lower |
| `click.echo(json.dumps(...))` | **Selected** | Minimal, correct, already used in codebase, no new imports needed |

---

### Decision: Scope includes `main.py` audit output in addition to `commands/`

**Rationale**: `main.py` lines 416 and 2056 use `console.print(json.dumps(audit_data, indent=2, default=str))`. These are JSON output paths (the `--format json` equivalent for the audit command). They must be fixed for the same reason.

**Alternatives considered**: Leaving `main.py` out of scope was considered (the issue originally named only `issues.py` and `comments`), but consistency and correctness require fixing all instances of the anti-pattern.

---

### Decision: `console.print_json(data=...)` calls do NOT need changing

**Rationale**: Calls to `console.print_json(data=...)` (found in `boards.py`, `time_tracking.py`, and `common.py`) use Rich's dedicated JSON printer, which serialises the data to JSON internally and does not parse the resulting string as Rich markup. When stdout is not a TTY (i.e., piped), Rich strips ANSI codes. These calls are not implicated in the reported bug.

**Confirmed locations** (leave unchanged):
- `commands/boards.py`: lines 49, 87
- `commands/time_tracking.py`: lines 97, 138, 198
- `commands/common.py`: line 23

---

### Complete inventory of `console.print(json.dumps(...))` sites to fix

| File | Lines | Variable |
|------|-------|----------|
| `youtrack_cli/commands/issues.py` | 656 | `issues` |
| `youtrack_cli/commands/issues.py` | 969 | `issues` |
| `youtrack_cli/commands/issues.py` | 1364 | `comments` |
| `youtrack_cli/commands/issues.py` | 1562 | `attachments` |
| `youtrack_cli/commands/issues.py` | 1682 | `links` |
| `youtrack_cli/commands/issues.py` | 1764 | `link_types` |
| `youtrack_cli/commands/users.py` | 222 | `users` |
| `youtrack_cli/commands/users.py` | 535 | `groups` |
| `youtrack_cli/commands/users.py` | 587 | `roles` |
| `youtrack_cli/commands/users.py` | 678 | `teams` |
| `youtrack_cli/commands/projects.py` | 216 | `projects` |
| `youtrack_cli/commands/projects.py` | 280 | `project` |
| `youtrack_cli/commands/projects.py` | 573 | `custom_fields` |
| `youtrack_cli/commands/articles.py` | 679 | `articles` |
| `youtrack_cli/commands/articles.py` | 821 | `articles` |
| `youtrack_cli/commands/articles.py` | 882 | `draft_articles` |
| `youtrack_cli/commands/articles.py` | 1244 | `comments` |
| `youtrack_cli/commands/articles.py` | 1491 | `attachments` |
| `youtrack_cli/main.py` | 416 | `audit_data` |
| `youtrack_cli/main.py` | 2056 | `audit_data` |

**Total**: 20 sites across 5 files.

**Substitution pattern** (identical for every site):
```python
# Before
console.print(json.dumps(<var>, indent=2))

# After
click.echo(json.dumps(<var>, indent=2))
```

For `main.py` audit sites (which use `default=str`):
```python
# Before
console.print(json.dumps(audit_data, indent=2, default=str))

# After
click.echo(json.dumps(audit_data, indent=2, default=str))
```

Each affected file already imports both `json` and `click` (click is the CLI framework); no new imports are needed.
