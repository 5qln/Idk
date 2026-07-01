"""L4 threshold must be IDENTICAL in the inline check and the cron watchdog.

Guards C3: idk_state.py used >= while idk_tick.py used > (off-by-one). This is a
source-level invariant test — the two comparisons must agree forever.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE = (REPO / "scripts" / "idk_state.py").read_text()
TICK = (REPO / "scripts" / "idk_tick.py").read_text()


def test_inline_check_uses_ge():
    assert 'state["agent_outputs_in_void"] >= threshold' in STATE


def test_cron_watchdog_uses_ge_not_gt():
    assert 'outputs >= cfg["max_agent_outputs_in_void"]' in TICK
    assert 'outputs > cfg["max_agent_outputs_in_void"]' not in TICK


def test_corruption_checks_gates_l4():
    # M1: the previously-inert corruption_checks key now gates the detector
    assert 'cfg.get("corruption_checks", True)' in TICK
