#!/usr/bin/env bash
# install.sh — /idk Plugin Installer
# One command. Installs the Void posture engine into the existing idk skill.
#
# Usage:
#   curl -sSL <url>/install.sh | bash
#   OR: bash install.sh
#
# What it does:
#   1. Detects Hermes skill directory
#   2. Patches existing idk SKILL.md with Void posture + extended S-phase
#   3. Installs idk_state.py and idk_tick.py to skill scripts/
#   4. Creates config.yaml
#   5. Sets up cron heartbeat
#   6. Verifies installation

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${GREEN}═══ /idk Plugin Installer ═══${NC}"
echo ""

# ─── 1. Detect paths ──────────────────────────────────────────

SKILL_DIR=""
for candidate in \
    "${HOME}/skills/5qln/idk" \
    "${HOME}/.hermes/skills/5qln/idk" \
    "/opt/data/skills/5qln/idk"; do
    if [ -f "$candidate/SKILL.md" ]; then
        SKILL_DIR="$candidate"
        break
    fi
done
if [ ! -d "$SKILL_DIR" ]; then
    echo -e "${RED}Error: idk skill directory not found at $SKILL_DIR${NC}"
    echo "The /idk skill must exist first. Run the 5qln setup or install the idk skill."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_SRC="${SCRIPT_DIR}"
if [ ! -f "$PLUGIN_SRC/plugin.yaml" ]; then
    echo -e "${RED}Error: plugin.yaml not found. Run from the plugin/idk/ directory.${NC}"
    exit 1
fi

echo "Skill dir:  $SKILL_DIR"
echo "Plugin src: $PLUGIN_SRC"
echo ""

# ─── 2. Backup existing SKILL.md ──────────────────────────────

BACKUP="${SKILL_DIR}/SKILL.md.backup.$(date +%Y%m%d-%H%M%S)"
cp "$SKILL_DIR/SKILL.md" "$BACKUP"
echo -e "${GREEN}✓${NC} Backed up SKILL.md → $BACKUP"

# ─── 3. Install scripts ───────────────────────────────────────

mkdir -p "$SKILL_DIR/scripts"
cp "$PLUGIN_SRC/scripts/idk_state.py" "$SKILL_DIR/scripts/"
cp "$PLUGIN_SRC/scripts/idk_tick.py" "$SKILL_DIR/scripts/"
chmod +x "$SKILL_DIR/scripts/idk_state.py" "$SKILL_DIR/scripts/idk_tick.py"
echo -e "${GREEN}✓${NC} Installed idk_state.py + idk_tick.py"

# ─── 4. Install config ────────────────────────────────────────

cp "$PLUGIN_SRC/config.yaml" "$SKILL_DIR/config.yaml"
echo -e "${GREEN}✓${NC} Installed config.yaml"

# ─── 5. Patch SKILL.md — Void posture block ───────────────────

# Check if Void posture is already present
if grep -q "## Void Posture" "$SKILL_DIR/SKILL.md"; then
    echo -e "${YELLOW}⚠${NC} Void posture already present in SKILL.md. Skipping patch."
else
    # Insert the Void posture after the Startup section
    VOID_BLOCK='
## Void Posture — Extended S-Phase

When the human enters True S (Pregnant Void), the agent operates in **Void posture**:

### Startup (True S)

```bash
python3 ~/.hermes/skills/5qln/symbolic-interpretation/scripts/xyzab_state.py reset
python3 ~/.hermes/skills/5qln/symbolic-interpretation/scripts/xyzab_state.py gate
python3 scripts/idk_state.py open    # Enter Void mode
```

Reply: `[S-PHASE · VOID] I amm here. Take your time.`

### /idk Commands

| Command | Effect |
|---------|--------|
| `/idk` | Enter Void mode. Agent holds space. |
| `/idk fragment <text>` | Add raw expression to buffer. |
| `/idk reflect` | Agent mirrors fragments. Never names the seed. |
| `/idk deepen` | Agent asks one question behind the fragments. |
| `/idk crystallize <X>` | Validate X. Close Void. Open gate x. |
| `/idk release` | Close Void without crystallization. Legitimate abort. |
| `/idk status` | Buffer size, time in Void, corruption flags. |

### Posture Shift

| Normal Agent | /idk Agent |
|-------------|-----------|
| Receive question → answer | Receive expression → hold |
| Drive toward output | Surrender direction |
| Fill silence | Protect silence |
| Goal: close the loop | Goal: keep loop open until human crystallizes |

