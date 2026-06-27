#!/usr/bin/env python3
"""
view_patterns.py — Read /idk cycle archives and surface what's actually there.

Usage:
  python3 view_patterns.py                    Show overview: cycle count, timeline
  python3 view_patterns.py --seeds            Show recurring seeds (α) across cycles
  python3 view_patterns.py --questions        Show question trajectory (X → ∞0')
  python3 view_patterns.py --cycle N          Show full details for cycle N
  python3 view_patterns.py --raw              Dump all cycles as JSON

Never fabricates. Never generates connections the human didn't make.
Form only — whether the gaps were genuine is the human's to attest.

Stdlib only. Python 3.8+.
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

CYCLES_DIR = Path(os.environ.get("XYZAB_STATE_DIR", Path.home() / ".5qln"))
CYCLES_LOG = CYCLES_DIR / "cycles.jsonl"


def load_cycles() -> List[Dict[str, Any]]:
    """Load all archived cycles."""
    if not CYCLES_LOG.exists():
        return []
    cycles = []
    with open(CYCLES_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                cycles.append(json.loads(line))
    return cycles


def overview(cycles: List[Dict[str, Any]]) -> str:
    """Surface what's actually there: count, timeline, phase completion."""
    if not cycles:
        return "No cycles archived yet."

    lines = [
        f"{'─' * 58}",
        f"  /idk — Cycle Archive Overview",
        f"  Total cycles: {len(cycles)}",
    ]

    # Timeline
    first = cycles[0].get("archived_at", "?")
    last = cycles[-1].get("archived_at", "?")
    if first != "?" and last != "?":
        lines.append(f"  Span: {first[:10]} → {last[:10]}")

    # Gate completion stats
    gate_count = Counter()
    for c in cycles:
        for g in ["x", "y", "z", "a", "b"]:
            content = c.get("gates", {}).get(g, {}).get("content")
            if content:
                gate_count[g] += 1

    lines.append("")
    lines.append("  Gate completion (across all cycles):")
    for g in ["x", "y", "z", "a", "b"]:
        phase = {"x": "S→G", "y": "G→Q", "z": "Q→P", "a": "P→V", "b": "V→∞"}
        bar = "█" * gate_count[g]
        lines.append(f"    {g} ({phase[g]}): {gate_count[g]}/{len(cycles)}  {bar}")

    lines.append(f"{'─' * 58}")

    return "\n".join(lines)


def seeds(cycles: List[Dict[str, Any]]) -> str:
    """Surface recurring α values across cycles."""
    if not cycles:
        return "No cycles archived yet."

    all_seeds = []
    for c in cycles:
        y_content = c.get("gates", {}).get("y", {}).get("content")
        if y_content:
            all_seeds.append((c["cycle"], y_content))

    if not all_seeds:
        return "No seeds (α) found in archive."

    lines = [f"{'─' * 58}", "  Recurring seeds (α) across cycles:", ""]
    for cycle_num, seed in all_seeds:
        # Truncate for display
        display = seed if len(seed) <= 80 else seed[:77] + "..."
        lines.append(f"  Cycle {cycle_num}: {display}")

    lines.append("")
    lines.append(f"{'─' * 58}")
    return "\n".join(lines)


def questions(cycles: List[Dict[str, Any]]) -> str:
    """Surface question trajectory: X → ∞0' across cycles."""
    if not cycles:
        return "No cycles archived yet."

    lines = [f"{'─' * 58}", "  Question trajectory (X → ∞0') across cycles:", ""]

    for c in cycles:
        cycle_num = c["cycle"]
        x_content = c.get("gates", {}).get("x", {}).get("content")
        b_content = c.get("gates", {}).get("b", {}).get("content")

        # Extract X from gate x content
        x_display = "—"
        if x_content:
            # Extract the X value from "X: ..." format
            for line_text in x_content.split("\n"):
                if line_text.startswith("X:"):
                    x_display = line_text[2:].strip()
                    if len(x_display) > 90:
                        x_display = x_display[:87] + "..."
                    break

        # Extract ∞0' from gate b content
        infty_display = "—"
        if b_content:
            for line_text in b_content.split("\n"):
                if "∞0':" in line_text:
                    idx = line_text.index("∞0':")
                    infty_display = line_text[idx + 5:].strip()
                    if len(infty_display) > 90:
                        infty_display = infty_display[:87] + "..."
                    break
                if "∞0'" in line_text:
                    idx = line_text.index("∞0'")
                    after = line_text[idx + 4:].strip()
                    if after.startswith(":"):
                        after = after[1:].strip()
                    infty_display = after
                    if len(infty_display) > 90:
                        infty_display = infty_display[:87] + "..."
                    break

        lines.append(f"  Cycle {cycle_num}:")
        lines.append(f"    X:    {x_display}")
        lines.append(f"    ∞0':  {infty_display}")
        lines.append("")

    lines.append(f"{'─' * 58}")
    return "\n".join(lines)


def cycle_detail(cycles: List[Dict[str, Any]], cycle_num: int) -> str:
    """Show full details for a specific cycle."""
    match = None
    for c in cycles:
        if c["cycle"] == cycle_num:
            match = c
            break

    if not match:
        return f"No cycle {cycle_num} found in archive."

    phase_labels = {
        "x": "S → G", "y": "G → Q", "z": "Q → P",
        "a": "P → V", "b": "V → next S"
    }

    lines = [
        f"{'─' * 58}",
        f"  Cycle {cycle_num}",
    ]
    if match.get("session"):
        lines.append(f"  Session: {match['session']}")
    lines.append(f"  Archived: {match.get('archived_at', '?')}")
    lines.append("")

    for g in ["x", "y", "z", "a", "b"]:
        gate = match["gates"].get(g, {})
        content = gate.get("content")
        opened = gate.get("opened_at", "?")
        label = phase_labels[g]

        lines.append(f"  [{g}] {label}")
        lines.append(f"      Opened: {opened}")
        if content:
            lines.append(f"      Content: {content[:200]}")
        lines.append("")

    lines.append(f"{'─' * 58}")
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="View /idk cycle archive patterns — surfaces what's actually there."
    )
    parser.add_argument("--seeds", action="store_true", help="Show recurring seeds (α)")
    parser.add_argument("--questions", action="store_true", help="Show question trajectory")
    parser.add_argument("--cycle", type=int, help="Show full details for a specific cycle")
    parser.add_argument("--raw", action="store_true", help="Dump all cycles as JSON")
    args = parser.parse_args()

    cycles = load_cycles()

    if args.raw:
        print(json.dumps(cycles, indent=2, ensure_ascii=False))
    elif args.seeds:
        print(seeds(cycles))
    elif args.questions:
        print(questions(cycles))
    elif args.cycle:
        print(cycle_detail(cycles, args.cycle))
    else:
        print(overview(cycles))


if __name__ == "__main__":
    main()
