from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class McpServerTests(unittest.TestCase):
    def test_stdio_server_lists_expected_tools(self) -> None:
        async def verify() -> set[str]:
            root = Path(__file__).resolve().parents[1]
            parameters = StdioServerParameters(
                command=sys.executable,
                args=[str(root / "scripts" / "desktop_mcp.py")],
                cwd=str(root),
            )
            async with stdio_client(parameters) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
            return {tool.name for tool in tools.tools}

        names = asyncio.run(verify())
        self.assertEqual(names, {
            "desktop_api_catalog",
            "desktop_environment_status",
            "desktop_project_snapshot",
            "desktop_git_status",
            "desktop_cli_status",
            "desktop_provider_status",
            "desktop_mcp_status",
            "desktop_fleet_status",
            "desktop_feature_parity",
            "desktop_readiness_gaps",
            "desktop_shared_state",
            "desktop_runtime_status",
            "desktop_package_status",
            "desktop_read_project_file",
            "desktop_search_project",
            "desktop_run_action",
            "desktop_run_verification",
            "desktop_latest_report",
            "desktop_release_decision",
        })


if __name__ == "__main__":
    unittest.main()
