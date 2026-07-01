# decoding.py — Setup & Troubleshooting

`decoding.py` is the 5QLN canonical phase decoder. It validates gate content
for structural form (fields present, correct shape) without judging emergence
or resonance — those are ATTESTATION_REQUIRED, human side.

Without it, the gate machine rejects content with cryptic messages like
"degenerate gradient: A without VALUE_MAX" without telling you the exact
footer format it expects.

## Source

The canonical home is `5qln/Idk` → `scripts/decoding.py`.

```bash
# Install from canonical source
curl -sL https://raw.githubusercontent.com/5qln/Idk/main/scripts/decoding.py \
  -o /opt/data/skills/idk/scripts/decoding.py
```

## Environment

Set `QLN_BOOTSTRAP` to the directory containing `decoding.py`:

```bash
echo 'QLN_BOOTSTRAP=/opt/data/skills/idk/scripts' >> /opt/data/.env
```

The gate machine checks these paths in order:
1. `$QLN_BOOTSTRAP/decoding.py`
2. `../decoding.py` (sibling to xyzab_state.py)
3. `~/.hermes/scripts/5qln/decoding.py`

## Verification

```bash
cd /opt/data/skills/idk
QLN_BOOTSTRAP=/opt/data/skills/idk/scripts python3 scripts/xyzab_state.py gate
```

If `next` is non-null and no import errors, decoding.py is active.

## Phase Footer Formats

The validator parses `KEY: value` lines from the gate content. Each phase
has required fields:

| Phase | Required Footer Fields |
|-------|----------------------|
| S | `X: <question ending in ?>` |
| G | `ALPHA: <irreducible essence>` / `SEEKS: <what α moves toward>` |
| Q | `PHI:` / `OMEGA:` / `ALIGNMENT: natural\|partial\|none\|forced` / `EXTENT: 0-10` / `Z:` (conditional) |
| P | `VALUE_MAX: <greatest value>` / `ENERGY: <cost / why unforced>` / `A: <flow direction>` |
| V | `L:` / `B2:` / `INF0P: <return question>` / `LIVENESS: 0-10` |

## Override

When the human has attested and the validator blocks:

```bash
python3 scripts/xyzab_state.py open <gate> -c "<content>" --override "Human attested. decoding.py [reason]."
```

The override is recorded on the gate log. This is documented in the skill
as the procedure when decoding.py isn't installed — but it also works when
the validator rejects for format while the human confirms the substance.