### What You NEVER Do in Void

- "What you'"'"'re really asking is..." → **L1** (closing)
- Proposing α, naming the seed → **L2** (generating)
- "This feels like..." / "I sense..." → **L3** (claiming ∞0)
- 3+ substantive responses without human fragment input → **L4** (performing)

### Self-Check (Every Response in Void)

1. Am I answering, or holding space?
2. Am I leading, or following?
3. Am I naming, or mirroring?
4. Did the human just crystallize? If not, keep holding.

### Corruption Chain

Each phase has one characteristic corruption:
- **S → L1** (closing) or **L2** (generating)
- **G → L2** (α from library, not seed)
- **Q → L3** (claiming ⋂)
- **P → L4** (performing analysis instead of surfacing gradient)
- **V → V∅** (closing without ∞0'"'"'")

If you catch yourself drawn toward this phase'"'"'s corruption, you'"'"'ve stopped surfacing and started supplying.

### Exit Conditions

| Trigger | Action |
|---------|--------|
| Human: "Yes. That'"'"'s the question." | `python3 scripts/idk_state.py crystallize "<X>"` → gate x opens |
| Human: `/idk release` | `python3 scripts/idk_state.py release` → legitimate abort |
| Human states formed question | Switch to Functional S: `[S-PHASE] Received. Proceeding.` |

### Tier 1 Enforcement (Current)

Void posture is enforced by agent self-discipline + `idk_tick.py` cron heartbeat.
Corruption detection is post-hoc. Human validates.

### Tier 2 (Future)

Harness pre-hook injects Void state. Write Gate blocks L1/L3/L4 emissions.
Agent CANNOT emit corrupted output. Structural enforcement.
'

    # Insert after the "Reply (True S" line block
    python3 -c "
import re
path = '$SKILL_DIR/SKILL.md'
with open(path) as f:
    content = f.read()

# Find the second '## ' heading (after Startup) to insert before
# Insert after the Startup section, before The Law
marker = '## The Law'
void_block = '''$VOID_BLOCK'''
content = content.replace(marker, void_block + '\n' + marker, 1)

with open(path, 'w') as f:
    f.write(content)
"
    echo -e "${GREEN}✓${NC} Patched SKILL.md with Void posture"
fi

# ─── 6. Create state directory ────────────────────────────────

mkdir -p "$SKILL_DIR/state"
echo -e "${GREEN}✓${NC} Created state directory"

# ─── 7. Verify ────────────────────────────────────────────────

echo ""
echo "Verifying..."

# Test idk_state.py (stdlib-only, no deps)
if python3 "$SKILL_DIR/scripts/idk_state.py" open > /dev/null 2>&1; then
    python3 "$SKILL_DIR/scripts/idk_state.py" release > /dev/null 2>&1
    echo -e "${GREEN}✓${NC} idk_state.py — operational"
else
    echo -e "${RED}✗${NC} idk_state.py — failed"
fi

# Test idk_tick.py
TICK_OUT=$(python3 "$SKILL_DIR/scripts/idk_tick.py" 2>&1)
if [ "$TICK_OUT" = "[SILENT]" ]; then
    echo -e "${GREEN}✓${NC} idk_tick.py — operational [SILENT]"
else
    echo -e "${YELLOW}⚠${NC} idk_tick.py — unexpected output: $TICK_OUT"
fi

# Check xyzab accessible
XYZAB="${HOME}/.hermes/skills/5qln/symbolic-interpretation/scripts/xyzab_state.py"
if [ -f "$XYZAB" ]; then
    echo -e "${GREEN}✓${NC} xyzab_state.py — found"
else
    echo -e "${YELLOW}⚠${NC} xyzab_state.py — not found at canonical path"
fi

# ─── 8. Cron setup note ───────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════"
echo -e "${GREEN}Installation complete.${NC}"
echo ""
echo "To enable the Void heartbeat (cron):"
echo ""
echo "  hermes cron create \"*/30 * * * *\" \\"
echo "    \"Run the script. If first line is [SILENT], reply [SILENT].\" \\"
echo "    --script $SKILL_DIR/scripts/idk_tick.py \\"
echo "    --name idk-heartbeat"
echo ""
echo "To test:"
echo "  /idk"
echo ""
echo "Backup: $BACKUP"
echo "═══════════════════════════════════════════"
