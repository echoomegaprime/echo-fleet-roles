# Echo Desktop Ops

Codex plugin and local MCP server providing a detailed, production-safe operations API for `C:\Users\bobmc\echo-desktop`.

## Coverage

- Repository, version, source inventory, Git state, branches, and recent commits
- Safe project-file reads and bounded source search
- Codex, Claude Code, Gemini, Qwen, GitHub Copilot CLI, and GitHub CLI status
- Shared multi-CLI ledger, handoffs, and generated Fleet state
- Fleet Control missions, role providers, progress, incidents, and readiness
- Echo Desktop provider and MCP configuration metadata without credential values
- Local Echo Desktop, bridge, broker, MCP, and role process status
- Dependency audit, TypeScript, Fleet tests, production build, Python compile, and AI Council self-test
- Windows package artifacts, SHA-256 hashes, final installer presence, evidence reports, and release gating

## MCP API

| Tool | Purpose |
|---|---|
| `desktop_api_catalog` | Describe API domains and safety controls |
| `desktop_environment_status` | Repository, version, Git, executables, report store |
| `desktop_project_snapshot` | Detailed source/build/package snapshot |
| `desktop_git_status` | Branch, commit, dirty state, history |
| `desktop_cli_status` | All supported coding CLIs and broker availability |
| `desktop_provider_status` | Provider metadata and bridge health |
| `desktop_mcp_status` | Sanitized MCP server configuration |
| `desktop_fleet_status` | Missions, roles, providers, progress, readiness |
| `desktop_feature_parity` | Completed and unresolved Claude Desktop parity rows |
| `desktop_readiness_gaps` | Consolidated parity, placeholder, document, signing, and Fleet blockers |
| `desktop_shared_state` | Provider-neutral state and append-only activity |
| `desktop_runtime_status` | Relevant local processes with redacted command lines |
| `desktop_package_status` | Installer/package files, hashes, unpacked executables |
| `desktop_read_project_file` | Read one repository-bound non-secret text file |
| `desktop_search_project` | Bounded redacted source search |
| `desktop_run_action` | Allowlisted typecheck/test/build/audit/package action |
| `desktop_run_verification` | Persisted inspect/quick/full/package/release report |
| `desktop_latest_report` | Latest redacted evidence report |
| `desktop_release_decision` | Deterministic promote/block gate |

## Safety model

- No arbitrary shell tool is exposed.
- Build actions are selected from a fixed allowlist.
- File reads are repository-bound and block traversal, dependencies, build output, and secret-bearing filenames.
- MCP/provider configuration returns names, transports, models, and environment-key names—not values.
- Logs and reports redact tokens, authorization headers, API keys, passwords, private keys, and usernames in profile paths.
- Release promotion requires a `package` or `release` report with every mandatory check passing.

## Setup and tests

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/desktop_mcp.py
```

Reports are stored under:

```text
%USERPROFILE%\.echo\echo-desktop-ops\reports
```

## Recommended workflow

1. `desktop_project_snapshot`
2. `desktop_cli_status`, `desktop_fleet_status`, and `desktop_runtime_status`
3. `desktop_run_verification(profile="full")` during development
4. `desktop_run_verification(profile="release")` for final certification
5. `desktop_release_decision`

A progress percentage, successful source build, or intermediate NSIS archive is not sufficient for promotion.
