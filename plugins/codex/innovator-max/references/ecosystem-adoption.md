# Ecosystem adoption map

Research date: 2026-08-02. These are upstream references, not vendored code. Pin versions and read current upstream security/release notes before installing anything.

## Adopt directly

- [Agent Skills specification](https://github.com/agentskills/agentskills) — keep `SKILL.md` plus progressive-disclosure resources as the portable instruction format. ECHO adds role and connector metadata beside the standard format.
- [MCP reference servers](https://github.com/modelcontextprotocol/servers) and [official TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) — use MCP as an interoperability surface for tools, resources, and prompts. Keep ECHO policy and broker execution behind the MCP adapter.
- [A2A protocol](https://github.com/a2aproject/A2A) and [Python SDK](https://github.com/a2aproject/a2a-python) — use for remote opaque-agent collaboration, long-running tasks, agent cards, and structured modalities; do not use A2A for local tool calls.

## Optional adapters

- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) — adapter for agents, tools, guardrails, handoffs, and MCP; ECHO remains provider-neutral.
- [Google ADK](https://github.com/google/adk-python) — adapter for modular agent trees, evaluation, tool confirmation, and deployment; do not make Gemini a hard dependency.
- [LangGraph](https://github.com/langchain-ai/langgraph) — optional durable workflow runner for graph-shaped jobs; SOL remains the mission checkpoint authority.
- [LiteLLM](https://github.com/BerriAI/litellm) — optional model-provider router for OpenAI-compatible and non-compatible providers; isolate it behind a provider adapter and pin/audit versions before deployment.
- [GitHub CLI agent skills](https://cli.github.com/manual/gh_skill_install) — use as a discovery/import source for compatible skills across Codex, Claude Code, Copilot, Cursor, Gemini CLI, Goose, OpenCode, and others; review every imported skill before enabling it.

## Deliberate non-goals

- Do not clone whole orchestration frameworks into the plugin.
- Do not let a model provider own role policy, secrets, mission state, or verification.
- Do not expose raw ECHO SDK credentials to clients; the scoped broker remains the trust boundary.
- Do not install third-party packages solely because a connector exists; ground, pin, scan, and smoke-test first.

## Target architecture

`Agent Skill / Chat / CLI / MCP / A2A client → JSONL or JSON-RPC adapter → role-aware resolver → scoped SOL broker → verifier → evidence + memory`.
