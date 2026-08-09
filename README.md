# ECHO Fleet Roles

ECHO Fleet Roles is the standalone, host-neutral role system for Codex and Claude Code. It packages 30 focused operating roles, including reverse engineering and authorized full-spectrum security testing, plus an audited SQLite runtime that changes roles inside one active terminal.

The role system changes specialization and workflow. It never expands the permissions, credentials, tools, or legal authorization supplied by the host.

## What ships

- `plugins/codex/echo-fleet-role-powerpack`: a current Codex plugin with 30 role skills, a role-switching control skill, and fail-open lifecycle hooks.
- `plugins/claude-code/echo-fleet-roles`: the matching Claude Code plugin.
- `echo-role`: a dependency-free Python CLI with atomic transitions, history, idempotency, and concurrent-change fencing.
- Repo-scoped marketplaces for both hosts.
- Contract, security, packaging, and same-session switch tests.

The 30 roles cover command, architecture, innovation, observation, building, publishing, enhancement, research, training, sentinel operations, curation, asset stewardship, beta testing, marketing, OSINT, troubleshooting, land work, clean-room reverse engineering, authorized pentesting, independent judging, release control, product, experience, data, and compliance.

## Install and verify on Windows

```powershell
Set-Location C:\path\to\echo-fleet-roles
pwsh -NoProfile -File .\scripts\verify.ps1
pwsh -NoProfile -File .\scripts\install-local.ps1 -InstallRuntime
```

Review the bundled hook definitions before trusting them. Restart Codex once after initial installation so it discovers the plugin and prompts for hook trust. Role changes after that are immediate:

```powershell
echo-role --json current
echo-role --json list
echo-role --json switch builder --expected-current commander --idempotency-key build-phase-1 --reason "implementation"
echo-role --json switch judge --expected-current builder --idempotency-key verify-phase-1 --reason "independent verification"
```

No additional terminal is required. The hook injects the selected role at session start and each submitted prompt.

## Security model

Role declarations are routing metadata, not authorization grants. The runtime stores only role names, transition metadata, and timestamps; it stores no credentials. Security-sensitive roles require machine-readable scope and use only tools already exposed by the host. See [SECURITY_MODEL.md](docs/SECURITY_MODEL.md).

## Verification

The local acceptance command is:

```powershell
pwsh -NoProfile -File .\scripts\verify.ps1
```

Release certification is exact-commit based. CI, end-to-end results, Cert Forge attestation, GitHub App Suite conformance, release hashes, and the canonical ANVIL clone are recorded in [VERIFICATION.md](docs/VERIFICATION.md) only after the corresponding live gate passes.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Operations](docs/OPERATIONS.md)
- [Security model](docs/SECURITY_MODEL.md)
- [Source of truth](docs/SOURCE_OF_TRUTH.md)
- [Verification](docs/VERIFICATION.md)

## License

Source-available proprietary software. See [LICENSE](LICENSE).
