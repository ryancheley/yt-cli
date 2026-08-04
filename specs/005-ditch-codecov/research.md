# Phase 0 Research: Ditch Codecov

## R1 — Where does coverage data land after a `tox` run, and how many files?

**Finding**: A local `pytest` (same invocation tox uses) leaves a **single**
`.coverage` file in the repo root. `pytest-cov` auto-combines subprocess data
into one file per run even with `[tool.coverage.run] parallel = true`.

**Decision**: Each matrix job produces one `.coverage`. To aggregate across jobs
we must give each job's file a **unique** name before upload, otherwise
`download-artifact` with `merge-multiple: true` would overwrite identically named
files.

**Approach**: `mv .coverage ".coverage.${{ matrix.python-version }}"` after the
test step, then upload. `coverage combine` auto-discovers any `.coverage.*` file,
so the renamed files combine without extra arguments.

**Alternatives considered**: Rename to a non-hidden name (e.g.
`coverage-3.11.dat`) — rejected because `coverage combine` only auto-discovers the
`.coverage.*` prefix; we'd have to pass explicit paths.

## R2 — Uploading hidden coverage files as artifacts

**Finding**: `actions/upload-artifact` excludes hidden (dot-prefixed) files by
default. `.coverage.<version>` is a dotfile.

**Decision**: Set `include-hidden-files: true` on the upload step (supported in
current `upload-artifact`).

## R3 — Correct, current SHA pins for the artifact actions

**Finding** (via `gh api repos/<a>/releases/latest` — the latest tags are
lightweight, so the ref SHA is the commit SHA):

- `actions/upload-artifact` → `v7.0.1` → `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`
- `actions/download-artifact` → `v8.0.1` → `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c`

These match Hynek's snippet and are current. Existing jobs' pins are reused for
`checkout` (`3d3c42e5…` v4) and `setup-uv` (`c771a70e…` v4) for consistency and a
smaller `zizmor` surface.

**Decision**: Pin exactly those SHAs with a trailing `# vX.Y.Z` comment (repo
convention).

## R4 — Deriving the threshold from config, not hardcoding

**Finding**: `pyproject.toml` has `[tool.coverage.report] fail_under = 60`.
`coverage report` reads `fail_under` from that config automatically and exits
non-zero when below it.

**Decision**: The enforcing command is a bare `coverage report` (no
`--fail-under`), so the gate stays in sync with `pyproject.toml`. The markdown
summary line uses `coverage report --format=markdown` and is guarded with
`|| true` so the summary is always written even on a failing run; the following
bare `coverage report` produces the actual pass/fail.

**Rationale**: Satisfies FR-009 ("derive threshold from existing config, not a
hardcoded number") and keeps a single source of truth.

## R5 — Cross-job source path alignment for `coverage report`

**Finding**: Coverage data stores absolute source paths. All matrix jobs and the
`coverage` job run on `ubuntu-latest` and check out to the identical path
(`/home/runner/work/yt-cli/yt-cli`), so combined data maps back to the checked-out
sources without remapping.

**Decision**: No `[tool.coverage.paths]` remapping needed. **Risk/mitigation**: if
a future runner path change makes `coverage report` show 0%/missing files, add a
`[tool.coverage.paths]` section. Noted in quickstart as the diagnostic.

## R6 — Which Python runs the `coverage` tool

**Finding**: `uv tool install coverage` provisions its own recent Python;
`coverage report` parses source to count executable lines, so it should run on a
Python new enough to understand the codebase's syntax. uv's default (latest
stable) satisfies this.

**Decision**: In the `coverage` job, `setup-uv` + `uv tool install coverage`; no
separate `actions/setup-python` step (fewer steps, smaller audit surface). Coverage
data format is stable across 7.x, so tool-vs-producer minor version skew is safe.

## R7 — Keeping the gate from being skipped on test failure

**Finding**: Spec requires the report to always run (FR-005) while still failing
the overall run when a test job fails.

**Decision**: `coverage` job uses `needs: [test]` + `if: always()`. Because the
matrix `test` job remains a dependency of `tests-complete`, a failing test job
still fails the summary gate independently of the `coverage` job's result.

## R8 — Removing the `coverage-baseline` job

**Finding**: `coverage-baseline` runs only on `push` and exists solely to
re-upload coverage to Codecov for the default-branch baseline. With Codecov gone
it has no remaining purpose (the `test-py315` push job is unrelated and stays).

**Decision**: Delete the `coverage-baseline` job entirely (FR-002). PR runs
compute and gate coverage; no default-branch baseline is needed.

## R9 — Residual Codecov references

**Finding**: The only **functional** Codecov reference is
`.github/workflows/ci.yml`. Other `grep -ri codecov` matches are historical and
must be left alone: `CHANGELOG.md` (release history) and
`specs/002-ci-py315-speedup/research.md` (a past spec). The `.specify/feature.json`
and `specs/005-ditch-codecov/` matches are just the substring in this feature's
directory name. There is **no** Codecov badge in `README.md` and no
`CODECOV_TOKEN` outside `ci.yml`.

**Decision**: Only edit `ci.yml`. SC-001 verification is scoped to functional
config: `grep -ri codecov .github README.md` returns nothing after the change.
Historical mentions in `CHANGELOG.md`/old specs are intentionally preserved.
