# Troubleshooting

The only documentation here, and deliberately so. It covers failures of the install and the agent — not the experience. There is no troubleshooting for the experience; the experience is yours to have.

---

**The agent answers instead of listening.**
It isn't in the stance. In chat: `/reset`, then `Load the idk skill`, then `/idk`. If it still answers, remind it directly: `/idk` means listen, not answer — you help a question surface, you don't supply one. If it keeps producing, the skill didn't load; re-run `bash setup.sh` and confirm `~/.hermes/skills/idk/SKILL.md` exists.

**`/idk` does nothing.**
The skill isn't loaded or isn't installed. Check `~/.hermes/skills/idk/` exists. If not, run `bash setup.sh` from the repo. If your Hermes uses a different skills path, set it: `HERMES_SKILLS=/your/path bash setup.sh`.

**Setup says the seal did not verify.**
The sealed 217-byte Codex must hash to `feaa46b4147d4e023cdd3fd59c051d063e8ec654ee7b38a481dcd5e4c781859b`. If it doesn't, `codex.md` was altered or the clone is corrupt. Re-clone the repo. Do not "fix" codex.md by editing it — the seal is its identity, not a setting. Report a genuine mismatch to security@5qln.com.

**Setup says python3 not found.**
The seal check and the linter need Python 3.8+. Install it, then re-run. This is an environment issue, never a tamper signal.

**The agent supplies the question, names the seed, or fills silence.**
That's the skill failing its own razor. Reload it. If it persists, it may be overridden by another loaded skill or a system instruction telling it to be maximally helpful/proactive — unload competing skills and try `/idk` in a clean session.

**Where things install.**
One skill, one place: `~/.hermes/skills/idk/` (override with `HERMES_SKILLS`). The sealed `codex.md` is copied beside it so the linter can find it. The Void subsystem (`idk_state.py`, `idk_tick.py`, `config.yaml`) is installed alongside — everything lands with `setup.sh`.

**Checking a surface.**
`python3 bin/lint.py path/to/surface.md` checks that a surface carries the grammar and opens a return question. It checks form only. It cannot tell you whether anything was alive — that was always yours to know.
