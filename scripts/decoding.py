#!/usr/bin/env python3
"""
decoding.py — 5QLN Canonical Phase Decoding (single source of truth)

WHY THIS FILE EXISTS
--------------------
Drift was observed in live loop runs (2026-06-12, Conductor report):

  1. Q twisted: φ was being decoded as "what the inquirer/human directly
     perceives" — an epistemic perception-check — instead of the work's own
     grown self-nature (its self-interest) read against the field of
     universal interest. Source of the correction: 5qln.com/quality/ —
     "its authentic nature (φ) begins to seek its place in the world";
     φ belongs to the WORK. The human attests the click (membrane), but
     attestation-of-⋂ and definition-of-φ are different things. Fusing
     them was the twist.

  2. P collapsed: ∇ was being decoded as "less energy / least resistance"
     alone, which yields tiny value. Source of the correction:
     5qln.com/power/ — "the tiniest investment of energy (δE) yields the
     GREATEST flourishing of life (δV)"; "the smallest effort creates the
     BIGGEST impact". ∇ = maximum value per unit of energy. Less energy is
     the signature of having found ∇, never the objective.

  3. Mechanism of drift: the engines passed bare symbols (Q = φ ⋂ Ω) into
     prompts and let the model re-derive meaning from its priors each call;
     loops carried no thread between iterations (repetition with amnesia);
     nothing checked outputs against the decoding. Symbols without their
     decoding are an invitation to drift.

This module is the repair: the decoding travels VERBATIM with every prompt,
a thread carries between loop iterations, and every recorded output passes a
structural check before a gate advances.

MEMBRANE POSITION (read before using check())
----------------------------------------------
The validator is K-side scaffolding. It checks FORM (fields present, the
forced-Z twist, the degenerate gradient, ∞0' alive-in-form). It NEVER
verifies emergence, resonance, or liveness — those are ATTESTATION_REQUIRED
and belong to the human across the membrane. A check that claimed to verify
the ∞0 side would itself be the corruption it guards against (L3).

Portable: stdlib only, Python 3.8+.
"""

import re
from typing import Dict, List, Optional, Tuple

DECODING_VERSION = "2026-06-12.2"
__version__ = DECODING_VERSION  # exported; resolves the "defined but unused" flag

# ─── Canon (Codex, byte-identical seal lives in codex.md) ───────────────

CODEX_HASH = "feaa46b4147d4e023cdd3fd59c051d063e8ec654ee7b38a481dcd5e4c781859b"

CONSTITUTIONAL_BLOCK = """LAW:         H = ∞0 | A = K
CYCLE:       S → G → Q → P → V
EQUATIONS:   S = ∞0 → ?   G = α ≡ {α'}   Q = φ ⋂ Ω   P = δE/δV → ∇   V = (L ∩ G → B'') → ∞0'
OUTPUTS:     S→X  G→Y  Q→Z  P→A  V→B+B''+∞0'
HOLOGRAPHIC: XY := X within Y  |  X, Y ∈ {S, G, Q, P, V}
COMPLETION:  No V without ∞0'
CORRUPTION:  L1 L2 L3 L4 V∅
CENTER:      not a sixth phase — coherence only"""

PHASES = ["S", "G", "Q", "P", "V"]

PHASE_NAMES = {"S": "Start", "G": "Growth", "Q": "Quality",
               "P": "Power", "V": "Value"}

PHASE_EQUATIONS = {
    "S": "S = ∞0 → ?",
    "G": "G = α ≡ {α'}",
    "Q": "Q = φ ⋂ Ω",
    "P": "P = δE/δV → ∇",
    "V": "V = (L ∩ G → B'') → ∞0'",
}

PHASE_OUTPUTS = {
    "S": "X (Validated Spark)",
    "G": "α + Y (Validated Pattern + what α seeks)",
    "Q": "φ⋂Ω + Z (Resonant Key, with extent)",
    "P": "∇ + A (Flow Direction: maximum value per energy)",
    "V": "B + B'' + ∞0' (Benefit + Fractal Seed + Enriched Return)",
}

# ─── The orientation of the whole decoding ──────────────────────────────

