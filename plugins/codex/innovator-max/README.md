# Innovator Max

Innovator Max is ECHO's role-aware capability package: a reviewed skill/plugin marketplace, live doorway resolver, scoped SDK connector broker, troubleshooting role, and an evidence-gated AAA graphics workflow.

## Protocol surfaces

- MCP 2025-06-18: `python scripts/mcp_server.py --transport stdio` for local clients, or `--transport streamable-http --host 127.0.0.1 --port 8792` for remote MCP clients.
- A2A v1.0 JSON-RPC: `python scripts/provider_server.py`; discover the Agent Card at `/.well-known/agent-card.json` and send requests to `/a2a`.
- OpenAI-compatible chat: `/v1/models` and `/v1/chat/completions`, including SSE when `stream=true`.
- Provider-neutral JSON: `/v1/connector` or `python scripts/connector_gateway.py --stdio` for lightweight CLI adapters.

Network transports fail closed unless `ECHO_CONNECTOR_HTTP_TOKEN` is set. A localhost-only development override exists for disposable smoke tests. Browser origins are denied unless explicitly supplied with `--allow-origin`. All protocol surfaces call the same dispatcher, so role policy, restricted-data refusal, plan-first execution, redaction, and audit metadata cannot drift by provider.

## Install and verify

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/conformance.py
```

The plugin's `.mcp.json` launches the standards-compliant MCP server. The capability catalog imports installed skills/plugins/connectors and known upstream registries as review-required metadata; presence never grants execution permission.

## Invocation shape

Plain text sent through A2A or Chat Completions becomes a role-aware capability retrieval. Send a JSON object to select a gateway operation explicitly:

```json
{"op":"invoke","role":"builder","capability":"echo.context.recall","command":"search","options":{"query":"current Build Tracker state"},"execute":false}
```

`execute:false` is the default. Execution uses the scoped SOL broker and is still subject to the role and sensitivity policy.
