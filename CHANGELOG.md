# Changelog

All notable changes to this repository are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/); this project does
not (yet) use SemVer — the Codex seal is the identity, not a version number.

## [Unreleased]

### Fixed
- Off-by-one in the L4 detector: the cron watchdog now uses `>=`, matching the
  inline check (previously `>`).
- `.gitignore` ignored the local state dir as `~/.5qln/`, which git never
  expands; anchored to `.5qln/`.
- Broken markdown code fence in `SKILL.md` (G-phase gate command).
- Five `SKILL.md` reference links pointed at non-existent files; added scaffolds.
- Obsidian wikilinks in `references/` converted to standard markdown.

### Changed
- Config loading + the simple YAML parser extracted to `scripts/config.py`
  (was duplicated across `idk_state.py` and `idk_tick.py`); parser now handles
  YAML booleans, inline comments, and quoted scalars.
- State writes are now atomic (`tempfile` + `os.replace`).
- `corruption_checks` config key is now live (gates the L4 detector).
- License renamed "Open Source" → "Source-Available" (the invariant clause does
  not meet the OSI definition).
- `ARCHITECTURE.md` aligned to four moods (was "three modes").

### Removed
- Dead code: `import time` (idk_state), `footer_instruction()` (decoding);
  `DECODING_VERSION` is now exported as `__version__`.

### Added
- Test suite (`tests/`), reference link-checker, multi-version CI, SHA-pinned
  GitHub Actions, `SECURITY.md`, `CONTRIBUTING.md`, and standard community files.
