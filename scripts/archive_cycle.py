#!/usr/bin/env python3
"""
archive_cycle.py — Append a completed cycle's trail to cycles.jsonl before reset.

Usage:
  python3 archive_cycle.py [--session SESSION_ID] [--dry-run]
  
What it does:
  1. Read the current gate state via xyzab_state.py trail.
  2. If all gates are open → cycle is complete → archive it.
  3. Append one JSON line to ~/.5qln/cycles.jsonl.
  4. Optionally reset (archive preserves the trail; reset clears it).

The archive contains:
  - cycle: cycle number
  - gates: full gate content (X, α, Z, ∇, B'', ∞0')
  - archived_at: ISO timestamp
  - session: optional session identifier for cross-session matching

Stdlib only. Python 3.8+.
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

CYCLES_DIR = Path(os.environ.get("XYZAB_STATE_DIR", Path.home() / ".5qln"))
CYCLES_LOG = CYCLES_DIR / "cycles.jsonl"

GATES = ["x", "y", "z", "a", "b"]
GATE_NAMES = {
    "x": "X (Validated Spark)",
    "y": "Y (Validated Pattern — α + {α'})",
    "z": "Z (Resonant Key — φ ⋂ Ω)",
    "a": "A (Flow Direction — ∇)",
    "b": "B (Artifact + Return Question — B'' + ∞0')",
}
GATE_PHASE = {"x": "S", "y": "G", "z": "Q", "a": "P", "b": "V"}


def get_trail() -> Dict[str, Any]:
    """Run xyzab_state.py trail and parse the JSON output."""
    script = Path(__file__).resolve().parent / "xyzab_state.py"
    result = subprocess.run(
        [sys.executable, str(script), "trail"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: trail failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def all_gates_open(state: Dict[str, Any]) -> bool:
    """Check if every gate is open."""
    return all(state["gates"][g]["open"] for g in GATES)


def extract_cycle_data(state: Dict[str, Any], session: Optional[str] = None) -> Dict[str, Any]:
    """Extract the essential cycle data from gate state."""
    gates = {}
    for g in GATES:
        gs = state["gates"][g]
        gates[g] = {
            "phase": GATE_PHASE[g],
            "name": GATE_NAMES[g],
            "content": gs.get("content"),
            "opened_at": gs.get("opened_at"),
        }
    
    return {
        "cycle": state.get("cycle", state.get("cycle_count", 0)),
        "gates": gates,
        "archived_at": datetime.now(timezone.utc).isoformat(),
        "session": session,
    }


def load_cycles(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Load all archived cycles from the JSONL log."""
    if not CYCLES_LOG.exists():
        return []
    cycles = []
    with open(CYCLES_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                cycles.append(json.loads(line))
    if limit and limit > 0:
        cycles = cycles[-limit:]
    return cycles


def append_cycle(entry: Dict[str, Any]) -> Path:
    """Append a cycle entry to the JSONL log."""
    CYCLES_DIR.mkdir(parents=True, exist_ok=True)
    with open(CYCLES_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return CYCLES_LOG


def archive(session: Optional[str] = None, dry_run: bool = False) -> Optional[Dict[str, Any]]:
    """
    Archive the current completed cycle.
    Returns the archived entry, or None if not complete.
    """
    state = get_trail()
    
    if not all_gates_open(state):
        print("Cycle is not complete — not all gates are open. Nothing to archive.")
        print(f"Gates: { {g: state['gates'][g]['open'] for g in GATES} }")
        return None
    
    entry = extract_cycle_data(state, session)
    
    if dry_run:
        print(json.dumps(entry, indent=2, ensure_ascii=False))
        print(f"\nDry run — would append to {CYCLES_LOG}")
        return entry
    
    path = append_cycle(entry)
    return entry


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Archive a completed /idk cycle before reset."
    )
    parser.add_argument("--session", default=None, help="Session identifier")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be archived")
    args = parser.parse_args()
    
    result = archive(
        session=args.session,
        dry_run=args.dry_run,
    )
    
    if result:
        cycle_num = result["cycle"]
        path = CYCLES_LOG
        if not args.dry_run:
            print(f"Cycle {cycle_num} archived → {path}")
            loaded = load_cycles()
            print(f"Total cycles in archive: {len(loaded)}")
    elif result is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
