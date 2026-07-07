# Research: Fix State Filter Returning Incorrect Issues

## Decision: Escape multi-word filter values with YouTrack curly braces

**Decision**: Wrap the `state` value in curly braces when composing the query:
`State: {In Progress}`. Apply the same escaping at every site that builds a
`state:` filter term from user input.

**Rationale**: YouTrack's query language treats whitespace as a token separator.
`State: In Progress` is parsed as the attribute filter `State: In` followed by a
free-text term `Progress`, which matches summary/description/comments — exactly
the reported defect. YouTrack's documented mechanism for a value containing
spaces is curly-brace escaping: `State: {In Progress}` binds the whole value to
the `State` attribute. Braces around a single-word value (`State: {Open}`) are
also valid and harmless, so always-wrapping keeps the code branch-free.

**Alternatives considered**:
- **Quote with double quotes** (`State: "In Progress"`): YouTrack treats quoted
  text as a full-text phrase, not an attribute-value binding — wrong semantics.
- **Only escape when a space is present**: adds a conditional for no benefit;
  braces are safe on single-word values, so always-wrap is simpler and correct.
- **URL/percent encoding**: irrelevant — the problem is query *parsing*, not HTTP
  transport; the HTTP client already encodes params.

## Decision: Fix at both query-construction sites (root cause, not symptom)

**Decision**: Apply escaping in `youtrack_cli/managers/issues.py`
(`IssueManager.list_issues`, the path the live `yt issues list` command uses) and
in `youtrack_cli/issues.py` (`IssueClient.list_issues`), since both build a
`state:` term from raw user input and share the identical defect.

**Rationale**: The ticket names the `list` command (manager path), but the legacy
`IssueClient` path constructs the same broken `state:{state}` string. Fixing only
the reported path leaves the sibling caller broken. A single shared escaping
helper applied at both sites is the smallest change that fixes the root cause
everywhere.

**Alternatives considered**:
- **Patch only the manager path**: smaller diff, but leaves `issues.py` latent
  bug — rejected.
- **Escape inside the low-level service/HTTP layer**: too broad; would risk
  double-escaping user-supplied raw `--query` strings that intentionally contain
  YouTrack syntax — rejected.

## Verification approach

Regression test asserts the composed query for a multi-word state contains the
brace-escaped term (`{In Progress}`) and does not leave a bare trailing word that
YouTrack would treat as free text. Test fails before the fix, passes after
(Constitution II).
