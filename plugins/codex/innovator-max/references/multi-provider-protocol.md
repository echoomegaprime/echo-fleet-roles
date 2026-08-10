# Multi-provider connector protocol

All clients use the same four operations over JSONL, HTTP JSON, MCP, or a chat-completions adapter:

```json
{"id":"1","op":"health"}
{"id":"2","op":"retrieve","role":"innovator","intent":"find current queue and reusable code"}
{"id":"3","op":"invoke","capability":"echo.context.recall","command":"search","options":{"query":"..."},"execute":false}
```

`invoke` defaults to a plan. A client must explicitly set `execute:true` for an actual broker call. This prevents chat models and accidental retries from mutating systems. Every client should preserve `id`, show selected connector and score, and request verification after writes.

## Provider adapters

- **sol-sdk**: the canonical ECHO path; calls the scoped SOL broker and keeps auth in its environment.
- **cli-jsonl**: any CLI can pipe one request per line and consume one response per line.
- **http-json**: wrap the JSONL dispatcher behind an authenticated service without changing request semantics.
- **openai-compatible**: map a tool call/function call to `retrieve` or `invoke`; return structured JSON, never prose-only status.
- **mcp-client**: expose the four operations as MCP tools while keeping the same schemas.

Providers are transport adapters, not separate business logic. Role policy, sensitivity checks, connector ranking, redaction, and evidence requirements stay in the shared runtime.

## Extension contract

New providers must implement `health`, `retrieve`, and `invoke`, preserve request IDs, reject unknown capabilities, default writes to plan mode, and pass redaction tests. New connectors must include an acceptance probe and explicit sensitivity/role metadata.
