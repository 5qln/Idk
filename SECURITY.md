# Security Policy

The /idk system makes cryptographic and privacy guarantees (the sealed Codex and
the three-gate membrane). A break in either is a security issue, not a bug.

## Supported versions

The `main` branch is the only supported version. The Codex seal
(`feaa46b4…c781859b`) identifies the canonical grammar; a surface whose seal does
not verify is out of scope.

## Reporting a vulnerability

Email **security@5qln.com**. Please include:

- the affected repository and commit,
- a description of the issue and its impact,
- reproduction steps or a proof-of-concept,
- whether private phase markers (α, Z, ∇, B″) could leak as a result.

Encrypt sensitive reports with our PGP key: `TODO: publish fingerprint here`.

## What to expect

- Acknowledgement within **3 business days**.
- An initial assessment within **10 business days**.
- Coordinated disclosure: we will agree a date with you before any public note.

Please do not open a public issue for a suspected leak of private content.
