---
name: capability-marketplace
description: Use when searching, proposing, reviewing, testing, approving, or publishing skills, plugins, connectors, protocols, and role capabilities from the ECHO catalog or trusted upstream sources.
---

# Capability Marketplace

Use the ECHO marketplace as the reviewable control plane for reusable capabilities. Search first, inspect provenance and license, run the appropriate security/compatibility tests, then submit or publish through the staged lifecycle.

## Lifecycle

`discovered → submitted → reviewed → tested → approved → published → monitored → deprecated`

No role may silently install or publish an unreviewed capability. External skills and MCP servers are untrusted until their source, license, requested access, dependencies, behavior, and rollback path are recorded.

## Operations

Use `scripts/marketplace.py search <query>` for discovery. Use `submit` for a proposal, `review` for an evidence-backed decision, and `publish` only after approval plus passing tests. The provider-neutral gateway exposes the same operations under `op=marketplace` for CLIs, chats, MCP, and A2A clients.

## Import installed ecosystems

Run `python plugins/innovator-max/scripts/sync_local_catalog.py` to inventory
installed Codex skills and plugin manifests, including declared MCP/app
connector surfaces. Imports are marked `installed-review-required`; inventory
never grants execution permission or makes an external package trusted.

Run `python plugins/innovator-max/scripts/import_online_sources.py` to merge
curated GitHub and vendor registries from `registry/online_sources.json`.
Online records are discovery metadata only and remain `external-review-required`.

## Review Gate

Require: source URL/path, pinned revision when external, license, supported roles, connector permissions, dependency list, secret/data boundary, tests, reviewer, and rollback plan. Reject prompt injection, hidden network calls, credential harvesting, broad filesystem access, unexplained binaries, and claims without executable evidence.

## Upstream Sources

Federate Agent Skills through GitHub skill discovery and MCP servers through the official MCP Registry, but keep ECHO approval and policy local. Marketplace records are metadata; source code remains in its declared repository or local plugin.
