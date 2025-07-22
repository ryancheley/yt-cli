# Help Text Style Guide

This document defines the standardized help text formatting patterns for YouTrack CLI commands.

## Overview

Consistent help text improves user experience by:
- Reducing cognitive load with predictable patterns
- Providing clear guidance for common use cases
- Maintaining professional appearance across all commands
- Enabling efficient learning and discovery

## Standard Help Text Structure

### For Command Groups (e.g., `yt issues`, `yt auth`)

```
Brief description - what this command group does

Longer description explaining the purpose and scope of the command group.
This should help users understand when to use commands in this group.

Common Examples:
    # Most common use case with brief comment
    yt command example1

    # Second most common use case
    yt command example2 --option value

    # Third most common pattern
    yt command example3 --option1 value1 --option2 value2

Command Categories:
    Core Operations: create, list, update, delete
    Advanced Features: search, batch, export
    Management: configure, permissions
```

### For Individual Commands (e.g., `yt issues create`)

```
Brief description - what this command does.

Longer description explaining the command's purpose and how it fits into typical workflows.
Include guidance on when to use this command and any important context.

Common Examples:
    # Most common use case
    yt command basic-example

    # Common use case with options
    yt command example --option value

    # Advanced use case
    yt command complex-example --option1 value1 --option2 value2

Tip: Brief guidance on key options or common gotchas.
```

## Formatting Standards

### Section Headers
- Use consistent section names: "Common Examples", "Command Categories", "Tip"
- Always use title case for section headers
- Add blank lines before and after sections

### Examples
- Always start with `# Comment explaining the example`
- Use realistic, actionable examples that users can copy-paste
- Show progression from simple to complex usage
- Use consistent project IDs (WEB-123, API-456, INFRA-789)
- Use realistic names (john.doe, admin) and values

### Comments
- Keep example comments brief but descriptive
- Focus on the "why" or "when" rather than just describing syntax
- Use lowercase for comment text (except proper nouns)

### Command Formatting
- Use full command names in examples (not aliases)
- Break long commands using backslash continuation `\`
- Align options for readability in multi-line examples

## Content Guidelines

### Tone and Voice
- **Helpful and Friendly**: Use encouraging language
- **Professional**: Avoid slang, maintain consistent terminology
- **Concise**: Every word should add value
- **Action-Oriented**: Focus on what users can accomplish

### Example Selection
Choose examples that are:
1. **Representative** - Cover the most common 80% of use cases
2. **Practical** - Users should be able to use them immediately
3. **Progressive** - Start simple, build complexity
4. **Complete** - Include all necessary context (project IDs, etc.)

### Tips and Guidance
- Include a "Tip" section for commands with common confusion points
- Highlight the most important options users should know about
- Mention related commands when relevant
- Point users to project-specific considerations (types, priorities)

## Examples by Command Type

### High-Traffic Commands (issues create, issues list, auth login)
- **Extra detail** in descriptions
- **More examples** (3-4 common patterns)
- **Explicit tips** about common mistakes
- **Context** about how the command fits into workflows

### Specialized Commands (admin, boards)
- **Clear scope** definition
- **Prerequisites** mentioned in description
- **Fewer examples** (2-3 focused patterns)
- **Links** to related commands or documentation

### Utility Commands (config, completion)
- **Brief descriptions**
- **One clear example** per major use case
- **Focus** on practical application

## Anti-Patterns to Avoid

### ❌ Information Overload
```
# DON'T: Show every possible option without guidance
Options:
  --option1 OPTION1    Description of option1
  --option2 OPTION2    Description of option2
  [... 15 more options ...]
```

### ❌ Inconsistent Example Formats
```
# DON'T: Mix different comment styles
Examples:
    yt command example1  # This style
    // yt command example2  - And this style
    /* yt command example3 */  -- And this one
```

### ❌ Abstract Examples
```
# DON'T: Use placeholder values that can't be used directly
yt issues create <PROJECT> "<SUMMARY>" --type <TYPE>
```

### ❌ No Context
```
# DON'T: Just list what the command does without explaining when/why
"""Update an issue."""
```

## ✅ Best Practices

### Progressive Disclosure
```
# Start with most common use case
yt issues list --assignee me

# Then show common variations
yt issues list --project-id WEB --state Open

# Finally show advanced usage
yt issues list --query "priority:Critical assignee:me" --format json
```

### Realistic Examples
```
# Use actual project patterns
yt issues create WEB-123 "Fix login error on mobile"

# Show real option values
yt issues create API-456 "Add OAuth endpoint" --type Feature --priority High
```

### Helpful Context
```
"""Create a new issue.

Create a new issue in the specified project with the given summary.
Issue types and priorities are project-specific in YouTrack.

Common Examples:
    # Simple bug report
    yt issues create WEB-123 "Fix login error"

    # Feature with assignment
    yt issues create API-456 "Add OAuth" --type Feature --assignee john.doe

Tip: Issue types and priorities are project-specific. Use values that exist in your YouTrack project.
"""
```

## Implementation Notes

### For Contributors
- Always update help text when adding new commands or options
- Test help text with `--help` flag before submitting PRs
- Follow this style guide for consistency
- Ask for help text review for new major features

### For Reviewers
- Verify examples are realistic and testable
- Check consistency with existing command help patterns
- Ensure tips address common user confusion points
- Validate that help text follows the progressive complexity model

## Validation Checklist

When adding or updating help text, verify:

- [ ] Brief description is clear and action-oriented
- [ ] Examples progress from simple to complex
- [ ] All examples are realistic and copy-pasteable
- [ ] Comments explain the "why" not just the "what"
- [ ] Tip section addresses common gotchas
- [ ] Consistent formatting with other commands
- [ ] No information overload
- [ ] Professional tone throughout
