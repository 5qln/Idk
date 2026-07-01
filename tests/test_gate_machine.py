"""xyzab gate machine — phase ordering (S->G->Q->P->V == gates x->y->z->a->b).

Drives the real CLI in an isolated XYZAB_STATE_DIR so nothing touches ~/.5qln.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
XYZAB = REPO / "scripts" / "xyzab_state.py"


def run(args, state_dir):
    env = {"XYZAB_STATE_DIR": str(state_dir), "PATH": "/usr/bin:/bin"}
    import os
    e = os.environ.copy()
    e.update(env)
    return subprocess.run([sys.executable, str(XYZAB), *args],
                          capture_output=True, text=True, env=e)


def test_reset_then_status_is_clean(tmp_path):
    run(["reset", "--no-archive"], tmp_path)
    r = run(["status"], tmp_path)
    assert r.returncode == 0
    # status renders a human-readable gate board; just confirm it ran and shows the cycle
    assert "cycle" in (r.stdout + r.stderr).lower()


def test_out_of_order_gate_is_rejected(tmp_path):
    run(["reset", "--no-archive"], tmp_path)
    # gate 'a' (P) cannot open before x/y/z — expect a non-success signal
    r = run(["open", "a", "-c", "premature"], tmp_path)
    combined = (r.stdout + r.stderr).lower()
    assert r.returncode != 0 or "order" in combined or "false" in combined or "reject" in combined
