# Data Model: Fix JSON Output Corruption

**Date**: 2026-08-03 | **Feature**: 004-fix-json-output

## Overview

This is a bug fix with no data model changes. No new entities, fields, or relationships are introduced. No database migrations are required.

## Affected Output Paths

The only "model" relevant to this fix is the runtime call-site pattern being replaced:

### Before (broken)

```python
console.print(json.dumps(<data>, indent=2))
# Rich parses the string for markup — [ and ] in JSON arrays trigger warnings
```

### After (fixed)

```python
click.echo(json.dumps(<data>, indent=2))
# Writes directly to stdout; no markup processing
```

## Invariants

- The JSON structure of all output remains identical — only the output mechanism changes.
- `indent=2` is preserved on all sites.
- `default=str` is preserved on `main.py` audit sites.
- Human-readable (table/CSV/Rich-formatted) code paths are not touched.
