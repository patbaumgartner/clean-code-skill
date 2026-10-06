# Security Policy

## Scope

This repository contains Markdown instructions that AI agents read, a plugin manifest, and two
small scripts (`scripts/install.sh`, `scripts/validate.py`). Relevant security issues include:

- Instructions that could cause an agent to run unsafe commands, exfiltrate data, or ignore a
  user's safety settings (prompt-injection style content).
- Installer behavior that deletes or overwrites files it should not, follows unsafe paths, or
  executes untrusted input.
- Supply-chain problems in CI, release, or dependency pinning.

The skill does not execute code on its own, ask for credentials, or make network requests.

## Supported versions

Only the latest released version receives fixes.

## Reporting a vulnerability

Please do **not** open a public issue for a suspected vulnerability.

Use GitHub's private vulnerability reporting: open the repository's **Security** tab and choose
**Report a vulnerability**. If that option is unavailable, contact the maintainer through the
details on their [GitHub profile](https://github.com/patbaumgartner) and ask for a private
channel before sharing details.

Include what you found, how to reproduce it, the affected version or commit, and the impact you
see. You can expect an acknowledgment within a few days and a fix or mitigation plan once the
issue is confirmed. Coordinated disclosure is appreciated; reporters are credited in the release
notes unless they prefer otherwise.

## Using skills safely

Skills are instructions that an agent follows with your permissions. Review any skill before
installing it, including this one, and pin to a release tag or commit when installing from a
repository. Avoid piping scripts from the network into a shell; clone, read, then run.
