---
name: doorway-integration
description: Use at the start of every ECHO task to resolve the scoped AGENTS.md and CLAUDE.md instructional doorway, apply project overlays and module routing, and preserve context economy and redaction rules.
---

# Doorway Integration

The instructional doorway is the control plane for every role. Keep it T1-small: doctrine, hard limits, retrieval bootstrap, and enrichment rules. Load instructions before retrieving capabilities or editing files, but load only the modules relevant to the current path; fetch deep knowledge on demand from live sources.

## Required Order

1. Current user instruction.
2. Project overlay, when present.
3. Nearest applicable `AGENTS.md` and `CLAUDE.md`.
4. Root ECHO router and always-load security/execution modules.
5. Domain modules selected by `config/scopes.yaml`.
6. Dependency instructions only when editing that dependency.

Use `scripts/doorway_loader.py --start <path>` to produce a redacted manifest of the applicable files, hashes, and load order. Read the returned files through the normal filesystem tool; the manifest intentionally avoids dumping the instructional bible into logs or SDK responses.

## Enforcement

- Treat `AGENTS.md` as the vendor-neutral doorway and `CLAUDE.md` as the deeper doctrine when both exist.
- Do not load unrelated worktree instructions, archived doctrine, or entire source instruction libraries.
- Resolve instruction conflicts according to the repository's conflict-resolution module and current user instruction.
- Never copy secrets, credentials, taxpayer data, client records, or private identity data into connector requests or reports.
- Include the doorway manifest in internal evidence as paths/hashes only.
- Verify the retrieval instrument before believing its result: health, freshness, schema, and real boundary behavior.

## Connector Contract

Every role profile includes this skill globally. The provider-neutral gateway exposes a `doorway` operation alongside `health`, `roles`, `list`, `retrieve`, and `invoke`, so CLIs, chats, MCP clients, and A2A clients can resolve the same instruction boundary before acting.
