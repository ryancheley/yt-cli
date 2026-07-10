# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities **privately** — do not open a public
GitHub issue for them.

Preferred channel: use GitHub's **Private vulnerability reporting** for this
repository (the **Report a vulnerability** button under the *Security* tab). If
that is unavailable, contact the maintainer directly at **rcheley@gmail.com**.

Please include:

- A description of the vulnerability and its impact.
- Steps to reproduce (or a proof of concept).
- The affected version (`yt --version`) and platform.

## What to expect

- **Acknowledgement:** within 7 days of your report.
- **Assessment & fix:** we aim to have a fix or mitigation plan for confirmed
  issues within 30 days, prioritized by severity.
- **Coordinated disclosure:** we will agree a disclosure timeline with you and
  credit you in the release notes unless you prefer to remain anonymous.

## Supported Versions

Security fixes are applied to the **latest released version**. Please upgrade to
the latest version before reporting, in case the issue is already resolved.

| Version | Supported |
| ------- | --------- |
| Latest release | ✅ |
| Older releases | ❌ (please upgrade) |

## Scope

YouTrack CLI is a single-user, local command-line tool. In-scope concerns
include handling of remote/network-influenced input (e.g. YouTrack API
responses), transport security of credentials, and command execution. Threats
that require another malicious local user on the same machine (e.g. local file
permissions) are outside the tool's threat model.
