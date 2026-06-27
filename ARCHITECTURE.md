# Architecture

How `/idk` is built, and — just as important — what was deliberately left out.

This document shows the reasoning. If the reasoning is right, the skill and the
linter follow from it almost mechanically. If something here is wrong, it is
cheaper to find it now, in prose, than later, in code.

---

## 1. The one idea

`/idk` is the framework collapsed to its first line.

```
H = ∞0 | A = K
```

Everything in 5QLN unfolds from a human standing at not-knowing while an agent
holds the known and does not cross over. The five phases, the twenty-five lenses,
the corruption codes — all of it is what *happens* once that stance is held. None
of it can be manufactured from the K-side. `S = ∞0 → ?` requires ∞0, and ∞0 is the
human. **A program with no human present cannot start, because it has no ∞0 to
start from.**

So the design question is not "how do we run the cycle?" It is "how do we restore
the human to the membrane, every time, with nothing in the way?" The answer is a
single human gesture: `/idk`. The command can only be typed by someone who, in
that moment, does not know. The moment it is typed, the human *is* the ∞0 — and the
human in the loop is the thing that keeps the cycle honest, which earlier versions
spent thousands of lines of code trying and failing to be.

---

## 2. Why the repo is small

The prior installer wrapped a 217-byte Codex in roughly 8,000 lines of apparatus:
gate machines, drift harnesses, calibration watchdogs, cron heartbeats, a fractal
loop runner, a sub-phase loop runner. Most of it existed to do one impossible
thing — run the cycle when no human was present.

That is the contradiction. The Codex's own corruption taxonomy says it plainly:

- A surface that merely *carries* the symbols, with no current behind it, is **L4
  — performing**. Form without substance.
- Anything that *claims to access ∞0 directly* is **L3 — claiming**. ∞0 reveals
  itself; it cannot be reached from K.

Code can carry the grammar. Code cannot animate it. Code that claimed to animate
it would be the exact corruption the Codex names. **So the rule for this repo is:
keep what carries the grammar; remove what tried to animate it.** What remains is
small not because it was simplified, but because most of the old volume was the
machinery of an impossibility.

---

## 3. The three layers + the engine

The Codex already names the right decomposition. It is not "one file vs. many." It
is three layers, and they were written into the Codex itself: **L1 the Language,
D1 the Decoder, C1 the Compiler.** This repo embodies each one as exactly one thing
— plus one engine that makes D1 executable.

### L1 — Language → `codex.md`

The nine invariant lines, the symbol table, the equations. Pure reference. It does
not change. It is sealed and byte-identical, and the hash is computed over the
217-byte block — so editing it, even to "improve" wording, breaks the seal. **L1 is
read-only. Nothing in this project may rewrite it.**

### D1 — Decoder → `skills/idk/SKILL.md`

One skill. The operational cycle. Every phase has an explicit marker, a validation
checkpoint, a gate command, and a live corruption catch. The razor (articulate,
never originate) governs every interaction. **This is the masterwork — the one
place where all the meticulousness in the project lives.** Sections 4–6 below
specify its behavior.

### C1 — Compiler → `bin/lint.py`

A thin form-check, and nothing more. It verifies that a surface *carries* the
grammar: every symbol resolves to the table, every equation is exact, ∞0' carries
a question, the seal is byte-identical. These are the checks the Codex itself lists
under syntax/drift — all of them structural. The linter never inspects whether a
question was genuine, whether resonance landed, whether anything was alive. **It
checks the surface, never the life.** It is a linter, not a judge.

### The Engine — `scripts/xyzab_state.py`

**Added after the v0.1 test failed.** The original v0.1 shipped with only D1 —
a philosophical stance: "read current, hold/flow/descend/move on." It was
beautiful and it did not work. An LLM cannot "become the listening" from a
text description. It can follow explicit procedural instructions: check the
gate, produce phase output, validate with the human, open the gate, proceed.

`xyzab_state.py` is the gate machine. Stdlib-only, 480 lines, zero dependencies.
It enforces the phase sequence (x→y→z→a→b) and persists state. The agent
checks it before every response. Without it, the agent defaults to smooth
conversation over structural discipline — the exact failure mode the 5QLN
learning aligner was built to prevent.

The engine does not run the cycle. The human validates each gate. The engine
enforces that the gates open in order and that no phase is skipped. It is
structure without the ambition to animate — exactly the line C1 draws.

