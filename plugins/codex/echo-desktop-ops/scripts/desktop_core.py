"""Production-safe operations and readiness core for Echo Desktop."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.error import URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel, Field

DEFAULT_REPOSITORY = Path(os.environ.get("ECHO_DESKTOP_REPO", r"C:\Users\bobmc\echo-desktop"))
DEFAULT_REPORT_DIR = Path(
    os.environ.get("ECHO_DESKTOP_OPS_REPORT_DIR", str(Path.home() / ".echo" / "echo-desktop-ops" / "reports"))
)
DEFAULT_TIMEOUT_SECONDS = 900
MAX_TEXT_BYTES = 200_000
MAX_RESULTS = 100

SECRET_NAME_RE = re.compile(
    r"(^|[._-])(env|secret|secrets|token|tokens|credential|credentials|oauth|private|key)([._-]|$)",
    re.IGNORECASE,
)
SECRET_TEXT_PATTERNS = (
    re.compile(r"Bearer\s+[A-Za-z0-9._~+\-/=]+", re.IGNORECASE),
    re.compile(r"(api[_-]?key|token|secret|authorization|password)\s*[:=]\s*[^\s\"']+", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----", re.IGNORECASE | re.DOTALL),
)
EXCLUDED_PARTS = {
    ".git", "node_modules", "dist", "dist-electron", "release", "__pycache__", ".pytest_cache",
    ".venv", "venv", ".next", "coverage", "secrets", "research/asar_extract",
}
TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".ps1", ".css", ".scss", ".html",
    ".xml", ".sql", ".sh", ".bat", ".cmd", ".env.example",
}


class CheckResult(BaseModel):
    name: str
    status: Literal["pass", "fail", "warn", "skip"]
    required: bool = True
    detail: str
    duration_ms: int | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)


class VerificationReport(BaseModel):
    report_id: str
    created_at: str
    repository: str
    profile: Literal["inspect", "quick", "full", "package", "release"]
    checks: list[CheckResult]
    required_passed: int
    required_total: int
    release_ready: bool
    secrets_redacted: bool = True
    git_branch: str = ""
    git_commit: str = ""
    version: str = ""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact(value: str) -> str:
    clean = value or ""
    for pattern in SECRET_TEXT_PATTERNS:
        clean = pattern.sub(lambda match: f"{match.group(1)}=[REDACTED]" if match.lastindex else "[REDACTED]", clean)
    clean = re.sub(r"([?&](?:key|token|secret)=)[^&\s]+", r"\1[REDACTED]", clean, flags=re.IGNORECASE)
    clean = re.sub(r"([A-Za-z]:\\Users\\)[^\\\s]+", r"\1[USER]", clean)
    return clean[:MAX_TEXT_BYTES]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_relative_path(repository: Path, relative_path: str) -> Path:
    if not relative_path or Path(relative_path).is_absolute():
        raise ValueError("Path must be relative to the Echo Desktop repository")
    candidate = (repository / relative_path).resolve()
    root = repository.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("Path escapes the Echo Desktop repository") from exc
    lowered_parts = {part.lower() for part in candidate.relative_to(root).parts}
    if lowered_parts & {part.lower() for part in EXCLUDED_PARTS}:
        raise ValueError("Path is inside an excluded build, dependency, or secret directory")
    if SECRET_NAME_RE.search(candidate.name) and candidate.name.lower() not in {".env.example"}:
        raise ValueError("Secret-bearing files are not exposed")
    return candidate


def command_path(name: str) -> str:
    found = shutil.which(name)
    return str(Path(found).resolve()) if found else ""


def compact_output(text: str, limit: int = 80_000) -> str:
    return redact(text[-limit:])


class ReportStore:
    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or DEFAULT_REPORT_DIR
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, report: VerificationReport) -> Path:
        path = self.directory / f"{report.report_id}.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(path)
        return path

    def load(self, report_id: str) -> VerificationReport | None:
        if not re.fullmatch(r"[0-9a-f]{32}", report_id or ""):
            return None
        path = self.directory / f"{report_id}.json"
        if not path.is_file():
            return None
        return VerificationReport.model_validate_json(path.read_text(encoding="utf-8"))

    def latest(self) -> VerificationReport | None:
        reports = sorted(self.directory.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        for path in reports:
            try:
                return VerificationReport.model_validate_json(path.read_text(encoding="utf-8"))
            except Exception:
                continue
        return None


class EchoDesktopVerifier:
    def __init__(
        self,
        repository: Path | str = DEFAULT_REPOSITORY,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        report_store: ReportStore | None = None,
    ) -> None:
        self.repository = Path(repository).expanduser().resolve()
        self.timeout_seconds = min(max(int(timeout_seconds), 30), 3600)
        self.report_store = report_store or ReportStore()

    def _run(
        self,
        name: str,
        command: list[str],
        *,
        required: bool = True,
        timeout: int | None = None,
        cwd: Path | None = None,
    ) -> CheckResult:
        started = time.perf_counter()
        executable = command_path(command[0]) if not Path(command[0]).is_file() else command[0]
        if not executable:
            return CheckResult(name=name, status="fail" if required else "warn", required=required, detail=f"Executable unavailable: {command[0]}")
        actual = [executable, *command[1:]]
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            completed = subprocess.run(
                actual,
                cwd=str(cwd or self.repository),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout or self.timeout_seconds,
                creationflags=creation_flags,
                check=False,
            )
            output = compact_output(f"{completed.stdout}\n{completed.stderr}")
            return CheckResult(
                name=name,
                status="pass" if completed.returncode == 0 else "fail",
                required=required,
                detail=f"Exit code {completed.returncode}",
                duration_ms=round((time.perf_counter() - started) * 1000),
                evidence={"command": [Path(actual[0]).name, *actual[1:]], "output": output},
            )
        except subprocess.TimeoutExpired as exc:
            output = compact_output(f"{exc.stdout or ''}\n{exc.stderr or ''}")
            return CheckResult(
                name=name,
                status="fail" if required else "warn",
                required=required,
                detail=f"Timed out after {timeout or self.timeout_seconds} seconds",
                duration_ms=round((time.perf_counter() - started) * 1000),
                evidence={"command": [Path(actual[0]).name, *actual[1:]], "output": output},
            )
        except Exception as exc:
            return CheckResult(
                name=name,
                status="fail" if required else "warn",
                required=required,
                detail=redact(f"{type(exc).__name__}: {exc}"),
                duration_ms=round((time.perf_counter() - started) * 1000),
            )

    def _git_text(self, *args: str) -> str:
        result = self._run("git", ["git", *args], required=False, timeout=60)
        return str(result.evidence.get("output", "")).strip() if result.status == "pass" else ""

    def _package_json(self) -> dict[str, Any]:
        path = self.repository / "package.json"
        if not path.is_file():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def environment_status(self) -> dict[str, Any]:
        package = self._package_json()
        return {
            "repository": str(self.repository),
            "repository_present": self.repository.is_dir(),
            "package_present": (self.repository / "package.json").is_file(),
            "name": package.get("name", ""),
            "version": package.get("version", ""),
            "branch": self._git_text("branch", "--show-current"),
            "commit": self._git_text("rev-parse", "--short", "HEAD"),
            "dirty_files": len([line for line in self._git_text("status", "--porcelain").splitlines() if line.strip()]),
            "executables": {
                name: {"available": bool(command_path(name)), "path": redact(command_path(name))}
                for name in ("node", "npm", "python", "git", "codex", "claude", "gemini", "qwen", "copilot", "gh")
            },
            "report_directory": str(self.report_store.directory),
            "secret_values_returned": False,
        }

    def git_status(self) -> dict[str, Any]:
        status = self._git_text("status", "--porcelain=v1", "--branch")
        log = self._git_text("log", "-10", "--oneline", "--decorate")
        branches = self._git_text("branch", "--format=%(refname:short)")
        return {
            "branch": self._git_text("branch", "--show-current"),
            "commit": self._git_text("rev-parse", "HEAD"),
            "status": status,
            "recent_commits": log.splitlines(),
            "local_branches": branches.splitlines(),
            "clean": not any(line and not line.startswith("##") for line in status.splitlines()),
        }

    def cli_status(self) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        for name in ("codex", "claude", "gemini", "qwen", "copilot", "gh"):
            path = command_path(name)
            row: dict[str, Any] = {"id": name, "available": bool(path), "path": redact(path)}
            if path:
                check = self._run(f"{name}_version", [name, "--version"], required=False, timeout=30)
                row["version_status"] = check.status
                row["version"] = str(check.evidence.get("output", "")).strip().splitlines()[:3]
            results.append(row)
        broker = self.repository / "scripts" / "echo-cli-broker.mjs"
        if broker.is_file() and command_path("node"):
            check = self._run("cli_broker_list", ["node", str(broker), "--list"], required=False, timeout=60)
            try:
                broker_results = json.loads(str(check.evidence.get("output", ""))) if check.status == "pass" else []
            except json.JSONDecodeError:
                broker_results = []
        else:
            check = CheckResult(name="cli_broker_list", status="warn", required=False, detail="Broker is unavailable")
            broker_results = []
        return {"providers": results, "broker": broker_results, "broker_status": check.model_dump(), "secret_values_returned": False}

    def _candidate_user_data_dirs(self) -> list[Path]:
        appdata = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
        candidates = [appdata / "echo-desktop", appdata / "Echo Desktop", appdata / "EchoDesktop"]
        return [path for path in candidates if path.exists()]

    def fleet_status(self) -> dict[str, Any]:
        shared_dir = self.repository / ".echo" / "fleet"
        shared_state = shared_dir / "SHARED_STATE.md"
        activity = shared_dir / "ACTIVITY.jsonl"
        state_candidates: list[Path] = []
        for base in self._candidate_user_data_dirs():
            state_candidates.append(base / "fleet-control" / "fleet-state.json")
        state_path = next((path for path in state_candidates if path.is_file()), None)
        state_summary: dict[str, Any] = {"found": False, "missions": [], "active_mission_id": ""}
        if state_path:
            try:
                payload = json.loads(state_path.read_text(encoding="utf-8"))
                missions = payload.get("missions", [])
                state_summary = {
                    "found": True,
                    "path": str(state_path),
                    "active_mission_id": payload.get("activeMissionId") or payload.get("active_mission_id") or "",
                    "mission_count": len(missions),
                    "missions": [
                        {
                            "id": item.get("id"),
                            "title": item.get("title"),
                            "status": item.get("status"),
                            "phase": item.get("currentPhase"),
                            "progress": item.get("progress"),
                            "readiness": (item.get("readiness") or {}).get("verdict"),
                            "roles": [
                                {
                                    "role": role.get("role"),
                                    "provider": role.get("cliProvider", "codex"),
                                    "status": role.get("status"),
                                    "progress": role.get("progress"),
                                    "pid": role.get("pid"),
                                }
                                for role in item.get("roles", [])
                            ],
                        }
                        for item in missions[:25]
                    ],
                }
            except Exception as exc:
                state_summary = {"found": True, "path": str(state_path), "error": redact(str(exc))}
        events: list[dict[str, Any]] = []
        if activity.is_file():
            for line in activity.read_text(encoding="utf-8", errors="replace").splitlines()[-100:]:
                try:
                    events.append(json.loads(redact(line)))
                except json.JSONDecodeError:
                    continue
        return {
            "fleet_state": state_summary,
            "shared_state_present": shared_state.is_file(),
            "shared_state_path": str(shared_state),
            "activity_path": str(activity),
            "activity_events": events,
            "secret_values_returned": False,
        }

    def shared_state(self) -> dict[str, Any]:
        shared = self.repository / ".echo" / "fleet" / "SHARED_STATE.md"
        activity = self.repository / ".echo" / "fleet" / "ACTIVITY.jsonl"
        return {
            "shared_state": redact(shared.read_text(encoding="utf-8", errors="replace")) if shared.is_file() else "",
            "activity": [redact(line) for line in activity.read_text(encoding="utf-8", errors="replace").splitlines()[-200:]] if activity.is_file() else [],
            "source_of_truth": str(self.repository / "ECHO_DESKTOP.md"),
        }

    def mcp_status(self) -> dict[str, Any]:
        appdata = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
        candidates = [
            appdata / "Claude" / "claude_desktop_config.json",
            *[base / "echo_desktop_config.json" for base in self._candidate_user_data_dirs()],
        ]
        sources: list[dict[str, Any]] = []
        merged: dict[str, Any] = {}
        for path in candidates:
            if not path.is_file():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                servers = payload.get("mcpServers", {})
                sanitized = {
                    name: {
                        "command": Path(str(config.get("command", ""))).name,
                        "arg_count": len(config.get("args", []) or []),
                        "transport": config.get("transport", "stdio" if config.get("command") else ""),
                        "url_host": re.sub(r"https?://([^/]+).*", r"\1", str(config.get("url", ""))),
                        "env_keys": sorted((config.get("env") or {}).keys()),
                    }
                    for name, config in servers.items()
                    if isinstance(config, dict)
                }
                sources.append({"path": str(path), "server_count": len(sanitized), "servers": sanitized})
                merged.update(sanitized)
            except Exception as exc:
                sources.append({"path": str(path), "error": redact(str(exc))})
        return {"sources": sources, "servers": merged, "server_count": len(merged), "secret_values_returned": False}

    def provider_status(self) -> dict[str, Any]:
        providers: list[dict[str, Any]] = []
        config_paths = [base / "echo_desktop_config.json" for base in self._candidate_user_data_dirs()]
        for path in config_paths:
            if not path.is_file():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                for item in payload.get("echoProviders", []) or []:
                    providers.append({
                        "id": item.get("id"),
                        "label": item.get("label"),
                        "kind": item.get("kind"),
                        "model": item.get("model"),
                        "enabled": item.get("enabled", True),
                        "zero_cost": item.get("zeroCost", False),
                        "tools_enabled": item.get("toolsEnabled", True),
                    })
            except Exception:
                continue
        bridge: dict[str, Any] = {"reachable": False}
        try:
            request = Request("http://127.0.0.1:8792/health", headers={"User-Agent": "echo-desktop-ops/0.1"})
            with urlopen(request, timeout=3) as response:
                payload = json.loads(response.read(200_000).decode("utf-8", errors="replace"))
            bridge = {
                "reachable": True,
                "ok": payload.get("ok"),
                "providers": payload.get("providers", {}),
            }
        except (URLError, TimeoutError, OSError, ValueError):
            pass
        return {"configured_providers": providers, "bridge": bridge, "secret_values_returned": False}

    def runtime_status(self) -> dict[str, Any]:
        if os.name != "nt" or not command_path("pwsh"):
            return {"supported": False, "processes": []}
        script = (
            "$ErrorActionPreference='SilentlyContinue';"
            "$p=Get-CimInstance Win32_Process | Where-Object {"
            "$_.Name -match '^(electron|node|python|pwsh|codex|claude)(\\.exe)?$' -and "
            "($_.CommandLine -like '*echo-desktop*' -or $_.CommandLine -like '*echo-cli-broker*' -or $_.CommandLine -like '*desktop_mcp.py*')};"
            "$p | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Depth 4 -Compress"
        )
        check = self._run("runtime_processes", ["pwsh", "-NoLogo", "-NoProfile", "-Command", script], required=False, timeout=30)
        raw = str(check.evidence.get("output", "")).strip()
        try:
            parsed = json.loads(raw) if raw else []
            rows = parsed if isinstance(parsed, list) else [parsed]
        except json.JSONDecodeError:
            rows = []
        return {"supported": True, "processes": rows, "status": check.status, "secret_values_returned": False}

    def feature_parity_status(self) -> dict[str, Any]:
        path = self.repository / "FEATURE_PARITY.md"
        if not path.is_file():
            return {"present": False, "total": 0, "completed": 0, "unresolved": [], "complete": False}
        rows: list[dict[str, str]] = []
        done_markers = {"done", "complete", "completed", "pass", "passed", "yes", "green", "x", "[x]", "✓", "✔", "✅"}
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not re.match(r"^\|\s*[A-H]\d+\s*\|", line):
                continue
            parts = [part.strip() for part in line.split("|")]
            if len(parts) < 5:
                continue
            item_id, feature, status = parts[1], parts[2], parts[3]
            normalized = status.lower().strip()
            complete = normalized in done_markers or any(marker in status for marker in ("✅", "✓", "✔"))
            rows.append({"id": item_id, "feature": feature, "status": status, "complete": complete})
        unresolved = [row for row in rows if not row["complete"]]
        return {
            "present": True,
            "path": str(path),
            "total": len(rows),
            "completed": len(rows) - len(unresolved),
            "unresolved_count": len(unresolved),
            "unresolved": unresolved[:100],
            "complete": bool(rows) and not unresolved,
        }

    def implementation_gap_status(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        settings = self.repository / "src" / "views" / "SettingsModal.tsx"
        if settings.is_file():
            content = settings.read_text(encoding="utf-8", errors="replace")
            if "<Placeholder" in content or "function Placeholder" in content:
                findings.append({"type": "literal_placeholder", "path": "src/views/SettingsModal.tsx", "detail": "One or more Settings tabs still render a placeholder component"})
        pattern = re.compile(r"\b(TODO|FIXME|NOT IMPLEMENTED|COMING SOON)\b", re.IGNORECASE)
        for base_name in ("src", "electron", "bridge"):
            base = self.repository / base_name
            if not base.is_dir():
                continue
            for path in base.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > 2_000_000:
                    continue
                relative = path.relative_to(self.repository)
                try:
                    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                        if pattern.search(line):
                            findings.append({"type": "marker", "path": str(relative), "line": line_number, "detail": redact(line.strip())[:500]})
                            if len(findings) >= 100:
                                break
                except OSError:
                    continue
                if len(findings) >= 100:
                    break
        return {"blocking_count": len(findings), "findings": findings, "clear": not findings}

    def release_document_status(self) -> dict[str, Any]:
        required = {
            "README.md": "Product overview and operating instructions",
            "SECURITY.md": "Security reporting and support policy",
            "PRIVACY.md": "Privacy and data-handling disclosure",
            "CHANGELOG.md": "Versioned release history",
            "THIRD_PARTY_NOTICES.md": "Third-party licenses and notices",
            "docs/USER_GUIDE.md": "User-facing installation and operation guide",
        }
        rows = []
        for relative, purpose in required.items():
            path = self.repository / relative
            rows.append({"path": relative, "purpose": purpose, "present": path.is_file(), "size": path.stat().st_size if path.is_file() else 0})
        missing = [row for row in rows if not row["present"]]
        return {"documents": rows, "missing": missing, "complete": not missing}

    def _authenticode_status(self, path: Path) -> dict[str, Any]:
        pwsh = command_path("pwsh")
        if not pwsh or os.name != "nt":
            return {"checked": False, "status": "unsupported", "valid": False}
        escaped = str(path).replace("'", "''")
        script = (
            f"$s=Get-AuthenticodeSignature -LiteralPath '{escaped}';"
            "[pscustomobject]@{Status=$s.Status.ToString();StatusMessage=$s.StatusMessage;"
            "Subject=if($s.SignerCertificate){$s.SignerCertificate.Subject}else{''}}|ConvertTo-Json -Compress"
        )
        result = self._run("installer_signature", ["pwsh", "-NoLogo", "-NoProfile", "-Command", script], required=False, timeout=60)
        try:
            payload = json.loads(str(result.evidence.get("output", ""))) if result.status == "pass" else {}
        except json.JSONDecodeError:
            payload = {}
        status = str(payload.get("Status", "Unknown"))
        return {
            "checked": True,
            "status": status,
            "status_message": redact(str(payload.get("StatusMessage", ""))),
            "signer_subject": redact(str(payload.get("Subject", ""))),
            "valid": status.lower() == "valid",
        }

    def packaged_fleet_tools_check(self) -> CheckResult:
        unpacked = self.repository / "release" / "win-unpacked"
        executable = unpacked / "Echo Desktop.exe"
        if not executable.is_file():
            executable = unpacked / "electron.exe"
        broker = unpacked / "resources" / "fleet-tools" / "echo-cli-broker.mjs"
        ledger = unpacked / "resources" / "fleet-tools" / "echo-fleet-ledger.mjs"
        instructions = unpacked / "resources" / "fleet-instructions" / "ECHO_DESKTOP.md"
        missing = [str(path) for path in (executable, broker, ledger, instructions) if not path.is_file()]
        if missing:
            return CheckResult(name="packaged_fleet_tools", status="fail", detail="Packaged Fleet resources are missing", evidence={"missing": missing})
        env = dict(os.environ)
        env["ELECTRON_RUN_AS_NODE"] = "1"
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                [str(executable), str(broker), "--list"],
                cwd=str(self.repository),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=90,
                env=env,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                check=False,
            )
            payload = json.loads(completed.stdout) if completed.returncode == 0 else []
            ids = sorted(item.get("id") for item in payload if isinstance(item, dict))
            expected = ["claude", "codex", "copilot", "gemini", "qwen"]
            passed = completed.returncode == 0 and ids == expected
            return CheckResult(
                name="packaged_fleet_tools",
                status="pass" if passed else "fail",
                detail="Bundled broker executed through packaged Electron Node mode" if passed else "Bundled broker did not return the complete provider catalog",
                duration_ms=round((time.perf_counter() - started) * 1000),
                evidence={"provider_ids": ids, "returncode": completed.returncode, "stderr": compact_output(completed.stderr, 20_000)},
            )
        except Exception as exc:
            return CheckResult(name="packaged_fleet_tools", status="fail", detail=redact(f"{type(exc).__name__}: {exc}"))

    def packaged_startup_smoke_check(self) -> CheckResult:
        unpacked = self.repository / "release" / "win-unpacked"
        executable = unpacked / "Echo Desktop.exe"
        if not executable.is_file():
            executable = unpacked / "electron.exe"
        if not executable.is_file():
            return CheckResult(name="packaged_startup_smoke", status="fail", detail="Packaged executable is missing")
        profile = self.report_store.directory.parent / f"smoke-{uuid.uuid4().hex}"
        started = time.perf_counter()
        process: subprocess.Popen[str] | None = None
        try:
            process = subprocess.Popen(
                [str(executable), f"--user-data-dir={profile}", "--disable-gpu"],
                cwd=str(unpacked),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
                creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
            )
            time.sleep(8)
            alive = process.poll() is None
            return CheckResult(
                name="packaged_startup_smoke",
                status="pass" if alive else "fail",
                detail="Packaged Echo Desktop remained alive through startup smoke" if alive else f"Packaged process exited with code {process.returncode}",
                duration_ms=round((time.perf_counter() - started) * 1000),
            )
        except Exception as exc:
            return CheckResult(name="packaged_startup_smoke", status="fail", detail=redact(f"{type(exc).__name__}: {exc}"))
        finally:
            if process and process.poll() is None:
                try:
                    if os.name == "nt" and command_path("taskkill"):
                        subprocess.run([command_path("taskkill"), "/PID", str(process.pid), "/T", "/F"], capture_output=True, timeout=30, check=False)
                    else:
                        process.terminate()
                except Exception:
                    pass
            shutil.rmtree(profile, ignore_errors=True)

    def fleet_e2e_evidence_check(self) -> CheckResult:
        status = self.fleet_status().get("fleet_state", {})
        missions = status.get("missions", []) if isinstance(status, dict) else []
        qualifying = []
        for mission in missions:
            roles = {row.get("role"): row for row in mission.get("roles", []) if isinstance(row, dict)}
            required_roles = {"commander", "deputy_commander", "architect", "builder", "enhancer", "publisher", "observer"}
            role_complete = required_roles.issubset(roles) and all(roles[name].get("status") == "complete" for name in required_roles)
            if role_complete and mission.get("status") == "complete" and mission.get("readiness") in {"production-ready", "conditionally-ready"}:
                qualifying.append(mission.get("id"))
        return CheckResult(
            name="fleet_e2e_mission_evidence",
            status="pass" if qualifying else "fail",
            detail="A complete Commander/Deputy multi-role mission is preserved as readiness evidence" if qualifying else "No complete Commander/Deputy Architect→Builder→Enhancer→Publisher→Observer mission is recorded",
            evidence={"qualifying_mission_ids": qualifying, "mission_count": len(missions)},
        )

    def package_status(self) -> dict[str, Any]:
        release = self.repository / "release"
        artifacts: list[dict[str, Any]] = []
        if release.is_dir():
            for path in sorted(release.glob("*")):
                if not path.is_file():
                    continue
                artifacts.append({
                    "name": path.name,
                    "size": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                    "sha256": sha256_file(path),
                })
        setup = [item for item in artifacts if item["name"].lower().endswith(".exe") and "setup" in item["name"].lower()]
        installer_signature = self._authenticode_status(release / setup[0]["name"]) if setup else {"checked": False, "status": "missing", "valid": False}
        unpacked = release / "win-unpacked"
        app_executables = [path.name for path in unpacked.glob("*.exe")] if unpacked.is_dir() else []
        return {
            "release_directory": str(release),
            "artifacts": artifacts,
            "final_installer_present": bool(setup),
            "final_installers": setup,
            "installer_signature": installer_signature,
            "intermediate_nsis_archive_present": any(item["name"].lower().endswith(".nsis.7z") for item in artifacts),
            "win_unpacked_present": unpacked.is_dir(),
            "win_unpacked_executables": app_executables,
        }

    def project_snapshot(self) -> dict[str, Any]:
        package = self._package_json()
        important = [
            "README.md", "SPEC.md", "FEATURE_PARITY.md", "ECHO_DESKTOP.md", "AGENTS.md", "CLAUDE.md",
            "GEMINI.md", "QWEN.md", "docs/FLEET_CONTROL_SPEC.md", "docs/CLI_ORCHESTRATION.md",
            "electron/main/fleet.ts", "src/views/FleetControlView.tsx", "scripts/echo-cli-broker.mjs",
            "scripts/echo-fleet-ledger.mjs",
        ]
        files = []
        for relative in important:
            path = self.repository / relative
            files.append({"path": relative, "present": path.is_file(), "size": path.stat().st_size if path.is_file() else 0})
        return {
            "environment": self.environment_status(),
            "git": self.git_status(),
            "package": {
                "name": package.get("name"),
                "version": package.get("version"),
                "description": package.get("description"),
                "scripts": sorted((package.get("scripts") or {}).keys()),
                "dependencies": sorted((package.get("dependencies") or {}).keys()),
                "dev_dependencies": sorted((package.get("devDependencies") or {}).keys()),
            },
            "important_files": files,
            "feature_parity": self.feature_parity_status(),
            "implementation_gaps": self.implementation_gap_status(),
            "release_documents": self.release_document_status(),
            "package_status": self.package_status(),
        }

    def read_project_file(self, relative_path: str, max_bytes: int = 100_000) -> dict[str, Any]:
        path = safe_relative_path(self.repository, relative_path)
        if not path.is_file():
            raise FileNotFoundError(relative_path)
        size = path.stat().st_size
        limit = min(max(int(max_bytes), 1_000), MAX_TEXT_BYTES)
        if size > limit:
            content = path.read_bytes()[:limit].decode("utf-8", errors="replace")
            truncated = True
        else:
            content = path.read_text(encoding="utf-8", errors="replace")
            truncated = False
        return {"path": relative_path, "size": size, "truncated": truncated, "content": redact(content)}

    def search_project(self, query: str, path_prefix: str = "", limit: int = 50) -> dict[str, Any]:
        needle = query.strip()
        if not needle:
            raise ValueError("Search query is required")
        start = safe_relative_path(self.repository, path_prefix) if path_prefix else self.repository
        if not start.exists():
            raise FileNotFoundError(path_prefix)
        results: list[dict[str, Any]] = []
        maximum = min(max(int(limit), 1), MAX_RESULTS)
        paths = [start] if start.is_file() else start.rglob("*")
        for path in paths:
            if len(results) >= maximum or not path.is_file():
                continue
            relative = path.relative_to(self.repository)
            lowered = {part.lower() for part in relative.parts}
            if lowered & {part.lower() for part in EXCLUDED_PARTS}:
                continue
            if SECRET_NAME_RE.search(path.name) and path.name.lower() != ".env.example":
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES and path.name.lower() not in {"dockerfile", "makefile"}:
                continue
            try:
                if path.stat().st_size > 2_000_000:
                    continue
                for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if needle.lower() in line.lower():
                        results.append({"path": str(relative), "line": line_number, "text": redact(line.strip())[:500]})
                        if len(results) >= maximum:
                            break
            except OSError:
                continue
        return {"query": needle, "results": results, "count": len(results), "truncated": len(results) >= maximum}

    def inspection_checks(self) -> list[CheckResult]:
        checks: list[CheckResult] = []
        repo_ok = self.repository.is_dir() and (self.repository / "package.json").is_file()
        checks.append(CheckResult(name="repository", status="pass" if repo_ok else "fail", detail="Echo Desktop repository is present" if repo_ok else "Repository or package.json is missing"))
        for relative in ("ECHO_DESKTOP.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "QWEN.md"):
            present = (self.repository / relative).is_file()
            checks.append(CheckResult(name=f"instruction_{relative.lower().replace('.', '_')}", status="pass" if present else "fail", detail=f"{relative} {'present' if present else 'missing'}"))
        for relative in ("electron/main/fleet.ts", "src/views/FleetControlView.tsx", "scripts/echo-cli-broker.mjs", "scripts/echo-fleet-ledger.mjs"):
            present = (self.repository / relative).is_file()
            checks.append(CheckResult(name=f"component_{Path(relative).stem}", status="pass" if present else "fail", detail=f"{relative} {'present' if present else 'missing'}"))
        parity = self.feature_parity_status()
        checks.append(CheckResult(
            name="feature_parity_complete",
            status="pass" if parity["complete"] else "fail",
            detail=f"Feature parity complete ({parity['completed']}/{parity['total']})" if parity["complete"] else f"Feature parity unresolved ({parity['unresolved_count']}/{parity['total']} rows)",
            evidence=parity,
        ))
        gaps = self.implementation_gap_status()
        checks.append(CheckResult(
            name="implementation_placeholders",
            status="pass" if gaps["clear"] else "fail",
            detail="No release-blocking placeholders remain" if gaps["clear"] else f"{gaps['blocking_count']} release-blocking placeholder or implementation markers remain",
            evidence=gaps,
        ))
        git = self.git_status()
        checks.append(CheckResult(name="git_worktree_clean", status="pass" if git["clean"] else "fail", detail="Worktree is clean" if git["clean"] else "Worktree contains uncommitted changes"))
        package = self.package_status()
        checks.append(CheckResult(name="windows_installer", status="pass" if package["final_installer_present"] else "fail", detail="Final Windows setup executable exists" if package["final_installer_present"] else "Final Windows setup executable is missing"))
        return checks

    def security_checks(self) -> list[CheckResult]:
        checks: list[CheckResult] = []
        main = (self.repository / "electron" / "main" / "index.ts").read_text(encoding="utf-8", errors="replace") if (self.repository / "electron" / "main" / "index.ts").is_file() else ""
        preload = (self.repository / "electron" / "preload" / "index.ts").read_text(encoding="utf-8", errors="replace") if (self.repository / "electron" / "preload" / "index.ts").is_file() else ""
        renderer_files = list((self.repository / "src").rglob("*.ts")) + list((self.repository / "src").rglob("*.tsx")) if (self.repository / "src").is_dir() else []
        renderer = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in renderer_files if path.stat().st_size < 2_000_000)
        # The app centralizes secure webPreferences in mergeHardenedWebPreferences() /
        # HARDENED_WEB_PREFERENCES (electron/main/ipc-hardening.ts), which spreads the caller
        # partial FIRST then hard-sets contextIsolation:true + nodeIntegration:false (non-overridable),
        # and every `new BrowserWindow` applies it. Recognize that pattern in addition to inline
        # literals so a centralized-hardening design is not a false "fail". Still fails on any explicit
        # unsafe override (contextIsolation:false / nodeIntegration:true) appearing in the main process.
        hardening = (self.repository / "electron" / "main" / "ipc-hardening.ts").read_text(encoding="utf-8", errors="replace") if (self.repository / "electron" / "main" / "ipc-hardening.ts").is_file() else ""
        helper_hardened = ("mergeHardenedWebPreferences" in main and "contextIsolation: true" in hardening and "nodeIntegration: false" in hardening)
        ci_ok = ("contextIsolation: true" in main or helper_hardened) and "contextIsolation: false" not in main
        ni_ok = ("nodeIntegration: false" in main or helper_hardened) and "nodeIntegration: true" not in main
        checks.append(CheckResult(name="electron_context_isolation", status="pass" if ci_ok else "fail", detail="contextIsolation enabled" if ci_ok else "contextIsolation was not verified"))
        checks.append(CheckResult(name="electron_node_integration", status="pass" if ni_ok else "fail", detail="Renderer Node integration disabled" if ni_ok else "Unsafe Node integration setting detected or missing"))
        checks.append(CheckResult(name="preload_context_bridge", status="pass" if "contextBridge.exposeInMainWorld" in preload else "fail", detail="Preload uses contextBridge" if "contextBridge.exposeInMainWorld" in preload else "Preload contextBridge missing"))
        checks.append(CheckResult(name="renderer_no_child_process", status="pass" if "node:child_process" not in renderer and "child_process" not in renderer else "fail", detail="Renderer does not import child_process" if "child_process" not in renderer else "Renderer child_process reference found"))
        checks.append(self._run("npm_audit", ["npm", "audit", "--audit-level=high"], required=True, timeout=300))
        return checks

    def run_action(self, action: str) -> CheckResult:
        actions: dict[str, tuple[str, list[str], bool, int]] = {
            "typecheck": ("TypeScript typecheck", ["npm", "run", "typecheck"], True, 600),
            "fleet_tests": ("Fleet Control contract tests", ["npm", "run", "test:fleet"], True, 600),
            "build": ("Production build", ["npm", "run", "build"], True, 900),
            "verify": ("Combined verification", ["npm", "run", "verify"], True, 1500),
            "audit": ("Dependency audit", ["npm", "audit", "--audit-level=high"], True, 300),
            "python_compile": ("Python bridge compile", ["python", "-m", "py_compile", "bridge/server.py", "bridge/ai_council.py", "bridge/gemini_rest.py", "bridge/vertex_rest.py", "scripts/smoke_bridge.py"], True, 300),
            "council_selftest": ("AI Council self-test", ["python", "bridge/ai_council.py", "--selftest"], True, 300),
            "package": ("Windows NSIS package", ["npm", "run", "dist"], True, 3600),
        }
        if action not in actions:
            raise ValueError(f"Unsupported action. Choose one of: {', '.join(sorted(actions))}")
        name, command, required, timeout = actions[action]
        return self._run(name, command, required=required, timeout=timeout)

    def run(self, profile: Literal["inspect", "quick", "full", "package", "release"] = "full") -> tuple[VerificationReport, Path]:
        checks = self.inspection_checks()
        if profile in {"quick", "full", "package", "release"}:
            checks.extend([self.run_action("typecheck"), self.run_action("fleet_tests")])
        if profile in {"full", "package", "release"}:
            checks.extend([
                self.run_action("build"),
                self.run_action("python_compile"),
                self.run_action("council_selftest"),
                *self.security_checks(),
            ])
        if profile in {"package", "release"}:
            checks.append(self.run_action("package"))
            package = self.package_status()
            checks.append(CheckResult(
                name="final_installer_after_package",
                status="pass" if package["final_installer_present"] else "fail",
                detail="Final setup executable exists" if package["final_installer_present"] else "Packaging did not produce a final setup executable",
                evidence=package,
            ))
            checks.append(self.packaged_fleet_tools_check())
            checks.append(self.packaged_startup_smoke_check())
        if profile == "release":
            package = self.package_status()
            signature = package.get("installer_signature", {})
            checks.append(CheckResult(
                name="installer_code_signature",
                status="pass" if signature.get("valid") else "fail",
                detail="Installer Authenticode signature is valid" if signature.get("valid") else f"Installer signature status: {signature.get('status', 'missing')}",
                evidence=signature,
            ))
            documents = self.release_document_status()
            for row in documents["documents"]:
                checks.append(CheckResult(
                    name=f"release_document_{row['path'].lower().replace('/', '_').replace('.', '_')}",
                    status="pass" if row["present"] else "fail",
                    detail=f"{row['path']} is present" if row["present"] else f"Missing {row['path']}: {row['purpose']}",
                    evidence=row,
                ))
            checks.append(self.fleet_e2e_evidence_check())
        required = [check for check in checks if check.required]
        passed = [check for check in required if check.status == "pass"]
        package = self._package_json()
        report = VerificationReport(
            report_id=uuid.uuid4().hex,
            created_at=utc_now(),
            repository=str(self.repository),
            profile=profile,
            checks=checks,
            required_passed=len(passed),
            required_total=len(required),
            release_ready=bool(required) and len(passed) == len(required) and profile in {"package", "release"},
            git_branch=self._git_text("branch", "--show-current"),
            git_commit=self._git_text("rev-parse", "--short", "HEAD"),
            version=str(package.get("version", "")),
        )
        return report, self.report_store.save(report)


def release_decision(report: VerificationReport | None) -> dict[str, Any]:
    if report is None:
        return {"decision": "block", "release_ready": False, "blocking_checks": ["missing_report"], "reason": "No Echo Desktop verification report exists"}
    blocking = [check.name for check in report.checks if check.required and check.status != "pass"]
    if report.profile not in {"package", "release"}:
        blocking.append("release_profile_not_run")
    decision = "promote" if report.release_ready and not blocking else "block"
    return {
        "decision": decision,
        "release_ready": decision == "promote",
        "report_id": report.report_id,
        "profile": report.profile,
        "required_passed": report.required_passed,
        "required_total": report.required_total,
        "blocking_checks": sorted(set(blocking)),
        "reason": "All required release checks passed" if decision == "promote" else "One or more required release checks are missing or failing",
    }
