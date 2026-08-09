# Repository instructions

Keep role behavior in focused `SKILL.md` files and shared routing data in `config/role_power_registry.json`. Maintain exact parity between Codex and Claude Code role inventories. Role switching may specialize behavior but must never bypass permissions, credentials, authorization, confirmation, or independent certification. Use the standard library unless a dependency is demonstrably necessary. Preserve proprietary licensing. Run `pwsh -NoProfile -File .\scripts\verify.ps1` after changes and do not claim release readiness without exact-commit evidence.
