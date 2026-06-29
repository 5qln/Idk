# Idk vs Idk2 — Repo Topology

There are two repos. They share the same sealed Codex. The delta is in the operating layer.

## Idk (original)

- **Repo:** `5qln/Idk`
- **Commits:** 13
- **Tagline:** "A full installer of /idk for ai agents"
- **Local:** `/opt/data/5qln-idk`
- **Character:** The reference implementation. Three layers: L1 (Codex), D1 (Decoder/SKILL.md), C1 (Compiler/lint.py). No persistence.

## Idk2 (operating)

- **Repo:** `5qln/Idk2`
- **Commits:** 3
- **Tagline:** "Main operating"
- **Local:** `/opt/data/Idk2`
- **Character:** Idk plus a memory layer that doesn't cross the Membrane. Same sealed Codex. Adds session-chain storage.

## What's byte-identical

| File | Both repos |
|---|---|
| `codex.md` | sha256: `fb29fb4eeafdb9f1b05810842d7dd675127f1b4089e314543228a6aecfd8b310` (2003 bytes) |
| `skills/idk/SKILL.md` | 202 lines, all 5 phases, corruption codes, "Two Moods, One Cycle" |
| `skills/idk/references/decoding.md` | Identical |
| `bin/lint.py` | Identical |
| `config.yaml` | Identical |
| `scripts/idk_state.py` | Identical |
| `scripts/idk_tick.py` | Identical |

## What Idk2 adds

1. **`scripts/archive_cycle.py`** (155 lines) — Captures the completed trail before reset. Appends one JSON line per cycle to `~/.5qln/cycles.jsonl`. Stdlib-only. Called inline by `xyzab_state.py cmd_reset`.

2. **`scripts/view_patterns.py`** (224 lines) — Reads the cycle log. Surfaces seeds, questions, and cycle detail that are actually there. The critical clause: *"never fabricates connections between sessions — if two seeds share a shape, it notes the surface similarity; it does not claim resonance or infer meaning."*

3. **`void-posture.md`** — Void posture specification with `/idk` sub-commands (`fragment`, `reflect`, `deepen`, `crystallize`, `release`, `status`), posture shift table, corruption chain mapped per-phase.

## What changed (shared files modified)

- **`scripts/xyzab_state.py`** — Engine gains `_auto_archive()` hook. On `cmd_reset`, if all gates are open, it imports and runs `archive_cycle.py` before clearing state. Adds `--no-archive` flag.

- **`README.md`** — "What's here" table gains two entries (archive_cycle.py, view_patterns.py). No other text changed.

- **`ARCHITECTURE.md`** — New §9 "Session-chain storage" (36 lines). Old §9 shifts to §10.

- **`install.sh`** — Different posture. Old: "Plugin Installer" that patches an existing skill. New: "Void Posture Engine Installer" that runs from repo root.

## Current state (2026-06-27)

Idk2's features have been ported INTO Idk (`5qln/Idk`, branch `feat/session-chain-storage`).
Idk is now the single source of truth. The port added:

1. **`scripts/archive_cycle.py`** — Captures the completed trail before reset.
   Appends one JSON line per cycle to `~/.5qln/cycles.jsonl`. Called inline by
   `xyzab_state.py cmd_reset` via `_auto_archive()`.

2. **`scripts/view_patterns.py`** — Reads the cycle log. Four views: default
   (overview), `--seeds`, `--questions`, `--cycle N`. Never fabricates connections.

3. **`void-posture.md`** — Void posture specification with `/idk` sub-commands.

4. **`scripts/xyzab_state.py`** — `_auto_archive()` hook, `--no-archive` flag.

Post-port audit also fixed: stale xyzab paths in void-posture.md + idk_state.py,
hardcoded machine paths (`/opt/data/5qln-wiki/`) → `~/.5qln/`, broken seal
verification command in codex.md (`verify_decoding.py` → `bin/lint.py --seal`),
`--detail` → `--cycle` flag in SKILL.md, missing entries in README "What's here"
table, and ARCHITECTURE.md §4 updated from "both modes" to "all three modes."

Idk2 is superseded. Keep the local clone for reference; all new work goes to Idk.
The installed skill at `/opt/data/skills/idk/` is the operating version — it already includes session-chain storage, three moods (Step by step / Flow / Decode), and all pitfalls beyond what either upstream SKILL.md contains.

## Void posture folded in (2026-06-27)

The architectural decision: Void posture is no longer optional. It IS the entrance.

**Before:** Two startup procedures existed with no connection between them.
- SKILL.md's startup: `[S-PHASE] Ready. What's at the edge of what you know?`
- void-posture.md's startup: `[S-PHASE · VOID] I'm here. Take your time.`
- install.sh installed the Void subsystem separately; the README's happy path never reached it.

**After:** Void posture is the real front door.
- SKILL.md startup replaced with full Void entrance (commands, posture shift, self-check, exit conditions, watchdog)
- install.sh deleted — everything lands with setup.sh
- Void-specific prohibitions added to "What You Will Not Do"
- Per-phase corruption chain added to Corruption Codes
- `idk_state.py`, `idk_tick.py`, `config.yaml` installed by setup.sh alongside the engine
- "optional" language removed from README, ARCHITECTURE, TROUBLESHOOTING

**The reason:** `/idk`'s first claim is "start from not knowing." The Void posture IS that — it declares presence and waits. The old startup ("What's at the edge of what you know?") was already asking for content. The two-startup split was development sequencing, not architecture.
