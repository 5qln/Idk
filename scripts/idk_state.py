#!/usr/bin/env python3
"""
idk_state.py — /idk Void Buffer state engine

Manages:
  - Is /idk active?
  - Fragments accumulated in the Void Buffer
  - Crystallization validation
  - Inquiry-field logging

State file: config.idk.state_dir + idk_state.json
stdlib-only, Python 3.8+.

Commands:
  open              Enter Void mode
  fragment <text>   Add a fragment to the buffer
  reflect           Return buffer contents for agent to mirror
  deepen            Return buffer + deepening prompt context
  crystallize <X>   Open xyzab gate x; on success close Void and log to IF-DB
  release           Close Void without crystallization (legitimate abort)
  status            Show buffer size, time in Void, corruption flags
  close             Force-close (admin)
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


def config_path() -> Path:
    """Locate config.yaml relative to this script or via env."""
    env = os.environ.get("IDK_CONFIG")
    if env:
        return Path(env)
    here = Path(__file__).resolve().parent.parent
    return here / "config.yaml"


def load_config() -> dict:
    """Load config, with defaults for anything missing."""
    defaults = {
        "idk": {
            "max_void_hours": 24,
            "max_agent_outputs_in_void": 3,
            "auto_log_fragments": True,
            "xyzab_integration": True,
            "corruption_checks": True,
            "inquiry_field_path": str(Path.home() / ".5qln" / "inquiry-field"),
            "state_dir": str(Path.home() / ".5qln"),
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
    d.mkdir(parents=True, exist_ok=True)
    return d / "idk_state.json"


def load_state(cfg: dict) -> dict:
    sf = state_file(cfg)
    if sf.is_file():
        with open(sf) as fh:
            return json.load(fh)
    return {
        "active": False,
        "started": None,
        "fragments": [],
        "agent_outputs_in_void": 0,
        "corruption_flags": [],
        "crystallized_x": None,
        "mode": None,
    }


def save_state(cfg: dict, state: dict):
    with open(state_file(cfg), "w") as fh:
        json.dump(state, fh, indent=2, default=str)


def cmd_open(cfg: dict):
    state = load_state(cfg)
    state["active"] = True
    state["started"] = datetime.now(timezone.utc).isoformat()
    state["fragments"] = []
    state["agent_outputs_in_void"] = 0
    state["corruption_flags"] = []
    state["crystallized_x"] = None
    state["mode"] = None
    save_state(cfg, state)
    print(json.dumps({"ok": True, "action": "void_opened", "started": state["started"]}))


def cmd_fragment(cfg: dict, text: str):
    state = load_state(cfg)
    if not state["active"]:
        print(json.dumps({"ok": False, "error": "void_not_active"}))
        return
    state["fragments"].append({
        "time": datetime.now(timezone.utc).isoformat(),
        "text": text,
    })
    save_state(cfg, state)
    print(json.dumps({"ok": True, "action": "fragment_added", "count": len(state["fragments"])}))


def cmd_reflect(cfg: dict):
    state = load_state(cfg)
    if not state["active"]:
        print(json.dumps({"ok": False, "error": "void_not_active"}))
        return
    output = {
        "ok": True,
        "action": "reflect",
        "fragment_count": len(state["fragments"]),
        "fragments": state["fragments"],
        "time_in_void_minutes": _minutes_in_void(state),
        "agent_outputs": state["agent_outputs_in_void"],
        "corruption_flags": state["corruption_flags"],
    }
    print(json.dumps(output, indent=2, default=str))


def cmd_deepen(cfg: dict):
    state = load_state(cfg)
    if not state["active"]:
        print(json.dumps({"ok": False, "error": "void_not_active"}))
        return
    output = {
        "ok": True,
        "action": "deepen",
        "fragments": state["fragments"],
        "prompt": (
            "The fragments above are raw expression from the Void. Do not name the seed. "
            "Ask ONE question that goes deeper into what's behind these fragments. "
            "Follow, don't lead."
        ),
    }
    print(json.dumps(output, indent=2, default=str))


def cmd_crystallize(cfg: dict, x: str):
    state = load_state(cfg)
    if not state["active"]:
        print(json.dumps({"ok": False, "error": "void_not_active"}))
        return

    # Hand off to the gate machine FIRST. The gate machine is the sole phase
    # authority — if it will not open gate x, the spark has not crystallized,
    # so the Void stays open and nothing is lost. We never report success on a
    # shut gate, and we never close Void out from under a rejected spark.
    xyzab_result = None
    if cfg.get("xyzab_integration"):
        xyzab_result = _open_xyzab_gate_x(x)
        if not xyzab_result.get("opened"):
            print(json.dumps({
                "ok": False,
                "action": "crystallize_rejected",
                "X": x,
                "reason": xyzab_result.get("reason"),
                "gate_violations": xyzab_result.get("violations"),
                "hint": xyzab_result.get("hint") or (
                    "The gate did not open. Restate X as a question — it may "
                    "open with what/where/why/how/whether… or end in ? — then "
                    "crystallize again. (Or open gate x with --override to "
                    "record a human decision.)"),
                "void": "still open — nothing lost",
                "xyzab_gate_x": xyzab_result,
            }, indent=2, default=str))
            return

    # Gate opened (or integration disabled): the crossing is real. Close Void.
    state["crystallized_x"] = x
    state["active"] = False
    if cfg.get("auto_log_fragments"):
        _log_to_if_db(cfg, state)
    save_state(cfg, state)
    print(json.dumps({
        "ok": True,
        "action": "crystallized",
        "X": x,
        "fragment_count": len(state["fragments"]),
        "time_in_void_minutes": _minutes_in_void(state),
        "xyzab_gate_x": xyzab_result,
    }, indent=2, default=str))


def cmd_release(cfg: dict):
    state = load_state(cfg)
    state["active"] = False
    save_state(cfg, state)
    print(json.dumps({
        "ok": True,
        "action": "released",
        "fragment_count": len(state["fragments"]),
        "time_in_void_minutes": _minutes_in_void(state),
        "note": "Legitimate abort. Void closed without crystallization. Nothing lost.",
    }))


def cmd_status(cfg: dict):
    state = load_state(cfg)
    output = {
        "active": state["active"],
        "started": state["started"],
        "fragment_count": len(state["fragments"]),
        "time_in_void_minutes": _minutes_in_void(state) if state["active"] else 0,
        "agent_outputs_in_void": state["agent_outputs_in_void"],
        "corruption_flags": state["corruption_flags"],
        "crystallized_x": state["crystallized_x"],
    }
    print(json.dumps(output, indent=2, default=str))


def _minutes_in_void(state: dict) -> float:
    if not state.get("started"):
        return 0
    started = datetime.fromisoformat(state["started"])
    now = datetime.now(timezone.utc)
    return round((now - started).total_seconds() / 60, 1)


def _log_to_if_db(cfg: dict, state: dict):
    if_path = Path(cfg.get("inquiry_field_path", str(Path.home() / ".5qln" / "inquiry-field")))
    if_path.mkdir(parents=True, exist_ok=True)
    entry = {
        "session_type": "idk_void",
        "started": state["started"],
        "fragment_count": len(state["fragments"]),
        "fragments": state["fragments"],
        "crystallized_x": state["crystallized_x"],
        "time_in_void_minutes": _minutes_in_void(state),
        "mode": state.get("mode", "true_s"),
    }
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    log_file = if_path / f"idk-{ts}.json"
    with open(log_file, "w") as fh:
        json.dump(entry, fh, indent=2, default=str)


def _find_xyzab() -> Optional[str]:
    """Locate xyzab_state.py: env override, then sibling (the normal install —
    setup.sh puts both in the same scripts/ dir), then the canonical path.
    Resolving relative to this file means the bridge also works from the repo,
    not only from ~/.hermes."""
    env = os.environ.get("QLN_XYZAB")
    here = Path(__file__).resolve().parent
    for c in (
        Path(env) if env else None,
        here / "xyzab_state.py",
        Path(os.path.expanduser("~/.hermes/skills/idk/scripts/xyzab_state.py")),
    ):
        if c and c.is_file():
            return str(c)
    return None


def _open_xyzab_gate_x(x: str) -> dict:
    """Hand the validated X to the gate machine and open gate x. Always returns
    an explicit 'opened' flag; on rejection it surfaces the gate's own
    violations and hint — so the caller can never mistake a shut gate for a
    crossing."""
    import subprocess
    script = _find_xyzab()
    if script is None:
        return {"opened": False, "reason": "not_found",
                "detail": "xyzab_state.py not found — set QLN_XYZAB, or install "
                          "the idk skill so it sits beside idk_state.py."}
    try:
        result = subprocess.run(
            [sys.executable, script, "open", "x", "-c", x],
            capture_output=True, text=True, timeout=10,
        )
    except Exception as e:
        return {"opened": False, "reason": "error", "detail": str(e)}

    out = {"opened": result.returncode == 0,
           "exit_code": result.returncode,
           "stdout": result.stdout.strip(),
           "stderr": result.stderr.strip()}
    if result.returncode != 0:
        out["reason"] = "rejected"
        try:
            parsed = json.loads(result.stdout)
            out["violations"] = parsed.get("violations", [])
            out["hint"] = parsed.get("hint")
        except (ValueError, TypeError):
            pass
    return out


if __name__ == "__main__":
    cfg = load_config()
    args = sys.argv[1:]
    if not args:
        print("Usage: idk_state.py <open|fragment|reflect|deepen|crystallize|release|status|close> [args]")
        sys.exit(1)

    cmd = args[0]
    if cmd == "open":
        cmd_open(cfg)
    elif cmd == "fragment" and len(args) > 1:
        cmd_fragment(cfg, " ".join(args[1:]))
    elif cmd == "reflect":
        cmd_reflect(cfg)
    elif cmd == "deepen":
        cmd_deepen(cfg)
    elif cmd == "crystallize" and len(args) > 1:
        cmd_crystallize(cfg, " ".join(args[1:]))
    elif cmd == "release":
        cmd_release(cfg)
    elif cmd == "status":
        cmd_status(cfg)
    elif cmd == "close":
        state = load_state(cfg)
        state["active"] = False
        save_state(cfg, state)
        print(json.dumps({"ok": True, "action": "force_closed"}))
    else:
        print(json.dumps({"ok": False, "error": f"unknown command: {cmd}"}))
        sys.exit(1)
