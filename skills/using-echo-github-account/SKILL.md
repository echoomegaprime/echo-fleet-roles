---
name: using-echo-github-account
description: Use when publishing, migrating, reviewing, or maintaining ECHO repositories, plugins, applications, infrastructure, or documentation under the canonical GitHub account.
---

# Using the ECHO GitHub Account

## Canonical identity

All new ECHO work targets **`echoomegaprime`**:

- Repository base: `https://github.com/echoomegaprime`
- Commit author name: `ECHO OMEGA PRIME`; commit author email: `bobbymcwilliams@echo-op.com`.
- Canonical ANVIL clone root: `/mnt/echo_ibm_1tb/ECHO_CONSOLIDATED/repos/echoomegaprime/`
- Legacy owners, including `ECHO-OMEGA-PRIME`, are read-only provenance unless the Commander explicitly authorizes a migration or marker update.

## Start gate

Run this before changing files or creating repositories:

```powershell
$ErrorActionPreference = 'Stop'
$ExpectedOwner = 'echoomegaprime'
$Login = (gh api user --jq '.login').Trim()
if ($Login -ne $ExpectedOwner) {
    throw "GitHub identity gate failed. Authenticated as '$Login'; required '$ExpectedOwner'. Do not push."
}

git status --short
git remote -v
git branch --show-current
```

Do not request, print, log, paste, or commit a PAT, password, private key, OAuth token, API key, or Vault response. Resolve credentials only through the approved Vault/SDK path.

## Repository workflow

1. Search Arcanum, Knowledge Forge, and the ECHO code library for reusable work.
2. Confirm the repository is owned by `echoomegaprime`.
3. Configure the repository-local identity:

```powershell
git config user.name 'ECHO OMEGA PRIME'
git config user.email 'bobbymcwilliams@echo-op.com'
```

4. Start from the default branch and create a branch beginning with `agent/` followed by a concise lowercase hyphenated description.
5. Preserve unrelated changes. Stage explicit paths; never use broad staging when unrelated work exists.
6. Never force-push, rewrite shared history, delete shared branches, or push directly to `main`.
7. Add or maintain `README.md`, `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `.gitignore`, and safe environment examples where applicable.
8. Keep credentials, customer data, private operational details, and restricted infrastructure information out of repositories and evidence.

## Validation and pull request

Run the applicable formatter, lint, type, unit, integration, end-to-end, secret-scan, build, container, and migration checks. Commit only the requested paths, push only the agent branch, and open a **draft** pull request.

The PR body must contain:

- `## Summary`
- `## Why`
- `## Validation` with exact commands and results
- `## Security` covering permissions, secrets, data boundaries, deployment, rollback, compatibility, and migrations
- `## Evidence` with commit SHA, test artifacts, certification receipts, and relevant logs or links

## Completion gate

Do not claim completion until the exact pushed commit has:

- Required hosted checks green
- CodeQL green
- ECHO Certification Forge passing when applicable
- ECHO Release Sentinel passing
- GitHub App Suite journey tests passing for production, security, or public-facing repositories
- Required review approval
- Reproducible evidence with no secret exposure

After approval and merge, tag releases only from the certified commit and synchronize the final clean clone to the canonical ANVIL path.

## Stop conditions

Stop without pushing when any of these is true:

- `gh api user` does not return `echoomegaprime`
- The remote points to a legacy owner
- The working tree contains unrelated changes that cannot be isolated
- Required tests or security checks fail
- A credential would have to be exposed
- The exact commit cannot be verified by hosted checks
