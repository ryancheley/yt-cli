# Quickstart: Validating the Codecov → self-hosted coverage migration

This feature is CI configuration, so validation is primarily by observing the
PR's own CI run. Below are the checks that prove each requirement.

## Prerequisites

- The change is on branch `700-ditch-codecov` and pushed as a PR (CI is PR-gated).
- `gh` CLI authenticated.

## 1. Static / local checks (before relying on CI)

```bash
# No functional Codecov references remain (SC-001).
# Expect: no output.
grep -ri codecov .github README.md

# Workflow is still valid YAML and passes the security review.
uvx zizmor .github/workflows/

# The threshold source of truth is present and is 60.
grep -n "fail_under" pyproject.toml   # [tool.coverage.report] fail_under = 60
```

Sanity-check the combine mechanics locally (simulates two matrix jobs):

```bash
rm -f .coverage .coverage.*
uv run pytest tests/test_console.py -q >/dev/null 2>&1 && mv .coverage .coverage.a
uv run pytest tests/test_common.py  -q >/dev/null 2>&1 && mv .coverage .coverage.b
uv tool run coverage combine        # or: uvx coverage combine
uv tool run coverage report --format=markdown   # renders a markdown table
rm -f .coverage .coverage.*
```

Expected: `coverage combine` reports "Combined data file …" for each input and
`coverage report` prints a table. (Local numbers are low because only two test
files ran — this only proves the *mechanics*, not the gate.)

## 2. CI checks on the PR

Open the PR CI run and confirm:

| Requirement | What to verify |
|-------------|----------------|
| FR-003/004 | Each `test (3.x)` job has an artifact `coverage-data-3.x` containing `.coverage.3.x`. |
| FR-005 | The `coverage` job runs even if a `test` job fails (`if: always()`). |
| FR-006 | The `coverage` job log shows `coverage combine` merging all versions. |
| FR-007 | The run **Summary** page shows a markdown coverage table with the total %. |
| FR-008 | The `coverage` job is green (aggregate ≥ 60). |
| FR-010 | On a green run there is **no** `html-report` artifact. |
| FR-011 | The `test` (summary) required check depends on `coverage` and is green. |
| SC-005 | The reported % reflects all matrix versions combined (≥ any single version). |

## 3. Negative test (optional, do not merge)

To prove the gate actually blocks (SC-003), temporarily lower coverage below 60
(e.g. add a large uncovered module) on a throwaway commit and confirm:

- the `coverage` job **fails**,
- the run **Summary** still shows the markdown report (written before the gate),
- an `html-report` artifact **is** produced (`if: failure()`),
- `tests-complete` (the `test` required check) is **red**, blocking merge.

Revert the throwaway commit before merging.

## 4. Post-merge

- Confirm the deleted `coverage-baseline` job no longer appears on `push` runs to
  `main` (FR-002); `test-py315` still runs.

## Diagnostics

- If `coverage report` shows 0% or "No source for code": the combined data's
  absolute paths didn't match the checkout path. Add a `[tool.coverage.paths]`
  remap in `pyproject.toml` (see research R5) and re-run.
- If the artifact is empty: the upload step is missing `include-hidden-files:
  true` (the data file is a dotfile).
