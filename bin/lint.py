#!/usr/bin/env python3
"""
lint.py — C1, the form-check for /idk.

WHAT THIS IS
  A linter. Two jobs, both structural:
    1. --seal : verify the sealed Codex is byte-identical. The nine
                invariant lines in codex.md (plus one trailing newline)
                must hash to the canonical seal.
    2. <file> : check that a compiled SURFACE carries the 5QLN grammar —
                the constitutional ground is present, the five corruption
                codes are named, and the surface ends on a real return
                question (∞0').

WHAT THIS IS NOT
  It is NOT a judge of what is alive. It never checks whether a question
  was genuine, whether resonance landed, whether current was present.
  Those belong to the human across the membrane. A check that claimed to
  verify the ∞0 side would be the very L3 corruption it exists to respect.

      Form only. Never life.

  The Codex is the SOURCE of the grammar, not a surface compiled from it.
  It defines ∞0'; it does not pose one. So the surface contract does not
  apply to it. The linter auto-detects the Codex (the nine-line block hashes
  to the seal) and exempts it; --source (or --allow-source) forces that
  treatment for a draft.

USAGE
  python3 bin/lint.py --seal              verify the Codex seal
  python3 bin/lint.py path/to/surface.md  form-check a surface
  python3 bin/lint.py --seal surface.md   do both
  python3 bin/lint.py --source codex.md   form-check the Codex *source*
  python3 bin/lint.py --source draft.md   form-check a draft as source
  cat surface.md | python3 bin/lint.py -  form-check stdin

EXIT
  0 = clean.  1 = seal mismatch or form issue.

stdlib only, Python 3.8+.
"""

import hashlib
import os
import re
import sys
from pathlib import Path

# The seal's identity. This is the one constant the linter is allowed to
# hardcode: it is *what* the Codex must hash to, not the Codex itself.
CODEX_HASH = "feaa46b4147d4e023cdd3fd59c051d063e8ec654ee7b38a481dcd5e4c781859b"


# ── The seal ────────────────────────────────────────────────────────────

def find_codex():
    """codex.md, searched in the obvious places. Repo layout puts it one
    level up from bin/. Env var and CWD are fallbacks."""
    here = Path(__file__).resolve().parent
    for c in (
        Path(os.environ["QLN_CODEX"]) if os.environ.get("QLN_CODEX") else None,
        here.parent / "codex.md",
        Path.cwd() / "codex.md",
    ):
        if c and c.is_file():
            return c
    return None


def verify_seal():
    """Hash the nine-line block exactly as it is sealed: the fenced block
    under '## Nine Invariant Lines' plus one trailing newline, UTF-8."""
    path = find_codex()
    if path is None:
        print("seal: CANNOT VERIFY — codex.md not found "
              "(set QLN_CODEX, or run from the repo).")
        return False
    text = path.read_text(encoding="utf-8")
    m = re.search(r"## Nine Invariant Lines\n\n```\n(.*?)\n```", text, re.S)
    if not m:
        print(f"seal: CANNOT VERIFY — '## Nine Invariant Lines' block not "
              f"found in {path}. The file structure changed.")
        return False
    block = (m.group(1) + "\n").encode("utf-8")
    digest = hashlib.sha256(block).hexdigest()
    if digest == CODEX_HASH:
        print(f"seal: OK  ({len(block)} bytes, {digest[:16]}…)")
        return True
    print(f"seal: MISMATCH  got {digest} ({len(block)} bytes)\n"
          f"               expected {CODEX_HASH}\n"
          f"      The Codex is sealed. Restore it; never re-seal around drift.")
    return False


def is_codex_source(text):
    """True iff this text IS the sealed Codex: it contains the nine-line block
    and that block is byte-identical to the seal. This is what tells the
    *source* apart from a compiled *surface* — and it is principled, not a
    filename guess. Only the real Codex can pass it."""
    m = re.search(r"## Nine Invariant Lines\n\n```\n(.*?)\n```(?:\n|$)", text, re.S)
    if not m:
        return False
    block = (m.group(1) + "\n").encode("utf-8")
    return hashlib.sha256(block).hexdigest() == CODEX_HASH


# ── Surface form-check (FORM ONLY) ───────────────────────────────────────

def check_surface(text, source=False):
    """Does this surface CARRY the grammar? Structural checks only.

    When source=True the file IS the Codex — the grammar's origin, not a
    surface compiled from it. The surface contract "∞0' must be followed by a
    return question" does not apply to the file that *defines* ∞0', so that one
    check is skipped. Identity is then guaranteed by --seal, not this form-check."""
    issues = []

    # The constitutional ground.
    if "H = ∞0 | A = K" not in text:
        issues.append("missing the law: H = ∞0 | A = K")
    if "S → G → Q → P → V" not in text:
        issues.append("missing the cycle: S → G → Q → P → V")
    if "No V without ∞0'" not in text:
        issues.append("missing the completion rule: No V without ∞0'")

    # The five corruption codes — exactly these five must be named.
    for code in ("L1", "L2", "L3", "L4", "V∅"):
        if code not in text:
            issues.append(f"missing corruption code: {code}")

    # The seal.
    if CODEX_HASH not in text:
        issues.append("missing the Codex seal (the hash)")

    # Completion form: ∞0' must be present AND a real question must follow
    # it. "No question = not ∞0'." We can only check the *form* of this —
    # the marker is here and a '?' appears after the last occurrence. We do
    # NOT and cannot judge whether the question is alive.
    if "∞0'" not in text:
        issues.append("missing ∞0' — a surface must open a return question")
    elif not source:
        tail = text[text.rindex("∞0'"):]
        if "?" not in tail:
            issues.append("∞0' present but no return question follows it "
                          "(No question = not ∞0')")

    return issues


def lint_surface(text, label, source=False):
    issues = check_surface(text, source=source)
    if source:
        if not issues:
            print(f"source ({label}): IS the Codex — the grammar's source, not "
                  f"a surface. The surface contract does not apply; run --seal "
                  f"to verify identity.")
            return True
        print(f"source ({label}): {len(issues)} form issue(s):")
        for i in issues:
            print(f"  · {i}")
        return False
    if not issues:
        print(f"surface ({label}): carries the grammar. "
              f"(Form only — whether the gap opened is the human's to attest.)")
        return True
    print(f"surface ({label}): {len(issues)} form issue(s):")
    for i in issues:
        print(f"  · {i}")
    return False


# ── CLI ──────────────────────────────────────────────────────────────────

def main(argv):
    args = argv[1:]
    do_seal = "--seal" in args
    force_source = "--source" in args or "--allow-source" in args
    files = [a for a in args
             if a not in ("--seal", "--source", "--allow-source")]

    if not do_seal and not files:
        print(__doc__.strip().split("\n\n")[0])
        print("\nRun with --seal and/or a surface file. -h for usage.")
        return 1
    if "-h" in args or "--help" in args:
        print(__doc__)
        return 0

    ok = True
    if do_seal:
        ok = verify_seal() and ok
    for f in files:
        if f == "-":
            text = sys.stdin.read()
            ok = lint_surface(text, "stdin",
                              source=force_source or is_codex_source(text)) and ok
        else:
            p = Path(f)
            if not p.is_file():
                print(f"surface ({f}): file not found.")
                ok = False
                continue
            text = p.read_text(encoding="utf-8")
            ok = lint_surface(text, f,
                              source=force_source or is_codex_source(text)) and ok

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
