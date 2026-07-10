# Phase 0 Research: Security fixes #740–#743

**Feature**: 003-security-fixes | **Date**: 2026-07-09

## R1. #740 — Sanitize server-supplied attachment filename

**Decision**: In `commands/articles.py download`, when `--output` is not given,
derive the local name with `Path(filename).name` (strips all directory
components). If that yields an empty/unsafe name (`""`, `.`, `..`), fall back to
`f"attachment_{attachment_id}"`. Keep the explicit `--output` path as-is (user's
own trusted choice).

**Rationale**: `Path(filename).name` neutralizes both relative traversal
(`../../x` → `x`) and absolute paths (`/etc/x` → `x`) in one stdlib call — the
minimal, correct fix. Confining to CWD matches today's behavior. This mirrors
the already-safe pattern used by `yt issues attach download`
(`attachment_{attachment_id}` default).

**Alternatives considered**: `os.path.basename` (equivalent; `Path.name` is the
project idiom). Full `resolve()`-and-prefix-check (more code; `.name` already
guarantees no separators so a prefix check is redundant for the no-`--output`
path).

## R2. #741 — Warn on cleartext (`http://`) base URL

**Decision**: Add a small helper in `auth.py`, e.g.
`warn_if_insecure_url(base_url)`, that prints a Rich-styled warning to stderr
when the URL scheme is `http`. Call it from `verify_credentials()` (the
chokepoint hit during interactive `yt auth login` and explicit verification)
before the request is made. Warn-only; the request proceeds (per Clarifications).

**Rationale**: `verify_credentials` is the single point every interactive login
and verification passes through, so one call covers the "authenticate" paths
without touching every request. Warn-only keeps `http://localhost` and on-prem
plain-HTTP working (single-user threat model), while making each cleartext send
visible. Scheme parsed with `urllib.parse.urlparse` (stdlib) rather than a
fragile `startswith`.

**Alternatives considered**:
- Warn inside the HTTP client on every request — highest coverage but noisy
  (repeats per call). Rejected for warn-fatigue.
- Warn only in the `main.py` login command — misses the programmatic
  `verify_credentials` path. Rejected.
- Hard-reject / opt-in flag — rejected by the user in Clarifications (warn-only).

## R3. #742 — Remove `shell=True` from the tutorial executor

**Decision**: In `executor.py`, change `_execute_via_subprocess` to build an
argv list via the existing `parse_command()` (which already uses `shlex.split`)
and run `asyncio.create_subprocess_exec("yt", *args, …)` instead of
`create_subprocess_shell(command, shell=True)`. Keep `is_command_allowed()` as a
tutorial-scope UX filter but note it is no longer the security boundary — with
`exec`, shell metacharacters are inert. Remove (or convert) the dead
`_execute_command` in `core.py` that also uses `shell=True`.

**Rationale**: `create_subprocess_exec` passes arguments directly to the process
without a shell, so `;`, `&&`, `$(...)`, backticks carry no meaning — this is the
real fix, and the code already parses commands into args, so it's a small
change. Invoking the installed `yt` entrypoint with the parsed args preserves
current behavior.

**Alternatives considered**: Tightening the whitelist to exact-match — still
leaves `shell=True` as a latent sink; rejected. Executing Click in-process
(the file's own TODO) — larger change than warranted for a hardening fix;
deferred.

**To verify during implement**: confirm `core.py::_execute_command` is truly
uncalled before deleting (grep showed only its definition; the live path is
`executor.execute_command`).

## R4. #743 — SECURITY.md

**Decision**: Add `SECURITY.md` at repo root describing: private reporting
channel (GitHub Private Vulnerability Reporting and/or maintainer email),
response-time expectation, coordinated-disclosure window, and supported
versions.

**Rationale**: Standard, discoverable location; GitHub surfaces it in the
Security tab and the "Report a vulnerability" UI. Lowest-effort closure of the
process gap.

**Alternatives considered**: `.github/SECURITY.md` (equivalent; root is fine and
more visible). Enabling GitHub Private Vulnerability Reporting is a repo setting
the maintainer can toggle; the file will reference it.

## R5. Testing approach (FR-009)

**Decision**: One regression test per behavioral fix, real-object style:
- **#740**: invoke the download command (via Click `CliRunner` or the manager)
  with the remote boundary returning `filename="../../pwned"`; assert the file
  lands at `tmp_path/pwned` and nothing is written outside `tmp_path`. Mock only
  the network `download_attachment` result (justified boundary mock).
- **#741**: call `warn_if_insecure_url("http://example")` and assert a warning is
  emitted; assert no warning for `https://`. Pure real-object.
- **#742**: drive the executor with a metacharacter command and assert no
  secondary effect (e.g. a sentinel file is NOT created), and/or assert
  `create_subprocess_exec` is used. Prefer the observable-side-effect assertion.

**Rationale**: Matches constitution II (real objects; mock only the un-driveable
remote boundary). Each test fails before its fix and passes after.
