# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Plan

This is a YouTrack CLI application for interacting with JetBrains YouTrack issue tracking system via command line interface. This cli will offer an ergonomic, best practice cli and will leverage

- rich
- textual
- pydantic

We use `uv` for managing dependencies.

## Create

Each new feature must have a corresponding github issue. When working on a new issue a new feature branch must be created with the name of the branch matching the name of the issue with the issue number in it.

For every change that is implemented, the corresponding documentation in the docs/ flder MUST be updated to reflect that change. Updates to README.md should be made to include a very short summary but not comprehensive details.

## Test

All tests must pass. We use `pytest` for testing, `ruff` for linting, `ty` for type checking, `tox` for running on various versions of Python. We'll utilize `zizmor` for reviewing our GitHub Actions. Pre-commit hooks ensure code quality before commits. All commands should be run with uv.

## Documentation

Documentation is available in the docs/ folder. Any new functionality should have documentation written for it there. The README.md file shoudl not be used for comprehensive documentation. Documentation for the YouTrack API can be found [here](https://www.jetbrains.com/help/youtrack/devportal/youtrack-rest-api.html) and should be referenced when needed.

## Deploy

Deployment will always be done to a feature branch. When a feature is significant enough, we'll bump the version of the tool and tag it with that version. We will have a github action that deploys this to Test PyPI and PyPI using a `release.yml` GitHub Action.

## GitHub Issue resolution steps

1. Make sure a new branch has been created
2. Think through the change that needs to be implemented
3. Write the plan to scratch/issue-id.md where id is the issue number from GitHub. For example issue 42 would be written to scratch/issue-42.md
4. Implement the changes from the plan written in scratch/issue-id.md
5. Create a PR. never bypass the pre-commit checks
6. Once the PR has been squashed and merged, switch back to main. You'll need to check the PR status every 60 seconds
7. Pull the changes from main to local development

## Current Configuration

- Claude Code permissions are configured in `.claude/settings.local.json`
