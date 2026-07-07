# Feature Specification: Fix State Filter Returning Incorrect Issues

**Feature Branch**: `fix-state-filter-721`

**Created**: 2026-07-07

**Status**: Draft

**Input**: Issue #721 — `yt issues list --project-id PROJECT --state 'In Progress'` returns issues that don't match the requested state. Multi-word state values are not escaped, so the trailing word is treated as a free-text search matching summary/description/comments.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filter issues by a multi-word state (Priority: P1)

A user lists issues for a project and filters by a state whose name contains a
space (e.g. "In Progress", "To Verify", "Won't fix"). They expect only issues
currently in that exact state to be returned.

**Why this priority**: This is the reported defect. The filter silently returns
wrong results, which erodes trust in every filtered list and any script built on
it.

**Independent Test**: Run the list command with a multi-word `--state` value and
confirm every returned issue has that state, and that issues merely mentioning
the words in their text are excluded.

**Acceptance Scenarios**:

1. **Given** a project with issues in states "In Progress" and "Open", where one
   "Open" issue mentions "in progress" in its description, **When** the user runs
   `list --project-id P --state 'In Progress'`, **Then** only the "In Progress"
   issues are returned and the "Open" issue is excluded.
2. **Given** a state value containing a space, **When** the list command builds
   its query, **Then** the state value is treated as a single atomic filter term,
   not split into a filter term plus a free-text term.

### User Story 2 - Single-word state filtering still works (Priority: P2)

A user filters by a single-word state (e.g. "Open", "Fixed") and continues to get
correct results as before.

**Why this priority**: The fix must not regress the common single-word case.

**Independent Test**: Run the list command with a single-word `--state` value and
confirm only matching issues are returned.

**Acceptance Scenarios**:

1. **Given** issues in state "Open", **When** the user runs `list --state Open`,
   **Then** only "Open" issues are returned.

### Edge Cases

- State value with leading/trailing whitespace.
- State value already wrapped by the user in escaping characters (avoid
  double-escaping).
- Empty state value (no state filter applied).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The list command MUST return only issues whose state exactly matches
  the requested `--state` value.
- **FR-002**: The list command MUST treat a multi-word state value as a single
  atomic filter term so its words are never interpreted as free-text search.
- **FR-003**: Multi-word state filtering MUST NOT match against issue summary,
  description, or comments.
- **FR-004**: Single-word state filtering MUST continue to return the same correct
  results it did before this change.
- **FR-005**: The state filter MUST compose correctly with other filters
  (project, assignee, free-text query) already supported by the list command.

### Key Entities

- **State filter**: The user-supplied value identifying the workflow state to
  filter issues by; may contain spaces.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of issues returned for a multi-word state filter have that
  exact state.
- **SC-002**: Issues that only mention the state words in their text (and are not
  in that state) are returned 0% of the time.
- **SC-003**: Single-word state filtering results are unchanged from prior
  behavior.
- **SC-004**: A regression test covering the multi-word state case fails before
  the fix and passes after.

## Assumptions

- The underlying issue tracker supports an escaping/quoting mechanism for filter
  values that contain spaces (curly-brace escaping in YouTrack query syntax).
- The fix is scoped to the issue list/search query construction; no change to the
  CLI flag surface is required.
