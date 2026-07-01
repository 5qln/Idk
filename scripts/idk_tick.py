#!/usr/bin/env python3
"""
idk_tick.py — /idk Void heartbeat for Hermes cron

Called by cron when /idk is active. Checks:
  1. Void open > max_void_hours? → flag for human surfacing
  2. Agent outputs >= max_agent_outputs_in_void? → flag L4
  3. Buffer unchanged for >6 hours? → gentle check-in

Output format:
  If no issues: prints [SILENT] on first line
  If issues: prints JSON with alert details

Usage: python3 idk_tick.py
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

from config import load_idk_config




def state_file(cfg: dict) -> Path:
    d = Path(cfg["state_dir"])
    return d / "idk_state.json"


def load_state(cfg: dict) -> dict:
    sf = state_file(cfg)
    if sf.is_file():
        with open(sf) as fh:
            return json.load(fh)
    return {"active": False}


def main():
    cfg = load_idk_config()
    state = load_state(cfg)
    if not state.get("active"):
        print("[SILENT]")
        return

    alerts = []
    started = state.get("started")
    if started:
        started_dt = datetime.fromisoformat(started)
        hours = (datetime.now(timezone.utc) - started_dt).total_seconds() / 3600
        if hours > cfg["max_void_hours"]:
            alerts.append({
                "type": "void_timeout",
                "hours": round(hours, 1),
                "threshold": cfg["max_void_hours"],
                "message": f"Void open for {round(hours, 1)} hours. Still here. No rush. Is there a seed stirring?"
            })

    outputs = state.get("agent_outputs_in_void", 0)
    if cfg.get("corruption_checks", True) and outputs >= cfg["max_agent_outputs_in_void"]:
        alerts.append({
            "type": "L4_risk",
            "agent_outputs": outputs,
            "threshold": cfg["max_agent_outputs_in_void"],
            "message": "Agent outputs in Void exceeded threshold. Possible L4 — performing depth posture."
        })

    fragments = state.get("fragments", [])
    if fragments:
        last_fragment_time = fragments[-1].get("time")
        if last_fragment_time:
            last_dt = datetime.fromisoformat(last_fragment_time)
            hours_since = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
            if hours_since > 6:
                alerts.append({
                    "type": "void_stale",
                    "hours_since_last_fragment": round(hours_since, 1),
                    "message": "No new fragments in 6+ hours. Is the Void still active, or has the human moved on?"
                })

    if not alerts:
        print("[SILENT]")
    else:
        print(json.dumps({"alerts": alerts}, indent=2, default=str))


if __name__ == "__main__":
    main()
