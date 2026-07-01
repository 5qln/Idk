# Contributing to /idk

Thank you for reading before opening a PR. This project has a few conventions
that are load-bearing and not obvious.

## The sealed Codex is immutable

`codex.md` contains nine invariant lines whose SHA-256 (`feaa46b4…c781859b`) is
the project's identity. CI (`verify-seal`) rejects any push that changes those
bytes. **Do not edit the sealed block.** Everything else — scripts, references,
docs — is open to extension. See `LICENSE` (Source-Available) for the terms.

## Running the checks locally

```bash
python -m pip install pytest
python -m pytest                 # the test suite
python tests/check_links.py      # no dangling references/ links
python bin/lint.py --seal        # the Codex seal is intact
python -m py_compile scripts/*.py bin/*.py
```

## Dating convention

Dates in comments and version strings (e.g. `2026-06-12.2`) are **ISO-8601 dates
of authorship on the project's working timeline**, not placeholders. When you add
a dated note, use ISO-8601 (`YYYY-MM-DD`) and the date you wrote it.

## The four moods

The single skill holds four moods of one cycle (`S→G→Q→P→V`): **Step-by-step**,
**Flow**, **Decode**, and **Commutation** (the fractal mood). See
`ARCHITECTURE.md §4` and `SKILL.md`. A PR that adds a fifth mode should explain
why the lawful cell cannot already express it.

## Scope

`scripts/` and `bin/` carry the runtime; changes there must keep tests green and
preserve JSON CLI output. SKILL.md is the agent contract — keep it
general-purpose (no single-user personalizations).
