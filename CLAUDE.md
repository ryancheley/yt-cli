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

For every change that is implemented, the README.md file MUST be updated to reflect that change.

## Test

All tests must pass. We use `pytest` for testing, `ruff` for linting, `ty` for type checking, `tox` for running on various versions of Python. We'll utilize `zizmor` for reviewing our GitHub Actions. Pre-commit hooks ensure code quality before commits. All commands should be run with uv.

## Documentation

Documentation is available in the docs/ folder. Any new functionality should have documentation written for it there. The README.md file shoudl not be used for comprehensive documentation.

## Deploy

Deployment will always be done to a feature branch. When a feature is significant enough, we'll bump the version of the tool and tag it with that version. We will have a github action that deploys this to Test PyPI and PyPI using a `release.yml` GitHub Action.

## Current Configuration

- Claude Code permissions are configured in `.claude/settings.local.json`