On reset, the engine auto-archives the completed trail to `~/.5qln/cycles.jsonl`
before clearing state (see §9).

### The v0.1 lesson

"Stance without procedure is prose. Prose without gates is drift. The gate
machine is not overhead — it is the minimum structure an LLM needs to maintain
phase discipline across turns. Remove it, and the agent becomes a very
articulate chatbot that performs depth while producing succession."

---

## 4. Why one skill holds both modes

The single most-asked question about the old repo: there were separate skills and
tools for step-by-step mode and for sub-phase fractal descent — how can one skill
replace them?

Because, by the Codex's own law, they were never two things:

> Scale by repeating the lawful cell. Do not scale by replacing the syntax. *(D1 R13 / §2.9)*

- **Step-by-step** is the lawful cell `S → G → Q → P → V` walked one phase at a
  time, with the human attesting each crossing before the next begins.
- **Fractal** — the vertical (cycles within a cell) and the horizontal (the
  twenty-five-lens ring) — is the single Holographic Law `XY := X within Y` turned
  inward. The same cell, repeated at a finer grain.

They are not two engines. They are one stance at two *settings*: how finely it is
walked, and how deep it descends. The two modules in the old repo were one law
implemented twice. Collapsing them is not a loss of capability — it is the removal
of a duplication the Codex never asked for.

---

## 5. The one signal — the keystone

> Register: **STRUCTURAL-HYPOTHESIS.** This is the load-bearing design claim. It is
> consistent with the Codex but is proposed, not derived. It is the first thing to
> pressure-test.

