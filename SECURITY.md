# Security policy

## Supported versions

LynxFlow is pre-1.0. Security fixes are applied on a best-effort basis on `main`.

## Reporting a vulnerability

Please **do not** file public GitHub issues for undisclosed security vulnerabilities.

Instead, email the maintainers at: **security@example.com** (replace with a working address before publishing the repository).

Include:

- A description of the issue and its impact
- Steps to reproduce
- Any suggested fix or mitigation (optional)

We will acknowledge receipt as soon as practical.

## Product security notes

LynxFlow is designed to be **local-first**:

- By default, project context should not be sent to third-party cloud services.
- Prompt history is stored locally in SQLite under the configured data directory.
- Users should review redaction warnings before copying or exporting prompts.