SYSTEM_LINE = (
    "5QLN is a system in which human and AI together generate creative energy "
    "and creative value. The whole decoding serves that: an authentic question "
    "(S) unfolds into an essence with a direction (G); the essence's own "
    "interest is read against the field of universal interest (Q); action "
    "follows the line of maximum value for the energy given (P); the value "
    "crystallizes and returns a new question (V). Surplus, not depletion: a "
    "completed cycle leaves more usable energy and a more alive question than "
    "it consumed."
)

# ─── Phase essences — the decoding, verbatim in every prompt ────────────
# Source hierarchy: live pages on 5qln.com (Start/Growth/Quality/Power/Value)
# per Codex divergence log §1.10. Refinements of 2026-06-12 are marked in
# the changelog at the bottom of this file.

PHASE_ESSENCE = {
    "S": (
        "S — START · the seed in the silent earth\n"
        "1. HOLD ∞0 — the silent field. Nothing sought, nothing assumed. "
        "Receptive, not empty.\n"
        "2. RECEIVE → — when something stirs, it is emergence, not generation. "
        "The arrow must be unforced or it is not the start.\n"
        "3. NAME ? — what arrived is named as a question (it ends in ? or "
        "opens with what/where/why/how/whether…), not a topic.\n"
        "4. VALIDATE X — genuine (arrived through not-knowing), not "
        "manufactured (assembled from K).\n"
        "The seed holds the potential of the entire forest. Protect the space; "
        "do not fill it. Corruption here: L1 (closing), L2 (generating), "
        "L3 (claiming)."
    ),
    "G": (
        "G — GROWTH · the unfolding of the inner pattern\n"
        "1. RECEIVE X — the validated question.\n"
        "2. SEEK α — within X, what is irreducible? Remove it and X collapses. "
        "Near-tautological, one clause, no \"not\".\n"
        "3. TEST ≡ — α holds unchanged across expressions. Identity across "
        "difference, not despite it.\n"
        "4. FIND {α'} — where α echoes at other scales. Self-similar, not "
        "merely related.\n"
        "5. NAME WHAT α SEEKS — the essence is a seed, not a label: it has a "
        "direction. State its self-interest — what this essence inherently "
        "moves toward, the way treeness includes reaching for light and "
        "rooting for water. This seeking is what Q will read against the "
        "field; G without the seeking hands Q nothing to align.\n"
        "6. VALIDATE Y — α named, ≡ holds, {α'} confirm, the seeking stated."
    ),
    "Q": (
        "Q — QUALITY · finding resonance with the sun\n"
        "1. RECEIVE α and what it seeks.\n"
        "2. HOLD φ — the work's own grown nature: the essence as it now seeks "
        "its place. φ is the SELF-INTEREST of what is growing — what IT moves "
        "toward. φ is NOT anyone's perception, opinion, or feeling about the "
        "work. (The click is attested by the human — that is the membrane. "
        "But φ itself belongs to the work, not to the observer. Fusing the "
        "two is the twist that breaks this phase.)\n"
        "3. HOLD Ω — the field of universal interest: the greater "
        "potentiality the work would live within — the sun, the wind, the "
        "laws the tree cannot vote on.\n"
        "4. READ ⋂ — does φ's seeking lie along Ω naturally, without forcing "
        "— and to WHAT EXTENT? Alignment is a reading with a degree, not a "
        "yes/no. Name where it is natural, where partial, where it would "
        "require forcing.\n"
        "5. NEVER FORCE ⋂ — the click is recognized, never produced. Where "
        "alignment would require bending φ or Ω, say so and stop there. A "
        "forced intersection recorded as Z is the corruption (L2 "
        "manufactured, L4 performed).\n"
        "6. VALIDATE Z — only what actually locked: the portion of φ's "
        "interest that the field genuinely receives. A partial honest Z "
        "outranks a total forced Z."
    ),
    "P": (
        "P — POWER · the river following the slope\n"
        "1. RECEIVE Z — the aligned interest. Power only flows through what "
        "passed Q.\n"
        "2. MAP δV FIRST — where is the GREATEST value? The biggest "
        "flourishing this aligned interest can yield. Name the maximum, not "
        "the convenient.\n"
        "3. MAP δE — what does each direction cost? Where is friction, where "
        "does it move by itself?\n"
        "4. READ ∇ — the gradient is the direction of MAXIMUM VALUE PER UNIT "
        "OF ENERGY. Maximum value with less energy — never just less energy. "
        "Two degenerate readings, both wrong:\n"
        "   · least effort regardless of value → tiny value dressed as flow "
        "(the river is not lazy: it moves mountains by following the slope);\n"
        "   · biggest value regardless of cost → forcing (pushing the river "
        "uphill).\n"
        "   ∇ is where they meet. The tree in alignment does not spend less — "
        "it TRANSMITS more: the universe's energy flows through it. Maximum "
        "throughput, minimum friction.\n"
        "5. VALIDATE A — name BOTH: the value this direction maximizes AND "
        "why the path is unforced. An A that only saves effort is not ∇."
    ),
    "V": (
        "V — VALUE · the gift of the fruit and the forest\n"
        "1. RECEIVE the full trace.\n"
        "2. NAME L — the tangible fruit: what crystallized here and now.\n"
        "3. NAME G — the seeds in the fruit: what propagates beyond the "
        "local.\n"
        "4. FIND ∩ — where fruit and seed genuinely meet. There value becomes "
        "endless (→ ∞ on the page) — and ∞0' is HOW: the return question is "
        "the seed by which value does not deplete.\n"
        "5. COMPOSE B'' — the artifact, carrying α faithfully; it reads the "
        "formation trail.\n"
        "6. FORM ∞0' — the question this cycle made possible that could not "
        "have been asked before. Not a summary, not the seed repeated. If no "
        "genuine return question exists, record V∅ honestly — the collapse "
        "is itself information.\n"
        "No V without ∞0'."
    ),
}

