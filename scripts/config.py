#!/usr/bin/env python3
"""
config.py — shared config loading + atomic state writes for the /idk scripts.

Single source of truth for config_path(), the (deliberately small) YAML
reader, the merged default config, and atomic_write_json(). idk_state.py and
idk_tick.py both import from here so a fix to the parser propagates to both
(previously the three functions were duplicated verbatim across the two files).

stdlib-only, Python 3.8+.
"""

import json
import os
import tempfile
from pathlib import Path

# Superset of every key either script reads. idk_tick ignores the extras.
DEFAULT_IDK_CONFIG = {
    "max_void_hours": 24,
    "max_agent_outputs_in_void": 3,
    "auto_log_fragments": True,
    "xyzab_integration": True,
    "corruption_checks": True,
    "inquiry_field_path": str(Path.home() / ".5qln" / "inquiry-field"),
    "state_dir": str(Path.home() / ".5qln"),
}

_TRUE = {"true", "yes", "on"}
_FALSE = {"false", "no", "off"}


def config_path() -> Path:
    """Locate config.yaml via $IDK_CONFIG or relative to this script."""
    env = os.environ.get("IDK_CONFIG")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "config.yaml"


def _coerce(val: str):
    """Coerce a scalar string to bool/int/float, honouring YAML-ish booleans."""
    low = val.lower()
    if low in _TRUE:
        return True
    if low in _FALSE:
        return False
    if val.lstrip("-").isdigit():
        return int(val)
    try:
        return float(val)
    except ValueError:
        return val


def _strip_inline_comment(val: str) -> str:
    """Drop a trailing ' # comment' but keep '#' inside quotes."""
    if val[:1] in ("'", '"'):
        return val  # quoted scalar: leave intact, dequoted below
    cut = val.find(" #")
    return val[:cut].rstrip() if cut != -1 else val


def parse_simple_yaml(path: Path) -> dict:
    """Parse a small flat config: one level of `section:` then `key: value`.

    Supported: scalars (bool/int/float/str), inline comments after a space,
    single- or double-quoted strings. NOT supported: nested maps beyond one
    level, flow lists, multi-line values. Anything unsupported is ignored
    rather than mis-parsed.
    """
    result: dict = {}
    section = None
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if not line[:1].isspace() and stripped.endswith(":"):
                section = stripped[:-1].strip()
                result[section] = {}
            elif section is not None and ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = _strip_inline_comment(val.strip())
                if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
                    result[section][key] = val[1:-1]
                elif val == "":
                    result[section][key] = ""
                else:
                    result[section][key] = _coerce(val)
    return result


def load_idk_config() -> dict:
    """Return the merged `idk` config (defaults overlaid with config.yaml)."""
    cfg = dict(DEFAULT_IDK_CONFIG)
    cp = config_path()
    if cp.is_file():
        try:
            loaded = parse_simple_yaml(cp)
            if loaded.get("idk"):
                cfg.update(loaded["idk"])
        except Exception:
            pass  # a broken config must not strand the agent; use defaults
    return cfg


def atomic_write_json(path: Path, obj, **dump_kwargs) -> None:
    """Write JSON via a temp file + os.replace so a concurrent/crashed write
    can never leave a torn or empty state file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, **dump_kwargs)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        finally:
            raise
