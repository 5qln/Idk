# Audit Validation Pattern — 5qln/Idk

When an external audit of the idk codebase arrives, do not trust its claims.
Re-run every check empirically against a fresh clone. This reference documents
the verification technique and the specific pitfalls found in the glm2 (Super Z)
audit at commit d7017f17.

## Technique

1. **Clone fresh.** Do not work from the existing working copy. The audit may
   reference a different commit or branch state.
2. **Run every claim.** Seal verification, line counts, lint failures, config
   key traces, gate machine behavior — execute, don't infer.
3. **Cross-reference counts.** Audit metadata (file counts, line sums) is often
   loose — verify denominators independently.
4. **Trace every config key.** Search all Python files for the key name; follow
   every read path. The audit may claim a key is "inert" when it's actually
   load-bearing (see M7 below).
5. **Check for CI.** The audit may claim "no tests/CI" — verify `.github/workflows/`
   exists. The repo already has `seal.yml`.
6. **Test the gate machine live.** Run through out-of-order opens, non-question
   inputs, valid interrogative openings. The gate is the repo's load-bearing
   mechanism — verify it works, don't just read the code.
7. **Produce a validation report** with three sections: what reproduced,
   where the audit is wrong/overstated, and what the audit missed.
8. **Recalibrate severity.** Some audits inflate severities (authoring tools
   marked CRITICAL, edge cases marked HIGH). Re-rate against actual impact.

## Specific pitfalls found in the glm2 audit

### M7 — "inert" config key that wasn't inert
The audit claimed `xyzab_integration` and `corruption_checks` are both
"inert, never checked by any code path." Only `corruption_checks` is inert.
`xyzab_integration` is read at `idk_state.py:192` inside `cmd_crystallize` —
it gates the entire Void→gate handoff. Setting it false silently bypasses
gate enforcement. **Lesson: trace every config key read path, not just the
key name.**

### Metadata counts are untrustworthy
"16 files / 3,445 lines" → actually 20 files, sum is 3,480.
"7 of 9 markdown files" → 7 of 8. The audit's own A.4 table lists 18 files.
**Lesson: count independently; audit denominators are often wrong.**

### CI exists but is thin
`.github/workflows/seal.yml` runs lint on every push/PR. The audit claimed
"no CI." The seal IS gated; the gate machine is not.
**Lesson: check for CI workflows before accepting "no tests" claims.**

### H3 may be a non-finding
The audit claimed ARCHITECTURE §8 needed a driving-vs-monitoring distinction
that was already present (line 248: "No cron heartbeat **driving** S",
line 264: "a cron heartbeat that **monitors**… it watches").
**Lesson: read the actual doc text, not just the audit's paraphrase of it.**

### C3 fix is epistemically fragile
The dead L4 counter can be revived, but the detector relies on agent
self-report — an agent in L4 drift may stop self-reporting. The fix
raises the floor, not the ceiling.
**Lesson: note epistemic limits of self-reporting detectors honestly.**

## Gate machine verification checklist

```bash
# Fresh cycle
python3 scripts/xyzab_state.py reset
python3 scripts/xyzab_state.py gate  # should show "x" pending

# Out-of-order: try opening y before x
python3 scripts/xyzab_state.py open y -c "..."  # should reject

# Non-question input
python3 scripts/xyzab_state.py open x -c "not a question"  # should reject

# Valid interrogative opening (no ?)
python3 scripts/xyzab_state.py open x -c "X: where do I go from here"  # should accept

# Persist and verify
python3 scripts/xyzab_state.py gate  # should show "y" pending
```

## Tier 1 fixes applied (June 2026, PR #10)

Three fixes were implemented from the validation report, in priority order:

### 1. C1 — Source vs surface (lint.py)
The linter now auto-detects the Codex as the grammar's *source* (not a compiled
surface) by hashing the nine-line block — principled, not a filename guess.
Only the real Codex can pass `is_codex_source()`. `--source`/`--allow-source`
flags for drafts. README now says "compiled surface" not "every genuine surface."

**Pitfall caught during review:** The original `is_codex_source` regex required
a trailing newline after the closing fence (`\n```\n`). If `codex.md` is saved
without a trailing newline, the regex silently fails and codex.md gets linted
as a surface again. Fixed: `\n```(?:\n|$)` accepts end-of-string.

### 2. C3 — Dead L4 detector (idk_state.py)
New `cmd_output` hook — the agent calls it once per Void response. Counter
increments, L4 triggers at `>=` threshold (default 3). `cmd_fragment` resets
the streak to 0 (human input breaks the performing pattern). Honesty note in
the docstring: self-report raises the floor, not the ceiling.

**Off-by-one fix:** Original code used `> threshold` which required 4 outputs
to trigger L4, but docs said "3+." Changed to `>=` to match docs.

### 3. M7 — xyzab_integration fail-open (idk_state.py)
The audit called `xyzab_integration` "inert" — it isn't. `cmd_crystallize` reads
it and bypasses the gate when it's off. Now: if integration is off but a gate
machine is present on PATH, crystallize is **refused** unless `--override` is
passed (which logs a `gate_bypass` corruption flag). Three tiers: normal
gate validation / human-override / standalone (no gate reachable).

## Installed-skill vs repo divergence

The installed skill at `$HERMES_HOME/skills/idk/SKILL.md` may accumulate
sections (FCF fragments, gateway slash command docs) that are never pushed
back to the repo at `5qln/Idk`. When making changes:
- Code changes (scripts, lint.py) go to the repo and are pushed.
- SKILL.md changes may be applied to the installed copy directly via
  skill_manage — if so, also push them to the repo.
- The repo is the source of truth for code; the installed skill is the
  runtime copy the agent reads. They can diverge. Check both.

## File inventory verification

```bash
# Count actual files
find . -type f -not -path './.git/*' | wc -l

# Count lines per file
find . -type f -not -path './.git/*' -exec wc -l {} + | sort -n

# Verify .md file count
find . -name '*.md' -not -path './.git/*' | wc -l
```
