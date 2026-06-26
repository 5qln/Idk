#!/usr/bin/env python3
"""
idk_tick.py — /idk Void heartbeat for Hermes cron

Called by cron when /idk is active. Checks:
  1. Void open > max_void_hours? → flag for human surfacing
  2. Agent outputs > max_agent_outputs_in_void? → flag L4
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


def config_path() -> Path:
    env = os.environ.get("IDK_CONFIG")
    if env:
        return Path(env)
    here = Path(__file__).resolve().parent.parent
    return here / "config.yaml"


def load_config() -> dict:
    defaults = {
        "idk": {
            "max_void_hours": 24,
            "max_agent_outputs_in_void": 3,
            "state_dir": "/opt/data/5qln-wiki/plugins/idk/state/",
        }
    }
    cp = config_path()
    if cp.is_file():
        try:
            loaded = _parse_simple_yaml(cp)
            if loaded and "idk" in loaded:
                defaults["idk"].update(loaded["idk"])
        except Exception:
            pass
    return defaults["idk"]


def _parse_simple_yaml(path: Path) -> dict:
    """Parse a simple flat YAML config without PyYAML dependency."""
    result = {}
    current_section = None
    with open(path) as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if not line.startswith(" ") and stripped.endswith(":"):
                current_section = stripped[:-1]
                result[current_section] = {}
            elif current_section and ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip()
                if val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
                elif val.isdigit():
                    val = int(val)
                result[current_section][key] = val
    return result


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
    cfg = load_config()
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
    if outputs > cfg["max_agent_outputs_in_void"]:
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
