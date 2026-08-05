# Phase 0 Research: Empty-comment "Event loop is closed" bug (#768)

## Root cause

- `youtrack_cli/commands/issues.py:1392-1396`: `list_issue_comments` loops over the
  collected issue IDs and calls `asyncio.run(issue_manager.list_comments(issue_id))`
  **once per iteration**.
- `asyncio.run()` creates a new event loop, runs the coroutine, then **closes** that loop.
- `youtrack_cli/client.py` `HTTPClientManager` is a module-level **singleton**
  (`_client_manager`) holding one `httpx.AsyncClient`. `_ensure_client` only recreates it
  when `self._client is None or self._client.is_closed` — there is **no event-loop
  affinity check**.
- Iteration 1 creates the client and a keep-alive connection pool bound to loop #1, then
  loop #1 is closed. Iteration 2+ reuses that client/pool on a fresh loop. When httpx
  tears down a pooled connection (`_response_closed → aclose → transport.close →
  loop.call_soon`), it calls into the **closed** loop → `RuntimeError: Event loop is closed`.

## Why it appeared on a no-comment issue

Nondeterministic: the empty-comment response is simply where httpx decided to close the
pooled connection (e.g. server `Connection: close`, or pool churn between loops). The
comment count is not causal — the multi-`asyncio.run` batch is. Confirmed by grepping
`youtrack_cli/commands/issues.py`: `list_issue_comments` is the **only** command that runs
`asyncio.run` inside a `for` loop over multiple IDs; every other command calls it once.

## Decision

- **Decision**: Add **event-loop affinity** to `HTTPClientManager._ensure_client`
  (`youtrack_cli/client.py`). Record the loop the client/lock were created on; when
  `_ensure_client` runs on a *different* running loop (e.g. a subsequent `asyncio.run()`),
  drop the stale client and recreate the client **and** its `asyncio.Lock` on the current
  loop before use.
- **Rationale**: Every network call routes through `_ensure_client`. Guarding once at that
  chokepoint fixes this bug and any future cross-loop reuse, needs **no change to the
  command** or its display/JSON logic, and does **not** disturb the existing comment-list
  test suite (which mocks `asyncio.run` per issue and asserts `call_count == 2`).
- **Alternatives considered**:
  - *Run the whole batch inside a single `asyncio.run()` in `list_issue_comments`*: also
    valid and removes the per-item-loop anti-pattern, but it reshuffles the command's
    fetch-vs-display structure and forces rewriting ~5 existing tests' mock shapes and the
    `call_count == 2` assertion. Larger, noisier diff than the shared-chokepoint guard.
    Rejected.
  - *Call `reset_client_manager_sync()` between iterations*: papers over the anti-pattern,
    forces reconnect per issue (slower), still fragile. Rejected.

## Implementation notes

- The `asyncio.Lock` created in `__init__` binds lazily to the first loop it is awaited on;
  reusing it on a later loop raises "got Future attached to a different loop". So the guard
  must recreate the **lock** alongside the client on a loop change — not just the client.
- The abandoned client is bound to an already-closed loop, so its connections are inert;
  for a short-lived CLI process, dropping the reference (no `aclose`) is acceptable. Mark
  with a `ponytail:` comment naming the ceiling.
- The loop-affinity check is synchronous (no `await`), so it completes atomically w.r.t.
  other coroutines on the same loop — the double-checked creation lock stays correct.
- Empty-comment display already works: `display_comments_table([])` renders an empty table
  and JSON emits `[]`. No display change needed.
