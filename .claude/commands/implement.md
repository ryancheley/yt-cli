# Implement GitHub Issue(s)

You are helping implement one or more GitHub issues using the gh CLI and modern development practices. Follow this comprehensive workflow:

## 1. Issue Analysis & Setup

First, fetch and analyze the issue details:

```bash
# Fetch issue details for each issue number provided
for issue in $ARGUMENTS; do
    echo "=== Issue #$issue ==="
    gh issue view $issue --json title,body,labels,assignees,milestone
    echo
done
```

**Tasks:**
- Read and understand the requirements for each issue thoroughly
- Identify any dependencies or related issues
- Check if each issue has proper labels and milestone
- Verify if you're assigned or should assign yourself
- If multiple issues are provided, determine if they should be implemented together or separately

## 2. Branch Strategy

Create a well-named feature branch:

```bash
# Create and switch to feature branch
git checkout main
git pull origin main

# For single issue:
if [ $(echo $ARGUMENTS | wc -w) -eq 1 ]; then
    gh issue develop $ARGUMENTS --checkout
else
    # For multiple issues, create descriptive branch name
    ISSUES=$(echo $ARGUMENTS | tr ' ' '-')
    git checkout -b feature/issues-$ISSUES-implementation
fi
```

## 3. Implementation Planning

Before coding, create an implementation plan:

**Analyze:**
- What files need to be modified?
- Are there tests that need to be written/updated?
- Are there documentation updates needed?
- What's the testing strategy?

## 4. Development Process

Implement the solution following best practices:

**Code Quality:**
- Follow project coding standards
- Write comprehensive tests (unit, integration)
- Update documentation as needed
- Consider security implications

**adding or updated new commands:**
- install CLI using `uv pip install -e .`
- use the command `source .env.local && yt auth login --token $YOUTRACK_API_KEY --base-url $BASE_URL` to authenticate
- prepend all cli commands with `source .env.local && ` to ensure that they work as expected and have no errors
- run the commands to make sure they function as expected
- use the `FPU` project for all testing
- When working on a custom field, the documentation is available [here](https://www.jetbrains.com/help/youtrack/devportal/api-how-to-update-custom-fields-values.html)

## 5. Pre-commit Validation

Before committing, validate your changes:

```bash
# Check the pre-commit status
pre-commit run
```

## 6. Commit Strategy

Create meaningful, atomic commits:

```bash
# Stage changes thoughtfully
git add .

# Commit with descriptive message linking to issue(s)
# For single issue:
if [ $(echo $ARGUMENTS | wc -w) -eq 1 ]; then
    git commit -m "feat: implement feature X

- Add new functionality for Y
- Update tests for Z component
- Update documentation

Fixes #$ARGUMENTS"
else
    # For multiple issues, reference all of them
    FIXES_LINE=$(echo $ARGUMENTS | sed 's/\([0-9]\+\)/#\1/g' | sed 's/ /, /g')
    git commit -m "feat: implement features for multiple issues

- Add new functionality for Y
- Update tests for Z component
- Update documentation

Fixes $FIXES_LINE"
fi
```

## 7. Pull Request Creation

Create a comprehensive PR:

```bash
# Push branch
git push -u origin HEAD

# Create PR with issue auto-linking
if [ $(echo $ARGUMENTS | wc -w) -eq 1 ]; then
    gh pr create \
      --title "Implement: [Brief description] (Fixes #$ARGUMENTS)" \
      --body "## Summary

Brief description of changes made.

## Changes Made
- List key changes
- Include any breaking changes
- Note migration requirements

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] Security review completed (if applicable)

## Documentation
- [ ] Code comments added where needed
- [ ] Documentation updated
- [ ] Changelog updated (if applicable)

Fixes #$ARGUMENTS" \
      --assignee "@me" \
      --label "enhancement"
else
    # For multiple issues
    FIXES_LINE=$(echo $ARGUMENTS | sed 's/\([0-9]\+\)/#\1/g' | sed 's/ /, /g')
    TITLE_ISSUES=$(echo $ARGUMENTS | sed 's/ /, #/g')
    gh pr create \
      --title "Implement: [Brief description] (Fixes #$TITLE_ISSUES)" \
      --body "## Summary

Brief description of changes made.

## Related Issues
This PR addresses the following issues:
$(for issue in $ARGUMENTS; do echo "- #$issue"; done)

## Changes Made
- List key changes
- Include any breaking changes
- Note migration requirements

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] Security review completed (if applicable)

## Documentation
- [ ] Code comments added where needed
- [ ] Documentation updated
- [ ] Changelog updated (if applicable)

Fixes $FIXES_LINE" \
      --assignee "@me" \
      --label "enhancement"
fi
```

## 8. Post-PR Actions

After creating the PR:

**Immediate:**
- Request reviews from appropriate team members
- Update issue with PR link if not auto-linked
- Check CI/CD pipeline status

**Follow-up:**
- Address review feedback promptly
- Update PR description if scope changes
- Merge when approved and CI passes

## 9. Issue Closure Verification

After merge:

```bash
# Verify each issue was auto-closed
for issue in $ARGUMENTS; do
    echo "Checking issue #$issue..."
    gh issue view $issue

    # If not auto-closed, close manually with comment
    if gh issue view $issue --json state -q .state | grep -q "OPEN"; then
        gh issue close $issue --comment "Implemented in PR #[PR_NUMBER]"
    fi
done
```

## Quality Checklist

**Before PR Creation:**
- [ ] Code follows project conventions
- [ ] All tests pass locally
- [ ] Documentation updated
- [ ] No sensitive data committed
- [ ] Performance impact considered
- [ ] Accessibility requirements met (if UI changes)

## Emergency Rollback Plan

Document rollback strategy:
- Identify database migration rollback steps
- Note any configuration changes to revert
- List dependent services to monitor

---

**Usage:**
- Single issue: `/project:implement $ISSUE_NUMBER`
- Multiple issues: `/project:implement $ISSUE_NUMBER1 $ISSUE_NUMBER2 ...`

This command guides you through implementing one or more GitHub issues with enterprise-grade practices suitable for healthcare engineering environments. When multiple issues are provided, the command will help you implement them together in a single branch and PR, referencing all issues appropriately.
