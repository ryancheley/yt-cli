# Implement GitHub Issue

You are helping implement a GitHub issue using the gh CLI and modern development practices. Follow this comprehensive workflow:

## 1. Issue Analysis & Setup

First, fetch and analyze the issue details:

```bash
# Fetch issue details (replace with actual issue number from $ARGUMENTS)
gh issue view $ARGUMENTS --json title,body,labels,assignees,milestone
```

**Tasks:**
- Read and understand the issue requirements thoroughly
- Identify any dependencies or related issues
- Check if the issue has proper labels and milestone
- Verify if you're assigned or should assign yourself

## 2. Branch Strategy

Create a well-named feature branch:

```bash
# Create and switch to feature branch
git checkout main
git pull origin main
gh issue develop $ARGUMENTS --checkout
# Alternative manual approach:
# git checkout -b feature/issue-$ARGUMENTS-descriptive-name
```

## 3. Implementation Planning

Before coding, create an implementation plan:

**Analyze:**
- What files need to be modified?
- Are there tests that need to be written/updated?
- Does this require database migrations?
- Are there documentation updates needed?
- What's the testing strategy?

**For Django projects specifically:**
- Models changes requiring migrations?
- New views/URLs needed?
- Template updates required?
- Admin interface changes?
- Management commands needed?

## 4. Development Process

Implement the solution following best practices:

**Code Quality:**
- Follow project coding standards
- Write comprehensive tests (unit, integration)
- Update documentation as needed
- Consider security implications
- Ensure accessibility compliance (for frontend changes)

**For Python/Django development:**
- Run `python manage.py check` for Django projects
- Execute test suite: `python manage.py test`
- Check migrations: `python manage.py makemigrations --dry-run`
- Lint code: `flake8` or `black` as per project standards

## 5. Pre-commit Validation

Before committing, validate your changes:

```bash
# Run tests
npm test  # or pytest, or python manage.py test

# Check code quality
# (adjust based on project tooling)
black . --check
flake8

# Verify build
npm run build  # or appropriate build command
```

## 6. Commit Strategy

Create meaningful, atomic commits:

```bash
# Stage changes thoughtfully
git add .

# Commit with descriptive message linking to issue
git commit -m "feat: implement feature X

- Add new functionality for Y
- Update tests for Z component
- Update documentation

Fixes #$ARGUMENTS"
```

## 7. Pull Request Creation

Create a comprehensive PR:

```bash
# Push branch
git push -u origin HEAD

# Create PR with issue auto-linking
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
# Verify issue was auto-closed
gh issue view $ARGUMENTS

# If not auto-closed, close manually with comment
gh issue close $ARGUMENTS --comment "Implemented in PR #[PR_NUMBER]"
```

## Quality Checklist

**Before PR Creation:**
- [ ] Code follows project conventions
- [ ] All tests pass locally
- [ ] Documentation updated
- [ ] No sensitive data committed
- [ ] Performance impact considered
- [ ] Accessibility requirements met (if UI changes)

**Healthcare/EHR Specific Considerations:**
- [ ] HIPAA compliance maintained
- [ ] PHI handling reviewed
- [ ] Audit logging implemented (if required)
- [ ] Data validation comprehensive
- [ ] Error handling robust

## Emergency Rollback Plan

Document rollback strategy:
- Identify database migration rollback steps
- Note any configuration changes to revert
- List dependent services to monitor

---

**Usage:** `/project:implement $ISSUE_NUMBER`

This command guides you through implementing GitHub issue #$ARGUMENTS with enterprise-grade practices suitable for healthcare engineering environments.
