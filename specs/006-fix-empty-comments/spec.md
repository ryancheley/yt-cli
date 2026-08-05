# Feature Specification: Listing comments for issues with no comments

**Feature Branch**: `006-fix-empty-comments-768`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "Fix issue #768: `cat issues.txt | yt issues comments list` fails with 'Event loop is closed' RuntimeError when an issue in the piped input has no comments. Listing comments for an issue that has zero comments should succeed and simply show no comments, both for single issues and when processing multiple issue IDs from stdin."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List comments for an issue that has none (Priority: P1)

A user runs the comment-list command against a single issue that happens to have no comments. Instead of an error, they see a clear indication that the issue has no comments and the command exits successfully.

**Why this priority**: This is the core defect. An empty comment set is a normal, expected state and must never be treated as a failure.

**Independent Test**: Run the comment-list command for one issue known to have zero comments and confirm it exits successfully with a "no comments" message and no error output.

**Acceptance Scenarios**:

1. **Given** an issue with zero comments, **When** the user lists its comments, **Then** the command reports that there are no comments and exits with a success status.
2. **Given** an issue with one or more comments, **When** the user lists its comments, **Then** the existing behavior is unchanged and all comments are displayed.

---

### User Story 2 - List comments for multiple issues piped from stdin (Priority: P1)

A user pipes a list of issue IDs into the comment-list command (e.g. `cat issues.txt | yt issues comments list`). Some issues in the list have comments and some do not. Every issue is processed to completion, regardless of which ones have no comments.

**Why this priority**: This is the exact reported reproduction. A single empty-comment issue in the batch currently aborts processing with an "Event loop is closed" error.

**Independent Test**: Pipe a list of several issue IDs, at least one of which has no comments, and confirm every issue is processed and the command exits successfully without an "Event loop is closed" error.

**Acceptance Scenarios**:

1. **Given** a piped list of issue IDs where at least one issue has no comments, **When** the user lists comments, **Then** each issue's comments (or "no comments" state) are shown and the command completes successfully.
2. **Given** a piped list where every issue has no comments, **When** the user lists comments, **Then** each issue is reported as having no comments and the command exits successfully.

---

### Edge Cases

- What happens when the very first issue in a piped batch has no comments? Processing must continue to subsequent issues.
- What happens when an issue ID in the batch is invalid or not found? That is a distinct error condition and is out of scope for this fix; empty-comment handling must not mask genuine lookup errors.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST treat an issue with zero comments as a successful, non-error outcome when listing comments.
- **FR-002**: The system MUST display a clear "no comments" indication for an issue that has no comments.
- **FR-003**: The system MUST process every issue ID supplied via stdin, even when one or more of those issues have no comments.
- **FR-004**: The system MUST NOT emit an "Event loop is closed" error (or any internal runtime error) as a result of an issue having no comments.
- **FR-005**: The system MUST exit with a success status when all requested issues are processed, including when some or all have no comments.
- **FR-006**: The system MUST preserve existing behavior for issues that do have comments.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Listing comments for an issue with zero comments succeeds 100% of the time with no error output.
- **SC-002**: Piping a batch of issue IDs that includes empty-comment issues processes 100% of the issues and exits successfully.
- **SC-003**: Zero occurrences of "Event loop is closed" errors across the empty-comment scenarios.
- **SC-004**: No regression in the displayed output for issues that have comments.

## Assumptions

- The "no comments" state is a normal condition, distinct from an issue-not-found or authentication error.
- The fix targets the comment-listing path only; other commands are out of scope.
- Existing output formatting for populated comment lists is considered correct and should be retained.