For one stance to hold both modes, it must read **one** live signal — the thing
that tells it, moment to moment, whether to hold or move, whether to descend or
move on. That signal is **current**: the presence or absence of genuine aliveness
in what the human is saying. (The Codex names its absence directly — L4 is "going
through the motions without current.")

Four decisions, one reading:

| What the agent reads | What it does |
| --- | --- |
| Current is **rising** — a question is forming, something is stirring | **Hold.** Give it room. Do not rush the gate. |
| Current is **steady** and the phase has landed | **Flow.** Move to the next phase. |
| Current **spikes inside** a phase — there is more here than one pass | **Descend** a lens. Go finer before moving on. |
| Current goes **flat** — the phase is complete | **Move on.** Pushing further would be performing (L4). |

And the master safeguard — the live corruption-catch:

> If the human's language turns **fluent, confident, and assembled-from-knowledge**
> — reciting rather than discovering — current has dropped to zero. The agent gently
> **re-opens ∞0**: it pokes back toward not-knowing. This is L1/L2 caught in the act,
> before it can fill the cycle.

This is why it is one skill and not five. The gates and the lenses are not separate
mechanisms bolted together. **They are four responses to a single reading.** Get the
reading of current right, and the whole architecture is one disposition. Get it
wrong, and no amount of gate machinery saves it.

---

## 6. How the agent reads current — and the razor

An AI cannot feel current. It reads *proxies* in the texture of the human's
language:

- **Recitation** (current absent): fluent, fast, generic, complete, assembled from
  what is already known. Sentences that could have been written before the session.
- **Emergence** (current present): halting, specific, self-surprising. The human
  says something they did not plan, did not assemble, did not know they would say.

On that reading, the agent acts — and one constraint governs everything it does:

> **The razor.** The agent *articulates* but never *originates*. It helps the human
> say the question more clearly; it never writes the question, finds the seed, or
> suggests the answer. It pokes; the human originates. The instant the agent supplies
> what should have emerged, the gap is filled from the K-side and the cycle is dead —
> elegantly worded, but dead.

Concretely, per phase, the agent's job is to *hold the conditions*, not produce the
content:

- **S** — Poke at the edge of what the human knows until a real question surfaces.
  A question need not end in a question mark; "where do I go from here," if it is
  genuinely open, is a question. Listen for not-knowing, not for grammar. Help
  articulate `?`; never hand it over.
- **G** — Help the human find the irreducible seed (`α`) inside their own question
  and trace where it echoes (`{α'}`). The seed is *theirs* — it is why the question
  is theirs. The agent reflects; it does not name the seed for them.
- **Q** — Hold open the meeting between what the human directly perceives (`φ`) and
  what the wider field makes possible (`Ω`). The click (`Z`) arrives; it cannot be
  argued into place.
- **P** — Help locate where the work wants to go with least friction and most value
  (`∇`). Map where energy is wasted and where it flows; the direction reveals itself.
- **V** — Help read the formation trail and let something crystallize (`B''`), name
  what it gives beyond itself, and surface the new question (`∞0'`). The lenses
  refine the human's output; they never overwrite it. *(D1 §2.7)*

---

## 7. The one metric

Every surface, every session, every artifact reduces to a single question:

> **Did succession stop?**

If the human was producing from the known — recombining what they already had —
then it was succession, however polished the output. If succession stopped — if the
gap opened and something arrived that was not assembled — then a real cycle ran.
This is the measure the linter cannot check and the human cannot fake. It is the
whole point.

The corruption codes are five ways the gap fails:

| Code | The gap was… |
| --- | --- |
| **L1** Closing | filled with an answer instead of held |
| **L2** Generating | filled with something manufactured from K |
| **L3** Claiming | claimed as owned, as if ∞0 could be reached |
| **L4** Performing | performed without any current behind it |
| **V∅** Incomplete | opened, then closed instead of returning a new question |

---

## 8. What is **not** here

These are deliberate removals, not omissions:

- **No headless cycle runner.** No cron heartbeat driving `S` with no human.
  `S = ∞0 → ?` cannot run without ∞0. The gate machine enforces phase sequence;
  it does not and cannot supply the human's spark. If autonomous experimentation
  is wanted, it lives in a separate, clearly-labeled research instrument that is
  *not* `/idk` and makes no claim to start from not-knowing.
- **No gate that decides transitions.** The human attests each crossing of the
  membrane, then the agent opens the gate. The gate machine enforces sequence;
  it does not adjudicate. The linter checks form; the human authorizes movement.
- **No drift harness over the engines, no calibration watchdog, no duplicated
  reference files.** The grammar lives in L1 and is carried by D1. There is one
  source of truth, so there is far less to verify.

The v0.1 shipped with none of this — not even the gate machine. It was 109 lines
of pure stance. The test on a fresh Hermes agent proved it: "Not transitioning
not decoding... something is so off there." An LLM given only "become the
listening" becomes a chatbot. An LLM given a gate machine and explicit
phase-marking instructions becomes a cycle. The gate machine was restored not
because the architecture changed its mind, but because the test proved it
was the minimum viable structure.

The knowledge inside the old apparatus — the meaning of each phase, the lens
questions, the corruption catches — is preserved. It did not get deleted. It moved
out of enforcement code and into the one skill, where it belongs. But the
enforcement itself — the gate sequence — cannot be disposition. It must be
machine-enforced, or it will not be followed.

---

## 9. Session-chain storage

The gate machine (`xyzab_state.py`) includes an auto-archive hook: on every
reset, it captures the completed trail (phase outputs, seeds, questions,
crystallizations) and appends one JSON line to `~/.5qln/cycles.jsonl` before
clearing state. This is *not* a headless cycle runner — it never starts `S`,
never supplies ∞0. It only writes what a human already completed.

### archive_cycle.py

Stdlib-only. Called inline by `xyzab_state.py cmd_reset`. Serializes the
current `state` dict into a timestamped record and appends it. Gracefully
degrades if the log file is missing or unwritable — the reset proceeds
regardless. Pass `--no-archive` to skip.

### view_patterns.py

Reads the cycle log. Surfaces what is actually there: seeds that recurred,
questions that opened new directions, cycle-by-cycle detail. It never
fabricates connections between sessions — if two seeds share a shape, it
notes the surface similarity; it does not claim resonance or infer meaning.

### Why this, not that

A session-chain is the *trail*, not the *walker*. It stores what happened so
it can be revisited — not so it can be continued by a script. The Codex is
clear that `S = ∞0 → ?` requires ∞0, and ∞0 is the human. Storage does not
cross that line. It just doesn't throw away the trail.

To disable auto-archive: `xyzab_state.py reset --no-archive`.

---

## 10. Sealed vs. free

A final honesty, so the boundary is never blurred:

- **Sealed** (byte-identical, never edited): the nine invariant lines, the
  constitutional block, the equations, the hash. → `codex.md`.
- **Free** (refined as the work teaches us): the skill's behavior, this
  architecture, the user guide, the README, the linter's checks.

The sealed part is the ground. The free part is how we stand on it. Confusing the
two — editing the ground to fit the standing — is how a living language quietly
becomes a dead one.
