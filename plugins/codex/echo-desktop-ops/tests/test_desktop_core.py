from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from desktop_core import (  # noqa: E402
    CheckResult,
    EchoDesktopVerifier,
    ReportStore,
    VerificationReport,
    redact,
    release_decision,
    safe_relative_path,
)


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "echo-desktop"
    (repo / "electron" / "main").mkdir(parents=True)
    (repo / "electron" / "preload").mkdir(parents=True)
    (repo / "src" / "views").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / ".echo" / "fleet").mkdir(parents=True)
    (repo / "package.json").write_text(json.dumps({"name": "echo-desktop", "version": "0.3.0", "scripts": {}}), encoding="utf-8")
    for name in ("ECHO_DESKTOP.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "QWEN.md"):
        (repo / name).write_text(f"# {name}\n", encoding="utf-8")
    (repo / "electron" / "main" / "fleet.ts").write_text("export const fleet = true\n", encoding="utf-8")
    (repo / "electron" / "main" / "index.ts").write_text("webPreferences: { contextIsolation: true, nodeIntegration: false }\n", encoding="utf-8")
    (repo / "electron" / "preload" / "index.ts").write_text("contextBridge.exposeInMainWorld('echo', {})\n", encoding="utf-8")
    (repo / "src" / "views" / "FleetControlView.tsx").write_text("export function FleetControlView() { return null }\n", encoding="utf-8")
    (repo / "scripts" / "echo-cli-broker.mjs").write_text("console.log('ok')\n", encoding="utf-8")
    (repo / "scripts" / "echo-fleet-ledger.mjs").write_text("console.log('ok')\n", encoding="utf-8")
    (repo / ".echo" / "fleet" / "SHARED_STATE.md").write_text("# State\n", encoding="utf-8")
    (repo / ".echo" / "fleet" / "ACTIVITY.jsonl").write_text('{"event":"checkpoint"}\n', encoding="utf-8")
    return repo


def test_redact_removes_common_secret_shapes() -> None:
    source = "api_key=abc123 Authorization: Bearer token.value password=hunter2"
    clean = redact(source)
    assert "abc123" not in clean
    assert "token.value" not in clean
    assert "hunter2" not in clean
    assert "REDACTED" in clean


def test_safe_relative_path_blocks_escape_and_secret(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    with pytest.raises(ValueError):
        safe_relative_path(repo, "../outside.txt")
    with pytest.raises(ValueError):
        safe_relative_path(repo, ".env")
    allowed = safe_relative_path(repo, "ECHO_DESKTOP.md")
    assert allowed == repo / "ECHO_DESKTOP.md"


def test_read_and_search_project_are_bounded(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo / "src" / "sample.ts").write_text("const fleetControl = true\n", encoding="utf-8")
    verifier = EchoDesktopVerifier(repo, report_store=ReportStore(tmp_path / "reports"))
    read = verifier.read_project_file("src/sample.ts")
    assert "fleetControl" in read["content"]
    search = verifier.search_project("fleetControl")
    assert search["count"] >= 1
    paths = {item["path"].replace("\\", "/") for item in search["results"]}
    assert "src/sample.ts" in paths


def test_package_status_distinguishes_intermediate_and_final(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    release = repo / "release"
    release.mkdir()
    (release / "echo-desktop-0.3.0-x64.nsis.7z").write_bytes(b"archive")
    verifier = EchoDesktopVerifier(repo, report_store=ReportStore(tmp_path / "reports"))
    first = verifier.package_status()
    assert first["intermediate_nsis_archive_present"] is True
    assert first["final_installer_present"] is False
    (release / "EchoDesktop-Setup-0.3.0.exe").write_bytes(b"installer")
    second = verifier.package_status()
    assert second["final_installer_present"] is True
    assert len(second["final_installers"][0]["sha256"]) == 64


def test_report_store_and_release_gate(tmp_path: Path) -> None:
    store = ReportStore(tmp_path / "reports")
    passing = CheckResult(name="installer", status="pass", detail="present")
    report = VerificationReport(
        report_id="a" * 32,
        created_at="2026-07-15T00:00:00+00:00",
        repository="C:/repo",
        profile="release",
        checks=[passing],
        required_passed=1,
        required_total=1,
        release_ready=True,
    )
    path = store.save(report)
    assert path.is_file()
    assert store.load("a" * 32) is not None
    assert release_decision(report)["decision"] == "promote"
    failing = report.model_copy(update={
        "report_id": "b" * 32,
        "checks": [CheckResult(name="installer", status="fail", detail="missing")],
        "required_passed": 0,
        "release_ready": False,
    })
    decision = release_decision(failing)
    assert decision["decision"] == "block"
    assert "installer" in decision["blocking_checks"]


def test_project_snapshot_exposes_no_secret_values(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    verifier = EchoDesktopVerifier(repo, report_store=ReportStore(tmp_path / "reports"))
    snapshot = verifier.project_snapshot()
    serialized = json.dumps(snapshot)
    assert "secret_values_returned" in serialized
    assert "api_key=" not in serialized.lower()


def test_feature_parity_and_placeholder_gates(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo / "FEATURE_PARITY.md").write_text(
        "| # | Feature | Status | Target |\n|---|---|---|---|\n| A1 | Stream | ✅ | x |\n| A2 | Cancel | ? | y |\n",
        encoding="utf-8",
    )
    settings = repo / "src" / "views" / "SettingsModal.tsx"
    settings.write_text("function Placeholder() { return null }\n<Placeholder />\n", encoding="utf-8")
    verifier = EchoDesktopVerifier(repo, report_store=ReportStore(tmp_path / "reports"))
    parity = verifier.feature_parity_status()
    assert parity["total"] == 2
    assert parity["completed"] == 1
    assert parity["complete"] is False
    gaps = verifier.implementation_gap_status()
    assert gaps["clear"] is False
    assert gaps["blocking_count"] >= 1


def test_release_documents_are_explicit(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    verifier = EchoDesktopVerifier(repo, report_store=ReportStore(tmp_path / "reports"))
    status = verifier.release_document_status()
    assert status["complete"] is False
    assert any(row["path"] == "PRIVACY.md" for row in status["missing"])


def _electron_status(repo: Path) -> dict[str, str]:
    verifier = EchoDesktopVerifier(repo, report_store=ReportStore(repo / "reports"))
    return {
        c.name: c.status
        for c in verifier.security_checks()
        if c.name in ("electron_context_isolation", "electron_node_integration")
    }


def test_electron_hardening_recognized_via_merge_helper(tmp_path: Path) -> None:
    # Real app centralizes hardening in mergeHardenedWebPreferences() rather than inline
    # literals at each BrowserWindow — the checker must not report that as a false "fail".
    repo = make_repo(tmp_path)
    (repo / "electron" / "main" / "index.ts").write_text(
        "mainWindow = new BrowserWindow({ webPreferences: mergeHardenedWebPreferences({ preload: PRELOAD }) })\n",
        encoding="utf-8",
    )
    (repo / "electron" / "main" / "ipc-hardening.ts").write_text(
        "export function mergeHardenedWebPreferences(p){ return { ...p, sandbox: true, "
        "contextIsolation: true, nodeIntegration: false } }\n",
        encoding="utf-8",
    )
    status = _electron_status(repo)
    assert status["electron_context_isolation"] == "pass"
    assert status["electron_node_integration"] == "pass"


def test_electron_hardening_still_fails_when_unhardened(tmp_path: Path) -> None:
    # Non-weakening: no inline literals and no hardening helper -> must still fail.
    repo = make_repo(tmp_path)
    (repo / "electron" / "main" / "index.ts").write_text(
        "mainWindow = new BrowserWindow({ webPreferences: { preload: PRELOAD } })\n",
        encoding="utf-8",
    )
    status = _electron_status(repo)
    assert status["electron_context_isolation"] == "fail"
    assert status["electron_node_integration"] == "fail"


def test_electron_hardening_fails_on_explicit_unsafe_override(tmp_path: Path) -> None:
    # Non-weakening: an explicit unsafe setting in the main process must fail even with the helper present.
    repo = make_repo(tmp_path)
    (repo / "electron" / "main" / "index.ts").write_text(
        "mainWindow = new BrowserWindow({ webPreferences: mergeHardenedWebPreferences({ preload: PRELOAD }) })\n"
        "// legacy: nodeIntegration: true\n",
        encoding="utf-8",
    )
    (repo / "electron" / "main" / "ipc-hardening.ts").write_text(
        "export function mergeHardenedWebPreferences(p){ return { ...p, sandbox: true, "
        "contextIsolation: true, nodeIntegration: false } }\n",
        encoding="utf-8",
    )
    status = _electron_status(repo)
    assert status["electron_node_integration"] == "fail"
