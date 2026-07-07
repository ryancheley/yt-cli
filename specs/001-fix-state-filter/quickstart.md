# Quickstart / Validation: Fix State Filter

## Prerequisites

- Authenticated `yt` CLI (`yt auth login`) against a YouTrack instance that has a
  project with a multi-word workflow state (e.g. "In Progress").
- At least one issue in state "In Progress" and one issue in a different state
  whose description/comment mentions the words "in progress".

## Automated check (no network)

Run the regression test added for this fix:

```bash
uv run pytest -k "state_filter" -q
```

Expected: the test asserting the multi-word state query is brace-escaped passes.

## Manual end-to-end check

```bash
yt issues list --project-id PROJECT --state 'In Progress' --format json
```

Expected outcomes:

- Every returned issue has state exactly "In Progress" (SC-001).
- The unrelated issue that only *mentions* "in progress" in its text is NOT
  returned (SC-002).

Regression check — single-word state still works:

```bash
yt issues list --project-id PROJECT --state Open
```

Expected: only "Open" issues returned, unchanged from prior behavior (SC-003).

See [research.md](./research.md) for the escaping rationale and [plan.md](./plan.md)
for the affected code sites.
