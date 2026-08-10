# Validation report

Evidence is recorded as PASS, FAIL, BLOCKED BY EXTERNAL DEPENDENCY, or NOT APPLICABLE. A skipped check is
never counted as passed.

## Current evidence

| Level | Check | Status | Evidence |
|---|---|---|---|
| Static | Python syntax and focused tool/OAuth/package/security contracts | PASS | `verify-plugin.ps1`; 67 tests passed twice; official plugin validator passed |
| Static | Package contract red phase | PASS | 8 expected failures proved missing package artifacts before implementation |
| Build | JavaScript/UI build | NOT APPLICABLE | Existing Python tool-only runtime; no UI and no new JavaScript dependency |
| Focused suite | Search/OAuth/tool/package/script security regressions | PASS | `python -m pytest GROK_BRIDGE/tests/test_search_contract.py GROK_BRIDGE/tests/test_chatgpt_echo_prime_ops_plugin.py GROK_BRIDGE/tests/test_echo_prime_ops_package.py GROK_BRIDGE/tests/test_echo_prime_ops_script_security.py -q`; 168 passed |
| Full suite | Connector regression suite | PASS | `python -m pytest GROK_BRIDGE/tests -q`; 212 passed, 1 skipped |
| Protocol | Public OAuth discovery, DCR, PKCE, refresh-family replay, MCP and safe tools | PASS | Public HTTPS smoke; 53/53 checks passed |
| Security | Formal Codex Security scan | PASS | Scan `3f69d5b8-96ad-4f01-993b-b48b47c9cf60` sealed; 0 critical/high and 3 medium follow-ups |
| Host | Real ChatGPT connection and invocation | PASS | Connected Aug 9, 2026; OAuth token exchange 200; Scan Tools completed; all five actions invoked in a fresh chat |
| Codex | Local marketplace installation | PASS | `echo-prime-ops@echo-omega-prime` 1.0.0 reports installed and enabled; stale 0.1 personal duplicate removed |
| Package | Deterministic archive and hashes | PASS | `artifacts/plugins/echo-prime-ops-1.0.0.zip` plus generated `.sha256` sidecar and per-file metadata |
| Public submission | Portal submission | BLOCKED BY EXTERNAL DEPENDENCY | Private/workspace release; verified organization and public policy URLs absent |

## Required final ladder

The release run records JSON/YAML/path/schema checks, Python compilation, focused and full tests, package
generation, OAuth discovery, DCR, PKCE, refresh rotation/replay rejection, initialize, tools/list, all five
safe calls, negative authorization/resource tests, staging and public MCP proof, and ChatGPT host evidence.
Public directory review is intentionally outside this private/workspace release.
