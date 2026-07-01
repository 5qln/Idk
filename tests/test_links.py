import subprocess, sys
from pathlib import Path
def test_skill_references_all_resolve():
    r = subprocess.run([sys.executable, str(Path(__file__).parent / "check_links.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
