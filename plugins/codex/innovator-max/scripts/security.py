"""Dependency-free manifest signing, policy checks, and redacted audit helpers."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timezone
from typing import Any

SECRET = re.compile(r"(?i)(api[_-]?key|token|password|secret|private[_-]?key)")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def signature(payload: dict[str, Any], secret: str) -> str:
    return hmac.new(secret.encode(), canonical(payload), hashlib.sha256).hexdigest()


def verify_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    supplied = payload.get("signature")
    secret = os.environ.get("ECHO_CONNECTOR_MANIFEST_HMAC")
    required = os.environ.get("ECHO_CONNECTOR_REQUIRE_SIGNED", "0") == "1"
    if not secret:
        return {"verified": False, "required": required, "reason": "signing key unavailable"}
    body = {key: value for key, value in payload.items() if key != "signature"}
    valid = bool(supplied) and hmac.compare_digest(supplied, signature(body, secret))
    return {"verified": valid, "required": required, "reason": "ok" if valid else "invalid signature"}


def policy(request: dict[str, Any], known_capabilities: set[str]) -> dict[str, Any]:
    operation = request.get("op", "health")
    if operation == "invoke":
        capability = request.get("capability")
        if capability not in known_capabilities:
            return {"allowed": False, "reason": "capability_not_registered"}
        if not request.get("command") or not isinstance(request.get("options", {}), dict):
            return {"allowed": False, "reason": "invalid_invocation_shape"}
        if request.get("execute") and not request.get("role"):
            return {"allowed": False, "reason": "role_required_for_execution"}
        if request.get("sensitivity") == "restricted":
            return {"allowed": False, "reason": "restricted_data_requires_explicit_boundary"}
        return {"allowed": True, "mode": "execute" if request.get("execute") else "plan"}
    return {"allowed": True, "mode": "read"}


def audit(request: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {"ts": datetime.now(timezone.utc).isoformat(), "request_id": request.get("id"), "op": request.get("op"), "ok": result.get("ok", False), "capability": request.get("capability"), "redacted": True}
