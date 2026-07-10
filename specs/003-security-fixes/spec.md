# Feature Specification: Remediate four security findings (#740–#743)

**Feature Branch**: `security-fixes-740-743`

**Created**: 2026-07-09

**Status**: Draft

**Input**: User description: "Fix four security findings in the YouTrack CLI (#740 path traversal on article attachment download, #741 cleartext HTTP base URL, #742 tutorial executor shell=True hardening, #743 add SECURITY.md). Threat model: single-user local install — remote/network threats in scope, local-user file-permission threats out of scope."

## Clarifications

### Session 2026-07-09

- Q: When a user configures an `http://` (non-TLS) base URL, how should the CLI
  behave to prevent silently sending the token in cleartext (#741)? → A: Warn
  only, still proceed — print a clear cleartext warning to stderr and continue
  the request. No blocking, no opt-in flag. The point is that transmission is no
  longer *silent*; the user is informed each time.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Safe attachment download (Priority: P1)

A user downloads an attachment from a YouTrack article. The attachment's
filename is chosen by whoever uploaded it — potentially an attacker or a
compromised server. The user expects the file to land in their working
directory under a safe name, never outside it.

**Why this priority**: #740 is the highest-impact finding — the untrusted input
(server-supplied filename) reaches a file-write sink and can escape the intended
directory (`../../.bashrc`, absolute paths). It is remotely influenced, squarely
in the threat model.

**Independent Test**: Simulate a download where the server returns a filename
containing path-traversal sequences; confirm the file is written only inside the
intended directory under a sanitized base name, and a traversal attempt is
refused or neutralized.

**Acceptance Scenarios**:

1. **Given** a server response whose attachment filename is `../../evil.sh`,
   **When** the user runs `yt articles attach download` without `--output`,
   **Then** the file is written inside the working directory under the bare
   name `evil.sh` (no directory escape).
2. **Given** a server filename that is an absolute path (`/tmp/evil` or
   `/etc/cron.d/x`), **When** downloaded, **Then** the write stays within the
   intended directory and does not target the absolute location.
3. **Given** a normal filename (`report.pdf`), **When** downloaded, **Then**
   behavior is unchanged — the file is saved as `report.pdf`.

---

### User Story 2 - No silent cleartext credentials (Priority: P2)

A user configures the CLI with a base URL. If they supply an insecure
`http://` URL, the API token would otherwise be transmitted in cleartext and be
capturable by a network attacker. The user should be stopped or clearly warned
before that happens.

**Why this priority**: #741 protects the credential in transit against a
network (MITM) attacker — in scope for the threat model. Slightly lower than
#740 because it requires a network-position attacker and an insecure URL choice.

**Independent Test**: Attempt login/verification with an `http://` base URL and
confirm the CLI surfaces the insecurity (blocks by default, or requires an
explicit opt-in) rather than silently proceeding.

**Acceptance Scenarios**:

1. **Given** a user provides an `http://` base URL, **When** they log in or
   verify credentials, **Then** the CLI prints a clear cleartext-transmission
   warning before sending the token (warn-only; the request still proceeds).
2. **Given** a user provides an `https://` base URL, **When** they log in,
   **Then** behavior is unchanged (no new friction).
3. **Given** a user provides a bare host with no scheme, **When** they log in,
   **Then** it continues to default to `https://` as today.

---

### User Story 3 - Tutorial runs without a shell (Priority: P3)

A user runs an interactive tutorial that executes example CLI commands. Those
commands should run without invoking a system shell, so shell metacharacters
carry no meaning and the executor is not a latent injection sink.

**Why this priority**: #742 is defense-in-depth. The commands are currently
hardcoded, so it is not externally exploitable today, but removing `shell=True`
and the bypassable whitelist prevents a future regression from becoming an RCE.

**Independent Test**: Run a tutorial step that executes its example command and
confirm it still works; confirm the executor no longer invokes a shell and that
shell metacharacters in a command string are not interpreted.

**Acceptance Scenarios**:

1. **Given** a tutorial step with a normal example command, **When** the user
   chooses to execute it, **Then** the command runs and its output is shown, as
   before.
2. **Given** a command string containing shell metacharacters (`;`, `&&`,
   `$(...)`), **When** executed by the tutorial executor, **Then** the
   metacharacters are treated as literal arguments, not shell operators — no
   secondary command runs.
3. **Given** the previously dead shell-executing code path, **When** the change
   is complete, **Then** it no longer invokes a system shell (removed or
   converted).

---

### User Story 4 - Clear vulnerability reporting path (Priority: P4)

A security researcher who finds a vulnerability needs a documented, private way
to report it instead of opening a public issue.

**Why this priority**: #743 is a process gap, lowest severity, but cheap and
valuable for responsible disclosure.

**Independent Test**: Confirm a discoverable policy file exists describing a
private reporting channel and expectations.

**Acceptance Scenarios**:

1. **Given** a researcher looks for how to report a vulnerability, **When** they
   check the repository, **Then** they find a `SECURITY.md` describing a private
   channel, response expectations, and supported versions.

---

### Edge Cases

- Server filename that is empty, `.`, `..`, or all path separators → must
  resolve to a safe, non-empty local name and never escape the directory.
- Server filename containing a mix of separators or URL-encoded traversal → the
  sanitized name must still be confined.
- `--output` explicitly provided by the user → this is the user's own choice on
  their single-user machine and remains honored (out-of-scope for traversal
  hardening, which targets the *server-supplied* name).
- `http://localhost` / `http://127.0.0.1` for local dev → the insecure-URL
  handling should still make the user aware, though this is a common legitimate
  case (the reject-vs-warn decision governs behavior here).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When saving a downloaded article attachment using the
  server-supplied filename, the system MUST strip any directory components and
  write only within the intended target directory; a filename containing
  traversal sequences or absolute paths MUST NOT cause a write outside that
  directory.
- **FR-002**: Normal attachment filenames MUST continue to download with
  unchanged behavior and naming.
- **FR-003**: When a user configures or authenticates against an `http://`
  (non-TLS) base URL, the system MUST emit a clear cleartext-transmission
  warning (to stderr) before proceeding, so the token is never sent silently.
  The request still proceeds (warn-only; no blocking, no opt-in flag).
- **FR-004**: `https://` base URLs and bare hosts (defaulted to `https://`)
  MUST continue to work without added friction.
- **FR-005**: The tutorial command executor MUST execute example commands
  without invoking a system shell, so that shell metacharacters are not
  interpreted.
- **FR-006**: The bypassable prefix-based command allowlist MUST no longer be
  relied upon as the safety mechanism; any dead shell-executing code path MUST
  be removed or converted to non-shell execution.
- **FR-007**: Executing a normal tutorial example command MUST continue to
  produce the same user-visible result as before.
- **FR-008**: The repository MUST include a discoverable security policy
  (`SECURITY.md`) documenting a private vulnerability-reporting channel,
  response expectations, and supported versions.
- **FR-009**: Each behavioral fix (FR-001, FR-003, FR-005) MUST be covered by an
  automated regression test that fails before the fix and passes after.

### Key Entities

- **Server-supplied attachment filename**: Untrusted string from a YouTrack API
  response used to name a downloaded file. Must be treated as hostile input.
- **Base URL**: The configured YouTrack instance address; its scheme
  (`http`/`https`) determines whether credentials travel in cleartext.
- **Tutorial example command**: A hardcoded command string a tutorial step can
  execute on the user's behalf.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of attachment downloads whose server-supplied filename
  contains traversal sequences or absolute paths are written inside the intended
  directory (0 escapes), verified by regression tests.
- **SC-002**: Every configuration or authentication against an `http://` base
  URL emits a visible cleartext warning before the token is sent (0 silent
  cleartext transmissions; warning shown 100% of the time).
- **SC-003**: The tutorial executor invokes no system shell; a command string
  with shell metacharacters produces 0 secondary command executions.
- **SC-004**: A `SECURITY.md` disclosure policy is present and discoverable.
- **SC-005**: All existing tests continue to pass and new regression tests for
  the three behavioral fixes pass, with no regression in normal (safe-input)
  behavior.

## Assumptions

- Threat model is a single-user local install: remote/network-influenced inputs
  (server filenames, cleartext transport) are in scope; local-user filesystem
  permission isolation is explicitly out of scope (per the deleted #739). See
  the project threat-model memory.
- The intended target directory for a downloaded attachment (when `--output` is
  not given) is the current working directory, matching today's behavior.
- The user's explicit `--output` path is trusted (their own choice on their own
  machine) and is not subject to the traversal hardening.
- The `http://` behavior is resolved (see Clarifications): warn-only, the
  request still proceeds. This intentionally keeps `http://localhost` and
  on-prem plain-HTTP instances working while making each cleartext send visible.
- The tutorial executor already parses commands into an argument list, which the
  non-shell execution can reuse.
