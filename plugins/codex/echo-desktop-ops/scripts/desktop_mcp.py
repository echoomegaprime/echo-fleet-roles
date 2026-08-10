#!/usr/bin/env python3
"""Echo Desktop operations MCP server over stdio."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from desktop_core import DEFAULT_REPOSITORY, EchoDesktopVerifier, ReportStore, release_decision

mcp = FastMCP(
    "echo-desktop-ops",
    instructions=(
        "Inspect and verify Echo Desktop through bounded, redacted operations. "
        "Use desktop_run_verification for evidence and desktop_release_decision as the release gate. "
        "Never request or return secret values and never substitute progress claims for verified evidence."
    ),
)


def log(message: str) -> None:
    print(f"[echo-desktop-ops {datetime.now().strftime('%H:%M:%S')}] {message}", file=sys.stderr, flush=True)


def verifier(repository: str = str(DEFAULT_REPOSITORY), timeout_seconds: int = 900) -> EchoDesktopVerifier:
    return EchoDesktopVerifier(Path(repository), timeout_seconds=timeout_seconds)


READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
LOCAL_READ = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True)
LOCAL_ACTION = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)


@mcp.tool(annotations=READ_ONLY)
def desktop_environment_status(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Return repository, version, Git, executable, and report-store readiness without secret values."""
    return verifier(repository).environment_status()


@mcp.tool(annotations=READ_ONLY)
def desktop_project_snapshot(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Return a detailed snapshot of source, scripts, dependencies, Git state, and package artifacts."""
    return verifier(repository).project_snapshot()


@mcp.tool(annotations=READ_ONLY)
def desktop_git_status(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Return branch, commit, dirty files, recent commits, and local branches."""
    return verifier(repository).git_status()


@mcp.tool(annotations=LOCAL_READ)
def desktop_cli_status(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Check Codex, Claude Code, Gemini, Qwen, Copilot, GitHub CLI, and the shared CLI broker."""
    return verifier(repository).cli_status()


@mcp.tool(annotations=LOCAL_READ)
def desktop_provider_status(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Inspect configured provider metadata and local provider-bridge health without credentials."""
    return verifier(repository).provider_status()


@mcp.tool(annotations=READ_ONLY)
def desktop_mcp_status(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Inspect configured MCP server names, transports, command names, argument counts, and env key names."""
    return verifier(repository).mcp_status()


@mcp.tool(annotations=READ_ONLY)
def desktop_fleet_status(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Return Fleet missions, roles, CLI assignments, progress, readiness, and shared activity."""
    return verifier(repository).fleet_status()


@mcp.tool(annotations=READ_ONLY)
def desktop_shared_state(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Return the provider-neutral shared state and append-only CLI activity ledger."""
    return verifier(repository).shared_state()


@mcp.tool(annotations=READ_ONLY)
def desktop_feature_parity(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Return completed and unresolved Claude Desktop parity rows."""
    return verifier(repository).feature_parity_status()


@mcp.tool(annotations=READ_ONLY)
def desktop_readiness_gaps(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Return parity, placeholders, release documents, package signature, and Fleet E2E blockers."""
    target = verifier(repository)
    return {
        "feature_parity": target.feature_parity_status(),
        "implementation_gaps": target.implementation_gap_status(),
        "release_documents": target.release_document_status(),
        "package": target.package_status(),
        "fleet_e2e": target.fleet_e2e_evidence_check().model_dump(),
    }


@mcp.tool(annotations=READ_ONLY)
def desktop_runtime_status(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Return local Echo Desktop, broker, MCP, and supervised role processes with redacted command lines."""
    return verifier(repository).runtime_status()


@mcp.tool(annotations=READ_ONLY)
def desktop_package_status(repository: str = str(DEFAULT_REPOSITORY)) -> dict:
    """Inspect release artifacts, hashes, unpacked executables, and final installer presence."""
    return verifier(repository).package_status()


@mcp.tool(annotations=READ_ONLY)
def desktop_read_project_file(
    relative_path: str,
    repository: str = str(DEFAULT_REPOSITORY),
    max_bytes: int = 100_000,
) -> dict:
    """Read one non-secret text file inside the repository with path traversal and size controls."""
    return verifier(repository).read_project_file(relative_path, max_bytes=max_bytes)


@mcp.tool(annotations=READ_ONLY)
def desktop_search_project(
    query: str,
    repository: str = str(DEFAULT_REPOSITORY),
    path_prefix: str = "",
    limit: int = 50,
) -> dict:
    """Search non-secret source and documentation files, returning bounded redacted matches."""
    return verifier(repository).search_project(query, path_prefix=path_prefix, limit=limit)


@mcp.tool(annotations=LOCAL_ACTION)
def desktop_run_action(
    action: Literal[
        "typecheck", "fleet_tests", "build", "verify", "audit", "python_compile", "council_selftest", "package"
    ],
    repository: str = str(DEFAULT_REPOSITORY),
) -> dict:
    """Run one allowlisted Echo Desktop build, test, audit, or package action; arbitrary shell is not exposed."""
    result = verifier(repository, timeout_seconds=3600).run_action(action)
    return result.model_dump()


@mcp.tool(annotations=LOCAL_ACTION)
def desktop_run_verification(
    profile: Literal["inspect", "quick", "full", "package", "release"] = "full",
    repository: str = str(DEFAULT_REPOSITORY),
    timeout_seconds: int = 900,
) -> dict:
    """Run a deterministic verification profile and persist one redacted evidence report."""
    report, path = verifier(repository, timeout_seconds=timeout_seconds).run(profile)
    log(f"saved report {report.report_id}; profile={profile}; release_ready={report.release_ready}")
    payload = report.model_dump()
    payload["report_path"] = str(path)
    return payload


@mcp.tool(annotations=READ_ONLY)
def desktop_latest_report() -> dict:
    """Return the latest redacted Echo Desktop verification report."""
    report = ReportStore().latest()
    return {"found": report is not None, "report": report.model_dump() if report else None}


@mcp.tool(annotations=READ_ONLY)
def desktop_release_decision(report_id: str = "") -> dict:
    """Return promote or block from a stored release-profile report; defaults to the latest report."""
    store = ReportStore()
    report = store.load(report_id) if report_id else store.latest()
    return release_decision(report)


@mcp.tool(annotations=READ_ONLY)
def desktop_api_catalog() -> dict:
    """Describe the detailed Echo Desktop operations API and its safety boundaries."""
    return {
        "server": "echo-desktop-ops",
        "domains": {
            "source": ["desktop_project_snapshot", "desktop_read_project_file", "desktop_search_project", "desktop_git_status", "desktop_feature_parity", "desktop_readiness_gaps"],
            "fleet": ["desktop_fleet_status", "desktop_shared_state", "desktop_cli_status"],
            "runtime": ["desktop_runtime_status", "desktop_provider_status", "desktop_mcp_status"],
            "release": ["desktop_package_status", "desktop_run_action", "desktop_run_verification", "desktop_latest_report", "desktop_release_decision"],
        },
        "controls": [
            "No arbitrary shell tool",
            "No secret values",
            "Repository-bound file reads",
            "Build and package actions are allowlisted",
            "Reports are redacted and stored locally",
            "Release promotion requires a package or release profile with every required check passing",
        ],
    }


if __name__ == "__main__":
    log("starting stdio server")
    mcp.run(transport="stdio")
