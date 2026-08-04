# Phase 1 Data Model: Ditch Codecov

This feature has no application data model. The "entities" are CI jobs and the
artifacts that flow between them.

## Entities

### Per-version coverage data artifact

- **Represents**: the raw coverage measurement from one matrix `test` job.
- **Producer**: each `test` matrix job (one per Python version).
- **Fields / attributes**:
  - `name`: `coverage-data-<python-version>` (e.g. `coverage-data-3.11`,
    `coverage-data-3.14t`).
  - `contents`: a single file `.coverage.<python-version>` (renamed from
    `.coverage`; a hidden dotfile).
- **Rules**:
  - Name MUST be unique per matrix entry so multiple versions coexist in one run.
  - Upload MUST include hidden files.
  - Produced even though a job may have a lower single-version percentage than the
    aggregate (single-version pytest gate `--cov-fail-under=50` is separate).

### Aggregate coverage result

- **Represents**: the combined measurement across all versions.
- **Producer**: the `coverage` job via `coverage combine` over all downloaded
  `.coverage.*` files → a single `.coverage`.
- **Rules**:
  - Derived only from artifacts present in the run (no version numbers baked into
    the aggregation step).
  - Basis for both the summary report and the pass/fail gate.

### Coverage summary report (markdown)

- **Represents**: human-readable total, shown in the run summary.
- **Producer**: `coverage report --format=markdown >> $GITHUB_STEP_SUMMARY`.
- **Rules**: written on every `coverage`-job run (guarded so it is emitted even
  when the subsequent gate fails).

### Detailed coverage report (HTML)

- **Represents**: drill-down for diagnosing a shortfall.
- **Producer**: `coverage html --skip-covered --skip-empty` → `htmlcov/`.
- **Rules**: uploaded as an artifact **only** when the gate fails
  (`if: failure()`); absent on passing runs.

## Job graph (state / dependency transitions)

```text
test (matrix: 3.10 … 3.14t)  ──► produces coverage-data-<v> artifacts
        │
        ├──► coverage        (needs: test, if: always())
        │         combine → summary(markdown) → gate(fail_under=60 from config)
        │         └─(on failure)─► upload htmlcov artifact
        │
lint, type-check, security, documentation  (unchanged)
        │
        └──► tests-complete  (needs: test, lint, type-check, security,
                              documentation, coverage; if: always())
                              passes only if ALL results == success
```

Removed: `coverage-baseline` (push-only; existed solely for Codecov baseline).
Unchanged: `test-py315` (push-only prerelease early-warning).