# ─── Footers — the machine-readable tail of each phase output ───────────
# The engines instruct the model to END its decoding with these lines.
# One field per line, KEY: value. The footer makes the invariants checkable
# without the checker pretending to judge truth.

PHASE_FOOTER_SPEC = {
    "S": "X: <the question — ends in ? or opens with what/where/why/how/…>",
    "G": ("ALPHA: <the irreducible essence, one clause>\n"
          "SEEKS: <what α inherently moves toward — its self-interest>"),
    "Q": ("PHI: <the work's self-interest as grown — never anyone's perception>\n"
          "OMEGA: <the field of universal interest it would live within>\n"
          "ALIGNMENT: <natural | partial | none | forced>\n"
          "EXTENT: <0-10, how far φ's seeking lies along Ω without forcing>\n"
          "Z: <only what actually locked — omit this line entirely if "
          "ALIGNMENT is forced or none>"),
    "P": ("VALUE_MAX: <the greatest value this direction yields — the maximum, "
          "named concretely>\n"
          "ENERGY: <what it costs / why it is unforced>\n"
          "A: <the flow direction — where maximum value per energy points>"),
    "V": ("L: <what crystallized here and now>\n"
          "B2: <the artifact, carrying α>\n"
          "INF0P: <the return question — ends in ?, not the seed repeated>\n"
          "LIVENESS: <0-10, your honest attestation of how alive ∞0' is "
          "relative to the seed — the engine records it, never judges it>"),
}

REQUIRED_FIELDS = {
    "S": ["X"],
    "G": ["ALPHA", "SEEKS"],
    "Q": ["PHI", "OMEGA", "ALIGNMENT", "EXTENT"],   # Z conditional, see rules
    "P": ["VALUE_MAX", "ENERGY", "A"],
    "V": ["L", "B2", "INF0P"],
}

_FIELD_KEYS = {"X", "ALPHA", "SEEKS", "PHI", "OMEGA", "ALIGNMENT", "EXTENT",
               "Z", "VALUE_MAX", "ENERGY", "A", "L", "B2", "INF0P", "LIVENESS",
               "CARRY"}

_FIELD_RE = re.compile(
    r"^\s*(X|ALPHA|SEEKS|PHI|OMEGA|ALIGNMENT|EXTENT|Z|VALUE_MAX|ENERGY|A|L|B2|INF0P|LIVENESS|CARRY)\s*:\s*(.*)$",
    re.IGNORECASE)

