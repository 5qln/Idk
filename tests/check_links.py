#!/usr/bin/env python3
"""Fail if SKILL.md cites a references/ file that does not exist (guards C2)."""
import re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
skill = (REPO / "skills/idk/SKILL.md").read_text(encoding="utf-8")
refdir = REPO / "skills/idk/references"
cited = sorted(set(re.findall(r"references/([A-Za-z0-9._-]+\.md)", skill)))
missing = [r for r in cited if not (refdir / r).exists()]
if missing:
    print("Broken references/ links cited in SKILL.md:")
    for m in missing:
        print(f"  - references/{m}")
    sys.exit(1)
print(f"All {len(cited)} references/ citations resolve.")
