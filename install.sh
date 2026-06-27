#!/usr/bin/env bash
# install.sh — /idk Void Posture Engine Installer
# One command. Pip installs Void posture into the existing idk skill.
#
# Run from the Idk repo root:
#   git clone https://github.com/5qln/Idk.git && cd Idk && bash install.sh
#
# Prerequisite: setup.sh must have been run first.

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo ""
echo -e "${GREEN}═══ /idk Void Posture Installer ═══${NC}"
echo ""

# ─── 1. Detect skill directory ─────────────────────────────────

SKILL_DIR=""
for candidate in \
    "${HOME}/skills/idk" \
    "${HOME}/.hermes/skills/idk" \
    "/opt/data/skills/idk" \
    "${HERMES_HOME}/skills/idk" \
    "${HERMES_SKILLS}/idk"; do
    if [ -f "$candidate/SKILL.md" ]; then
        SKILL_DIR="$candidate"
        break
    fi
done
if [ ! -d "$SKILL_DIR" ]; then
    echo -e "${RED}Error: idk skill directory not found.${NC}"
    echo "Run setup.sh first: git clone https://github.com/5qln/Idk.git && cd Idk && bash setup.sh"
    exit 1
fi

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -f "$REPO_DIR/scripts/idk_state.py" ]; then
    echo -e "${RED}Error: scripts/idk_state.py not found. Run from the Idk repo root.${NC}"
    exit 1
fi

echo "Skill dir: $SKILL_DIR"
echo "Repo dir:  $REPO_DIR"
echo ""

# ─── 2. Backup ─────────────────────────────────────────────────

BACKUP="${SKILL_DIR}/SKILL.md.backup.$(date +%Y%m%d-%H%M%S)"
cp "$SKILL_DIR/SKILL.md" "$BACKUP"
echo -e "${GREEN}✓${NC} Backed up → $BACKUP"

# ─── 3. Install scripts ────────────────────────────────────────

mkdir -p "$SKILL_DIR/scripts"
cp "$REPO_DIR/scripts/idk_state.py" "$SKILL_DIR/scripts/"
cp "$REPO_DIR/scripts/idk_tick.py" "$SKILL_DIR/scripts/"
chmod +x "$SKILL_DIR/scripts/idk_state.py" "$SKILL_DIR/scripts/idk_tick.py"
echo -e "${GREEN}✓${NC} Installed idk_state.py + idk_tick.py"

# ─── 4. Install config ─────────────────────────────────────────

if [ -f "$REPO_DIR/config.yaml" ]; then
    cp "$REPO_DIR/config.yaml" "$SKILL_DIR/config.yaml"
    echo -e "${GREEN}✓${NC} Installed config.yaml"
else
    echo -e "${YELLOW}⚠${NC} No config.yaml in repo — using defaults"
fi

# ─── 5. Patch SKILL.md — replace old Startup with Void posture ─

VOID_MD="$REPO_DIR/void-posture.md"
if [ ! -f "$VOID_MD" ]; then
    echo -e "${RED}Error: void-posture.md not found in repo.${NC}"
    exit 1
fi

if grep -q "## Void Posture" "$SKILL_DIR/SKILL.md"; then
    echo -e "${YELLOW}⚠${NC} Void posture already present. Skipping patch."
else
    python3 -c "
path = '$SKILL_DIR/SKILL.md'
with open(path) as f:
    content = f.read()

with open('$VOID_MD') as f:
    void_block = f.read()

old_start = content.find('## Startup')
old_law   = content.find('## The Law')

if old_start == -1 or old_law == -1:
    print('ERROR: markers not found')
    exit(1)

new_content = content[:old_start] + void_block + '\n' + content[old_law:]
with open(path, 'w') as f:
    f.write(new_content)
print('OK')
"
    echo -e "${GREEN}✓${NC} Patched SKILL.md — Void posture is now the startup"
fi

# ─── 6. Create state directory ─────────────────────────────────

mkdir -p "$SKILL_DIR/state"
echo -e "${GREEN}✓${NC} Created state directory"

# ─── 7. Verify ─────────────────────────────────────────────────

echo ""
echo "Verifying..."

if python3 "$SKILL_DIR/scripts/idk_state.py" open > /dev/null 2>&1; then
    python3 "$SKILL_DIR/scripts/idk_state.py" release > /dev/null 2>&1
    echo -e "${GREEN}✓${NC} idk_state.py — operational"
else
    echo -e "${RED}✗${NC} idk_state.py — failed"
fi

TICK_OUT=$(python3 "$SKILL_DIR/scripts/idk_tick.py" 2>&1 || true)
if [ "$TICK_OUT" = "[SILENT]" ]; then
    echo -e "${GREEN}✓${NC} idk_tick.py — operational [SILENT]"
else
    echo -e "${YELLOW}⚠${NC} idk_tick.py: $TICK_OUT"
fi

# ─── 8. Done ───────────────────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════"
echo -e "${GREEN}Installation complete.${NC}"
echo ""
echo "Test: /idk"
echo "Backup: $BACKUP"
echo "═══════════════════════════════════════════"
