from __future__ import annotations

import asyncio
import json
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from provider_server import create_app  # noqa: E402


class ProviderProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app("unit-token", "http://testserver", {"https://allowed.example"}, 1000))
        self.auth = {"Authorization": "Bearer unit-token"}

    def test_auth_origin_and_openai_chat_contract(self) -> None:
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/v1/models").status_code, 401)
        denied = self.client.get("/v1/models", headers={**self.auth, "Origin": "https://denied.example"})
        self.assertEqual(denied.status_code, 403)
        models = self.client.get("/v1/models", headers={**self.auth, "Origin": "https://allowed.example"})
        self.assertEqual(models.status_code, 200)
        completion = self.client.post(
            "/v1/chat/completions",
            headers=self.auth,
            json={"model": "echo-capability-gateway", "messages": [{"role": "user", "content": "find graphics tools"}]},
        )
        self.assertEqual(completion.status_code, 200)
        payload = completion.json()
        self.assertEqual(payload["object"], "chat.completion")
        routed = json.loads(payload["choices"][0]["message"]["content"])
        self.assertTrue(routed["ok"])
        self.assertGreaterEqual(len(routed["matches"]), 1)

    def test_a2a_v1_agent_card_and_send_message(self) -> None:
        card = self.client.get("/.well-known/agent-card.json")
        self.assertEqual(card.status_code, 200)
        self.assertEqual(card.json()["supportedInterfaces"][0]["protocolVersion"], "1.0")
        request = {
            "jsonrpc": "2.0",
            "id": "a2a-test",
            "method": "SendMessage",
            "params": {
                "message": {
                    "messageId": "message-test",
                    "role": "ROLE_USER",
                    "parts": [{"text": '{"op":"health"}'}],
                }
            },
        }
        response = self.client.post("/a2a", headers={**self.auth, "A2A-Version": "1.0"}, json=request)
        self.assertEqual(response.status_code, 200, response.text)
        envelope = response.json()
        self.assertEqual(envelope["jsonrpc"], "2.0")
        self.assertIn("message", envelope["result"])
        result_text = envelope["result"]["message"]["parts"][0]["text"]
        self.assertTrue(json.loads(result_text)["ok"])


class McpProtocolTests(unittest.TestCase):
    def test_stdio_initialize_list_and_call(self) -> None:
        async def exercise() -> None:
            params = StdioServerParameters(
                command=sys.executable,
                args=[str(SCRIPTS / "mcp_server.py"), "--transport", "stdio"],
                cwd=str(PLUGIN_ROOT),
            )
            async with stdio_client(params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    initialized = await session.initialize()
                    self.assertEqual(initialized.serverInfo.name, "innovator_max_mcp")
                    listing = await session.list_tools()
                    names = {tool.name for tool in listing.tools}
                    self.assertIn("echo_gateway_health", names)
                    self.assertIn("echo_invoke_capability", names)
                    result = await session.call_tool("echo_gateway_health", {})
                    self.assertFalse(result.isError)
                    self.assertTrue(result.structuredContent["ok"])

        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
