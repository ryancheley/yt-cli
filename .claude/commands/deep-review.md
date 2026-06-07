# Deep CLI Documentation Review

## Purpose
Perform a comprehensive, **live** review that compares the actual CLI behavior
against everything in `docs/`, and report (or fix) the discrepancies. Do not
print canned results — every finding below must come from running the current
CLI and reading the current docs in this repo.

## Method

Work through these steps in order. Use `scratch/` for any intermediate
artifacts (it is gitignored).

### 1. Extract the real CLI command tree
Recursively walk every command, subcommand, and option from `--help`. Write this
helper to `scratch/walk_cli.py` and run it, capturing the tree to
`scratch/cli_tree.json`:

```python
#!/usr/bin/env python3
"""Recursively walk the yt CLI command tree via --help and dump JSON."""
import json, re, subprocess


def help_for(path):
    cmd = ["python", "-m", "youtrack_cli.main"] + path + ["--help"]
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    except Exception as e:  # noqa
        return f"ERROR: {e}"


def parse_help(text):
    subcommands, options, section = {}, [], None
    for line in text.split("\n"):
        s = line.strip()
        if s == "Commands:":
            section = "commands"; continue
        if s == "Options:":
            section = "options"; continue
        if s and not line.startswith(" ") and s.endswith(":"):
            section = None; continue
        if section == "commands" and line.startswith("  ") and s:
            parts = s.split(None, 1)
            subcommands[parts[0]] = parts[1] if len(parts) > 1 else ""
        elif section == "options" and s.startswith("-"):
            options.append(re.split(r"\s{2,}", s)[0])
    return subcommands, options


def walk(path):
    subs, opts = parse_help(help_for(path))
    return {"options": opts,
            "subcommands": {s: walk(path + [s]) for s in subs}}


if __name__ == "__main__":
    print(json.dumps(walk([]), indent=2))
```

Run with: `uv run python scratch/walk_cli.py > scratch/cli_tree.json`

### 2. Compare against the docs across all of these dimensions
Use the tree plus `grep`/reads over `docs/` (both `docs/commands/*.rst` and the
cross-cutting prose: `index.rst`, `quickstart.rst`, `workflows.rst`,
`learning-path.rst`, `youtrack-concepts.rst`, `configuration.rst`,
`troubleshooting.rst`, `custom-fields.rst`, `progress-indicators.rst`, etc.).

1. **Top-level commands**: every command in the tree appears in
   `docs/commands/index.rst` toctree and has a `docs/commands/<cmd>.rst`, and
   vice-versa (no documented command that doesn't exist).
2. **Subcommands (incl. nested)**: every `yt <cmd> <sub> [<sub2>]` path in the
   tree is documented; flag documented paths that don't exist.
3. **Options — missing**: options present in the CLI but never mentioned in that
   command's doc file.
4. **Options — invented**: options documented (`--foo`, `--format [..]` choices)
   that the CLI does **not** have. This is the highest-value category and the
   easiest to miss — e.g. a doc claiming `--format [table|json|csv]` when the
   command only supports `[table|json]`, or no `--format` at all.
5. **Broken examples**: extract every `yt ...` invocation from the docs and
   validate the command path and the options against the tree.
6. **Global options table** in `index.rst`: must match exactly the options shown
   under `Options:` in `yt --help` (watch for options documented as global that
   are really per-subcommand).

### 3. Verify before reporting (avoid false positives)
A bracketed token after a subcommand is usually an **argument** (a username,
alias name, theme name, issue id), not a broken subcommand. Before flagging any
item:
- Run the specific `uv run yt <path> --help` to confirm the subcommand/option
  truly does or doesn't exist.
- Read the surrounding doc context — some "wrong" commands are intentional
  (e.g. troubleshooting docs that show an incorrect form next to the correct
  one). Leave those alone.

### 4. Write the report
Write a prioritized findings file to `scratch/docs-review-<YYYY-MM-DD>.md`:
- **HIGH**: an example that fails when run (wrong command path, invented option,
  wrong positional/flag) or a wrong global-options table.
- **MED**: a real feature (option/subcommand) with no documentation.
- **LOW**: cosmetic / hypothetical wording.

Each finding: the doc location(s), the broken text, and the correct form.

### 5. Decide next step (ask the user)
Do **not** auto-create GitHub issues. Present the summary and ask how to proceed:
fix everything in one PR, fix only HIGH items, file grouped GitHub issues, or
stop at the report. Then follow this repo's workflow (feature branch named after
the issue, `pre-commit run --all-files`, squash-merge once green).

## Usage
This is a Claude Code slash command — invoke it as `/deep-review`. It is not a
`yt` subcommand.
