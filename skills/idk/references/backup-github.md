# Backup to GitHub

The `/idk` skill and its session-chain tools live across two GitHub identities:

| Identity | Role | Auth |
|----------|------|------|
| `5qln` (org) | **Source of truth** — `5qln/Idk`, `5qln/Questions`, `5qln/Idk-commons` | Separate SSH key (`~/.ssh/id_ed25519_5qln`, Host `github.com-5qln`) |
| `qlnlife` (personal) | **Backup mirror** — `qlnlife/Idk`, `qlnlife/Hermes5BU` | Default SSH key (`~/.ssh/id_ed25519`) |

## What goes where

- **5qln/Idk:** Code and tooling — `xyzab_state.py`, `decoding.py`, `SKILL.md`, `codex.md`, Void posture engine, linter, install/setup scripts, reference docs.
- **qlnlife/Hermes5BU/articles/:** Article drafts and published writings from 5qln.com — the human's creative output.
- **qlnlife/Idk:** Mirror of 5qln/Idk (kept in sync).

## Repo structure (5qln/Idk)

```
Idk/
├── README.md, USER-GUIDE.md, TROUBLESHOOTING.md, ARCHITECTURE.md
├── LICENSE, .gitignore, .github/workflows/seal.yml
├── codex.md
├── config.yaml
├── void-posture.md
├── install.sh, setup.sh
├── bin/lint.py
├── scripts/
│   ├── xyzab_state.py      # gate machine + auto-archive on reset
│   ├── decoding.py          # canonical phase decoder
│   ├── idk_state.py         # Void posture state machine
│   └── idk_tick.py          # Void posture tick engine
└── skills/idk/
    ├── SKILL.md
    └── references/
        ├── decoding.md
        ├── decoding-setup.md
        ├── structural-article-analysis.md
        └── backup-github.md
```

## Push workflow (SSH keys)

Two separate identities — each has its own SSH key. SSH config at `~/.ssh/config`:

```
# Default: qlnlife
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519

# 5qln org
Host github.com-5qln
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_5qln
    IdentitiesOnly yes
```

**Push to 5qln/Idk (code):**
```bash
cd /path/to/idk-repo
git remote add 5qln git@github.com-5qln:5qln/Idk.git
git push 5qln main
```

**Push to qlnlife mirror:**
```bash
git push origin main   # default remote = qlnlife
```

**Push articles to backup:**
```bash
cd /path/to/hermes5bu-backup
cp /path/to/article.md articles/
git add articles/
git commit -m "Add article: <title>"
git push
```

## Pitfall: mixing SSH identities with wrong repos

The 5qln SSH key (`github.com-5qln` host alias) has NO access to qlnlife repos. Using
`git@github.com-5qln:qlnlife/REPO.git` will fail with "Permission denied." 

The qlnlife key (default `github.com` host) has NO access to 5qln org repos. Using
`git@github.com:5qln/REPO.git` will fail with "Permission denied."

**Rule:** Match the host alias to the account:
- `github.com` → qlnlife (articles, Hermes5BU)
- `github.com-5qln` → 5qln (code, Idk, Questions, Idk-commons)

**Before pushing, verify the remote URL matches the right host alias.**
If the remote is `git@github.com:qlnlife/...` but you're using the 5qln key, the
push silently fails as `5qln` not `qlnlife`. Use `git remote -v` to check.

## No PATs needed

SSH key-based auth is used for both accounts. No tokens, no credential helpers, no expiry.
Test with: `ssh -T git@github.com` (qlnlife) or `ssh -T git@github.com-5qln` (5qln).

## Branch protection (5qln/Idk)

## Branch protection (5qln/Idk)

The main branch on `5qln/Idk` is protected:
- **Pull request required** before merging
- **1 approving review required** (the human)
- **Stale reviews dismissed** — new commits invalidate old approvals
- **Force pushes:** blocked
- **Branch deletion:** blocked

To configure (requires fine-grained PAT with Admin + Contents + Pull Requests on `5qln/Idk`):
```bash
curl -X PUT https://api.github.com/repos/5qln/Idk/branches/main/protection \
  -H "Authorization: token <PAT>" \
  -H "Accept: application/vnd.github+json" \
  -d '{
    "required_pull_request_reviews": {
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": false,
      "required_approving_review_count": 1
    },
    "enforce_admins": false,
    "allow_force_pushes": false,
    "allow_deletions": false
  }'
```

The agent makes PRs; the human reviews and merges. No one pushes directly to main.
