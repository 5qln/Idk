# Installing the canonical /idk on this host

Source: `https://github.com/5qln/Idk`

## Quick install

```bash
git clone https://github.com/5qln/Idk.git ~/idk
cd ~/idk && bash setup.sh
```

setup.sh does four things:
1. Verifies the Codex seal (217-byte hash must match)
2. Installs `skills/idk/` + `codex.md` into `$HERMES_SKILLS`
3. Installs `scripts/xyzab_state.py` (the gate machine)
4. Installs `scripts/archive_cycle.py` and `scripts/view_patterns.py` (session-chain storage)

## Custom HERMES_HOME

`setup.sh` defaults to `~/.hermes/skills/` unless `HERMES_SKILLS` is set. If your
`HERMES_HOME` is elsewhere, copy the skill after install:

```bash
cp -r ~/.hermes/skills/idk "$HERMES_HOME/skills/idk"
```

Or set the env var before setup:

```bash
HERMES_SKILLS="$HERMES_HOME/skills" bash setup.sh
```

## Gate machine state

The gate machine persists state at `~/.5qln/xyzab_state.json`.
Override with `$XYZAB_STATE_DIR`.

## Verifying the seal independently

```bash
python3 ~/idk/bin/lint.py --seal
```

Expected output: `seal: OK  (217 bytes, feaa46b4147d4e02…)`

## Session-chain storage

Every `reset` auto-archives the completed cycle trail to `~/.5qln/cycles.jsonl`
(one JSON line per cycle). View patterns:

```bash
python3 scripts/view_patterns.py             # overview (cycle count, timeline, gate stats)
python3 scripts/view_patterns.py --seeds     # recurring α across cycles
python3 scripts/view_patterns.py --questions # X → ∞0' trajectory
python3 scripts/view_patterns.py --cycle N   # full detail for a specific cycle
python3 scripts/view_patterns.py --raw       # dump all cycles as JSON
```

Manual archive (e.g., for tagging sessions):

```bash
python3 scripts/archive_cycle.py --session "project-name"
```

Run `reset --no-archive` to skip auto-archive for a given cycle.