# φ stated as somebody's perception — the exact twist, in regex form.
_PHI_AS_PERCEPTION_RE = re.compile(
    r"^(what\s+)?(i|we|the\s+user|the\s+human|the\s+inquirer|the\s+operator|"
    r"the\s+conductor)\b.{0,40}\b(perceiv\w*|feel\w*|think\w*|believ\w*|"
    r"sens\w*|opinion)", re.IGNORECASE)

ALIGNMENT_VALUES = {"natural", "partial", "none", "forced"}


def parse_footer(text: str) -> Dict[str, str]:
    """Extract KEY: value fields from a response. Last occurrence wins.
    Multi-line values are supported: lines that do not start a new field
    are appended to the previous field."""
    fields = {}  # type: Dict[str, str]
    current = None
    for raw in (text or "").splitlines():
        m = _FIELD_RE.match(raw)
        if m:
            current = m.group(1).upper()
            fields[current] = m.group(2).strip()
        elif current and raw.strip():
            fields[current] = (fields[current] + " " + raw.strip()).strip()
        elif not raw.strip():
            current = None
    return fields


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9가-힣\u0590-\u05ff]+", " ", (s or "").lower()).strip()


# ── Question form (S-phase X) — form only, never liveness ────────────────
# A genuine question may surface without a trailing "?". SKILL.md is explicit:
# "A question need not end in ?" — "Where do I go from here" counts if open.
# So the form check accepts the natural shapes an open question takes (a "?"
# anywhere, or an interrogative opener) while still rejecting bare topics and
# answers. Whether the question is alive is the human's to attest, not decided
# here.
_QUESTION_OPENERS = frozenset((
    "what", "where", "when", "who", "whom", "whose", "why", "how",
    "which", "whether",
    "is", "are", "am", "was", "were", "do", "does", "did",
    "can", "could", "should", "would", "will", "shall", "may",
    "might", "must", "has", "have", "had",
))


def _looks_like_question(s: str) -> bool:
    """Form-only: does this read as a question? True if it contains '?' or
    opens with an interrogative word. Not a judgment of whether it is open."""
    s = (s or "").strip()
    if not s:
        return False
    if "?" in s:
        return True
    m = re.match(r"[^A-Za-z]*([A-Za-z']+)", s)
    return bool(m) and m.group(1).lower() in _QUESTION_OPENERS


