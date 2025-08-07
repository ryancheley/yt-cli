# Deep CLI Documentation Review

## Purpose
This command performs a comprehensive review of the YouTrack CLI to ensure consistency between the implemented CLI commands and the documentation in the `docs/` directory.

## What it does
1. **CLI Command Analysis**: Examines the CLI structure in `youtrack_cli/main.py` and all command modules
2. **Documentation Analysis**: Reviews all documentation files in the `docs/` directory
3. **Consistency Check**: Compares CLI implementation against documentation
4. **Issue Creation**: Creates GitHub issues for any discrepancies found

## Usage
```bash
yt deep-review
```

---

## Results Summary

**Analysis completed successfully!**

### Findings
- **9 total discrepancies** found between CLI implementation and documentation
- **1 high priority issue**: 11 commands missing documentation
- **7 medium priority issues**: Missing subcommand and global options documentation
- **1 low priority issue**: 3 documented global options not in CLI

### GitHub Issues Created
- [Issue #575](https://github.com/ryancheley/yt-cli/issues/575): Add documentation for undocumented CLI commands
- [Issue #576](https://github.com/ryancheley/yt-cli/issues/576): Document missing global CLI options
- [Issue #577](https://github.com/ryancheley/yt-cli/issues/577): Document missing subcommands in issues command
- [Issue #578](https://github.com/ryancheley/yt-cli/issues/578): Document missing subcommands across multiple command groups

### Analysis Details
Full analysis results are available in `scratch/docs-inconsistencies.md` with detailed breakdowns of each discrepancy.

## Implementation

The actual deep review runs a comprehensive analysis script that:

1. **Extracts CLI structure** - Gets all commands, subcommands, and options from CLI help
2. **Analyzes documentation** - Parses all .rst files in docs/commands/
3. **Identifies discrepancies** - Compares CLI vs documentation coverage
4. **Creates GitHub issues** - Automatically files issues for high/medium priority items

The script is available in `scratch/analyze_consistency.py` for future runs.
