# Quickstart / Validation: Empty-comment comment listing (#768)

Validates that listing comments succeeds when issues have zero comments, single and batched.

## Prerequisites

- `uv sync`
- A reachable YouTrack (dev default `http://0.0.0.0:8080`) with at least one issue that has
  **no** comments and one that has comments.

## Automated regression (primary)

```bash
uv run pytest tests -k "comments_list" -q
```

Expected: the new regression test for a multi-issue batch containing an empty-comment issue
passes; it fails on `main` before the fix with a `RuntimeError: Event loop is closed`.

## Manual validation

Single empty-comment issue:

```bash
yt issues comments list ISSUE-WITH-NO-COMMENTS
```

Expected: exits 0, shows an empty comments table (no error, no traceback).

Batch via stdin, mixing empty and non-empty issues (the reported repro):

```bash
printf 'ISSUE-WITH-COMMENTS\nISSUE-WITH-NO-COMMENTS\n' | yt issues comments list
```

Expected: both issues processed, empty one shows no comments, exit 0, **no** "Event loop is
closed" error.

JSON output unchanged:

```bash
yt issues comments list ISSUE-WITH-NO-COMMENTS --format json   # -> []
printf 'A\nB\n' | yt issues comments list --format json        # -> {"A": [...], "B": [...]}
```

## Gates

```bash
uv run pre-commit run --all-files
uv run ty check
uv run pytest -q
```