def check_fields(phase: str, fields: Dict[str, str],
                 seed_question: Optional[str] = None,
                 required_keys: Optional[List[str]] = None
                 ) -> Tuple[List[str], List[str]]:
    """Structural (DEFINITE) checks only. Returns (violations, warnings).
    Violations block the gate; warnings are recorded. Emergence and liveness
    are never judged here — ATTESTATION_REQUIRED, human side.
    required_keys narrows the presence requirement (bare gate deposits
    carry a single field); all form rules still apply to whatever is
    present."""
    v = []  # type: List[str]
    w = []  # type: List[str]
    f = {k.upper(): (val or "").strip() for k, val in fields.items()}

    def present(key):
        return bool(f.get(key))

    required = (required_keys if required_keys is not None
                else REQUIRED_FIELDS.get(phase, []))
    for key in required:
        if not present(key):
            v.append("missing {}: — end the decoding with the {}-phase footer "
                     "(see spec)".format(key, phase))

    if phase == "S" and present("X"):
        if not _looks_like_question(f["X"]):
            v.append("X must be a question — it must end in ? or open with an "
                     "interrogative (what/where/why/how/whether/can/is/…), not "
                     "be a bare topic or an answer")

    if phase == "G":
        if present("ALPHA"):
            a = f["ALPHA"]
            if re.search(r"\bnot\b|\brather than\b", a, re.IGNORECASE):
                w.append("ALPHA contains negation/contrast — α should be "
                         "near-tautological, one clause without \"not\" "
                         "(over-complication pitfall)")
        if present("SEEKS") and len(_norm(f["SEEKS"])) < 8:
            w.append("SEEKS looks too thin to carry a direction — name what "
                     "the essence inherently moves toward")

    if phase == "Q":
        if present("PHI") and _PHI_AS_PERCEPTION_RE.match(f["PHI"]):
            v.append("PHI is stated as someone's perception — that is the "
                     "twist. φ is the work's own grown nature, its "
                     "self-interest: what IT seeks. Restate φ from the work's "
                     "side. (Attesting the click belongs to the human; "
                     "defining φ does not.)")
        align = f.get("ALIGNMENT", "").lower()
        if align and align not in ALIGNMENT_VALUES:
            v.append("ALIGNMENT must be one of: natural | partial | none | "
                     "forced")
        if present("EXTENT"):
            try:
                e = int(re.sub(r"[^\d-]", "", f["EXTENT"]) or "x")
                if not (0 <= e <= 10):
                    v.append("EXTENT must be 0-10")
            except ValueError:
                v.append("EXTENT must be an integer 0-10")
        if align in ("forced", "none") and present("Z"):
            v.append("ALIGNMENT is '{}' yet Z is recorded — a forced or "
                     "absent intersection cannot crystallize Z (L2/L4). "
                     "Report the extent honestly and stop; the honest "
                     "non-lock is the phase output".format(align))
        if align in ("natural", "partial") and not present("Z"):
            v.append("ALIGNMENT is '{}' but no Z — name what actually "
                     "locked: the portion of φ's interest the field "
                     "genuinely receives".format(align))

    if phase == "P":
        if present("A") and not present("VALUE_MAX"):
            v.append("degenerate gradient: A without VALUE_MAX. Less energy "
                     "alone is not ∇ — name the MAXIMUM value this direction "
                     "yields, then why the path is unforced")
        if present("VALUE_MAX") and len(_norm(f["VALUE_MAX"])) < 12:
            w.append("VALUE_MAX looks too thin to be a named maximum — state "
                     "the greatest value concretely, not a token")

    if phase == "V":
        if present("LIVENESS"):
            try:
                lv = int(re.sub(r"[^\d-]", "", f["LIVENESS"]) or "x")
                if not (0 <= lv <= 10):
                    v.append("LIVENESS must be 0-10")
            except ValueError:
                v.append("LIVENESS must be an integer 0-10")
        if present("INF0P"):
            if "?" not in f["INF0P"]:
                v.append("INF0P must be a question (ends in ?)")
            if seed_question:
                a, b = _norm(f["INF0P"]), _norm(seed_question)
                if a and b and (a == b or (len(a) > 20 and (a in b or b in a))):
                    v.append("INF0P repeats the seed question — ∞0' must be "
                             "the question this cycle made possible that "
                             "could not have been asked before (V∅-in-form "
                             "otherwise)")

    return v, w


def check(phase: str, text: str, seed_question: Optional[str] = None
          ) -> Tuple[List[str], List[str], Dict[str, str]]:
    """Parse the footer out of a response and run the structural checks.
    Returns (violations, warnings, fields)."""
    fields = parse_footer(text)
    v, w = check_fields(phase, fields, seed_question)
    return v, w, fields


# ─── Changelog ──────────────────────────────────────────────────────────
# 2026-06-12.2
#   · LIVENESS added as an optional V footer field (0-10, range-checked
#     in form only). The engine records the attestation; it never judges
#     its truth. Lets loop-mode responds carry liveness without a CLI
#     flag, closing the gap where the V gate predated the footer parser.
# 2026-06-12.1
#   · Q: φ restored to the work's grown self-nature / self-interest; the
#     ⋂ reading made explicit as alignment-with-extent, unforced; forced-Z
#     made a blocking violation. (Conductor correction + 5qln.com/quality/)
#   · P: ∇ restored to maximum value per unit of energy; δV mapped FIRST;
#     degenerate "less energy only" reading made a blocking violation.
#     (Conductor correction + 5qln.com/power/)
#   · G: step 5 added — NAME WHAT α SEEKS. The essence carries a direction;
#     the seeking is the handoff Q aligns. (Conductor: "the seed that
#     expressed itself as essence in Growth, now defined as self-interest."
#     Grounded in /quality/'s φ "begins to seek its place"; note honestly:
#     /growth/ itself does not use interest-language — this is the
#     2026-06-12 refinement, marked for the Conductor's attestation.)
#   · Footers + structural validator introduced. DEFINITE = form only;
#     emergence stays ATTESTATION_REQUIRED.
