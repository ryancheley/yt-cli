# Quickstart Validation Guide: Fix JSON Output Corruption

**Feature**: 004-fix-json-output | **Date**: 2026-08-03

## Prerequisites

- A configured `yt` CLI (`yt auth login` completed, or a `.env` with credentials)
- `jq` installed (`brew install jq` / `apt install jq`)
- Python available for the stdlib validation path

## Automated Regression Test (no YouTrack needed)

The regression test uses Click's test runner to invoke commands with mocked API responses and asserts the output is parseable JSON with no Rich markup warnings. Run:

```bash
uv run pytest tests/ -k "json_output" -v
```

Expected: all tests pass, no warnings about unescaped markup.

The test must fail on the pre-fix codebase and pass after.

## Manual Validation Against a Live Instance

### 1. Issues list

```bash
yt issues list --format json | python -m json.tool > /dev/null && echo "PASS"
yt issues list --format json | jq 'length'
```

Expected: `PASS` printed; `jq` outputs the count of issues with no parse error.

### 2. Issues get

```bash
yt issues get <ISSUE-ID> --format json | python -m json.tool > /dev/null && echo "PASS"
```

### 3. Comments

```bash
yt issues comments list <ISSUE-ID> --format json | python -m json.tool > /dev/null && echo "PASS"
```

### 4. Attachments

```bash
yt issues attachments list <ISSUE-ID> --format json | python -m json.tool > /dev/null && echo "PASS"
```

### 5. Links

```bash
yt issues links list <ISSUE-ID> --format json | python -m json.tool > /dev/null && echo "PASS"
```

### 6. Users

```bash
yt users list --format json | python -m json.tool > /dev/null && echo "PASS"
```

### 7. Projects

```bash
yt projects list --format json | python -m json.tool > /dev/null && echo "PASS"
```

### 8. Articles

```bash
yt articles list --format json | python -m json.tool > /dev/null && echo "PASS"
```

## Regression Check: Human-Readable Output Unchanged

```bash
yt issues list            # must show Rich-formatted table
yt issues list --format table   # same
```

Expected: coloured table output with no change in appearance.

## Edge Case: Issue with Brackets in Description

If possible, use an issue with `[bug]` or `[feature]` in its description:

```bash
yt issues get <ISSUE-WITH-BRACKETS-ID> --format json | python -m json.tool
```

Expected: brackets appear verbatim in JSON, no markup warning on stderr.

## Confirming No Rich Markup Warnings

```bash
yt issues list --format json 2>/tmp/stderr_check.txt | python -m json.tool > /dev/null
grep -i "markup\|unescaped\|escape" /tmp/stderr_check.txt && echo "FAIL: warnings found" || echo "PASS: no warnings"
```
