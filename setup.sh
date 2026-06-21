#!/usr/bin/env bash
#
# /idk — setup.
#
# Run from the repo directory after cloning:
#   git clone https://github.com/5qln/idk.git
#   cd idk && bash setup.sh
#
# What this does:
#   1. Verifies the sealed Codex is byte-identical (refuses to proceed if not).
#   2. Installs the one skill into the Hermes skills directory.
#   3. Tells you how to start.
#
# Optional:
#   HERMES_SKILLS   Where the skill goes (default: ~/.hermes/skills)
#
# There are no engines, no daemons, no cron jobs. /idk runs only when a human
# is present and types it. The human at the membrane is the whole runtime.

set -e

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
HERMES_SKILLS="${HERMES_SKILLS:-${HOME}/.hermes/skills}"
CANONICAL_HASH="feaa46b4147d4e023cdd3fd59c051d063e8ec654ee7b38a481dcd5e4c781859b"

echo -e "${BOLD}/idk — setup${NC}"
echo ""

# ── 1. Verify the seal ────────────────────────────────────────────────
echo -e "${BOLD}1. Verifying the Codex seal${NC}"

if [ ! -f "${REPO_DIR}/codex.md" ]; then
    echo -e "   ${RED}✗${NC} codex.md not found — the checkout looks incomplete. Re-clone."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo -e "   ${YELLOW}⚠${NC} python3 not found. The seal check needs Python 3.8+."
    echo -e "     This is an environment problem, not a tamper signal. Install Python 3 and re-run."
    exit 2
fi

set +e
python3 "${REPO_DIR}/bin/lint.py" --seal
SEAL_RC=$?
set -e
if [ "${SEAL_RC}" -ne 0 ]; then
    echo -e "   ${RED}✗ The Codex seal did not verify.${NC}"
    echo -e "     The 217-byte Codex is sealed and must hash to:"
    echo -e "     ${CANONICAL_HASH}"
    echo -e "     Restore codex.md; never re-seal around a change. Report: security@5qln.com"
    exit 1
fi
echo -e "   ${GREEN}✓${NC} sealed Codex is byte-identical"
echo ""

# ── 2. Install the skill ──────────────────────────────────────────────
echo -e "${BOLD}2. Installing the skill${NC}"

if [ ! -d "${REPO_DIR}/skills/idk" ]; then
    echo -e "   ${RED}✗${NC} skills/idk not found — the checkout looks incomplete. Re-clone."
    exit 1
fi

mkdir -p "${HERMES_SKILLS}"
rm -rf "${HERMES_SKILLS}/idk"
cp -r "${REPO_DIR}/skills/idk" "${HERMES_SKILLS}/idk"
# Place the sealed Codex beside the skill, so the form-linter can find it.
cp "${REPO_DIR}/codex.md" "${HERMES_SKILLS}/idk/codex.md"
echo -e "   ${GREEN}✓${NC} idk → ${HERMES_SKILLS}/idk"
echo ""

# ── 3. Done ───────────────────────────────────────────────────────────
echo -e "${GREEN}${BOLD}Ready.${NC}"
echo ""
echo -e " In chat with your Hermes agent:"
echo ""
echo -e "   ${BOLD}/reset${NC}"
echo -e "   ${BOLD}Load the idk skill.${NC}"
echo -e "   ${BOLD}/idk${NC}"
echo ""
echo -e " Then don't reach for a question. Let one come."
echo ""
echo -e " Verify the seal independently anytime:"
echo -e "   python3 ${REPO_DIR}/bin/lint.py --seal"
echo -e " The hash must match the one published at https://www.5qln.com/codex/"
echo ""
