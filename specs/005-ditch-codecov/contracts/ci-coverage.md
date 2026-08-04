# Contract: CI Coverage Gate

The "interface" of this feature is the `ci.yml` job graph and the artifact
contract between the `test` matrix and the `coverage` job. This document is the
authoritative shape the implementation must satisfy.

## `test` job (modified)

**Inputs**: matrix `python-version`.

**New responsibilities** (added after the existing tox test step):

1. Rename the produced data file:
   `mv .coverage ".coverage.${{ matrix.python-version }}"`.
2. Upload it as an artifact:
   - action: `actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1`
   - `name: coverage-data-${{ matrix.python-version }}`
   - `path: .coverage.${{ matrix.python-version }}`
   - `include-hidden-files: true`

**Removed**: the "Upload coverage to Codecov" step and its `CODECOV_TOKEN` env.

## `coverage` job (new)

```yaml
coverage:
  name: coverage
  needs: [test]
  if: always() && github.event_name == 'pull_request'
  runs-on: ubuntu-latest
  steps:
    - checkout (persist-credentials: false)          # repo-pinned SHA
    - setup-uv                                        # repo-pinned SHA
    - download-artifact:                              # v8.0.1 SHA
        pattern: coverage-data-*
        merge-multiple: true
    - run: |
        uv tool install coverage
        coverage combine
        coverage html --skip-covered --skip-empty
        coverage report --format=markdown >> "$GITHUB_STEP_SUMMARY" || true
        coverage report            # threshold from pyproject fail_under=60
    - upload-artifact (if: failure()):               # v7.0.1 SHA
        name: html-report
        path: htmlcov
```

**Contract guarantees**:

- Runs even if a `test` job failed (`if: always()`), so a report is always
  attempted.
- Only runs on `pull_request` (mirrors the other PR-gated jobs; no push variant).
- Exit status is failure iff aggregate coverage `< 60` (from `pyproject.toml`) or
  no data could be combined.
- Threshold is NOT written in the workflow (derived from config).

## `tests-complete` summary job (modified)

- `needs:` gains `coverage`.
- The pass/fail evaluation gains `COVERAGE_RESULT: ${{ needs.coverage.result }}`
  and requires it to be `success` alongside the existing five jobs.

## Global constraints (unchanged invariants)

- Every `uses:` is pinned to a full commit SHA with a `# vX` comment.
- `checkout` uses `persist-credentials: false`.
- `zizmor .github/workflows/` passes with no new findings.
- `lint`, `type-check`, `security`, `documentation`, and push-only `test-py315`
  are untouched.
