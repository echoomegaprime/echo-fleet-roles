# Deployment

This repository deploys as local host plugins and a Python CLI; it does not expose a network service.

1. Clone the exact release tag.
2. Verify release SHA-256 hashes and both exact-commit certificates.
3. Run `pwsh -NoProfile -File .\scripts\verify.ps1`.
4. Run `pwsh -NoProfile -File .\scripts\install-local.ps1 -InstallRuntime`.
5. Review and trust the plugin hooks.
6. Restart the host once for initial discovery, then run the same-session smoke.

Rollback removes the marketplace source, disables the plugin, and reinstalls the prior signed tag. Role state is backward-compatible SQLite metadata and may be retained; it contains no credentials.
