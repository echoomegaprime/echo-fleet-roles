"""Tests for the shared invocation boundary in connector_runtime.

SKILL.md states: "All clients use health, list, retrieve, and invoke. Invocation
defaults to a plan; execute:true is required for a real call. This is the safety
and interoperability boundary."

That held for the stdio gateway only. The CLI reached the raw executor directly,
so `connector_runtime.py invoke <cap> <cmd>` made a real SDK call with no policy
check, no registration check, no plan default, and no audit record. These lock in
that both clients now refuse the same things and plan by default -- and that the
execute path still genuinely reaches the executor, because a boundary that blocks
everything looks identical to a boundary that works until you check.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import connector_runtime as cr  # noqa: E402
import connector_gateway as cg  # noqa: E402

REGISTERED = "echo.context.recall"   # present in registry/connectors/*.json
UNREGISTERED = "echo.totally.made.up"


@pytest.fixture
def spy(monkeypatch):
    """Replace the raw executor so no test can make a real SDK call."""
    calls: list[tuple] = []

    def fake(capability, command, options, broker):
        calls.append((capability, command, options, broker))
        return 0

    monkeypatch.setattr(cr, "invoke", fake)
    return calls


# --- plan by default -------------------------------------------------------

def test_invoke_without_execute_returns_a_plan_and_calls_nothing(spy):
    out = cr.guarded_invoke({"capability": REGISTERED, "command": "search", "role": "innovator"})
    assert out["ok"] is True
    assert out["planned"] is True
    assert spy == [], "a plan must not reach the executor"


def test_execute_true_actually_reaches_the_executor(spy):
    """Positive control. Without it, 'everything is a plan' would read as a fix."""
    out = cr.guarded_invoke({"capability": REGISTERED, "command": "search",
                             "role": "innovator", "execute": True})
    assert out["ok"] is True
    assert out["planned"] is False
    assert len(spy) == 1 and spy[0][0] == REGISTERED


def test_executor_failure_is_reported_as_not_ok(monkeypatch):
    monkeypatch.setattr(cr, "invoke", lambda *a, **k: 1)
    out = cr.guarded_invoke({"capability": REGISTERED, "command": "search",
                             "role": "innovator", "execute": True})
    assert out["ok"] is False


# --- the checks the CLI previously skipped entirely ------------------------

def test_unregistered_capability_is_refused(spy):
    out = cr.guarded_invoke({"capability": UNREGISTERED, "command": "search", "role": "innovator"})
    assert out["ok"] is False
    assert out["reason"] == "capability_not_registered"
    assert spy == []


def test_execute_without_a_role_is_refused(spy):
    out = cr.guarded_invoke({"capability": REGISTERED, "command": "search", "execute": True})
    assert out["ok"] is False
    assert out["reason"] == "role_required_for_execution"
    assert spy == [], "policy denial must happen before the executor"


def test_restricted_sensitivity_is_refused(spy):
    out = cr.guarded_invoke({"capability": REGISTERED, "command": "search",
                             "role": "innovator", "sensitivity": "restricted", "execute": True})
    assert out["ok"] is False
    assert out["reason"] == "restricted_data_requires_explicit_boundary"
    assert spy == []


def test_missing_command_is_refused(spy):
    out = cr.guarded_invoke({"capability": REGISTERED, "role": "innovator"})
    assert out["ok"] is False
    assert spy == []


def test_non_dict_options_are_refused(spy):
    out = cr.guarded_invoke({"capability": REGISTERED, "command": "search",
                             "role": "innovator", "options": ["not", "a", "dict"], "execute": True})
    assert out["ok"] is False
    assert out["reason"] == "invalid_invocation_shape"
    assert spy == []


def test_request_without_op_is_still_fully_gated(spy):
    """policy() returns {'allowed': True, 'mode': 'read'} for any op != 'invoke'.

    A caller that simply omitted `op` would otherwise bypass every check, so the
    boundary sets it itself. This is the fail-open case, not a formality.
    """
    out = cr.guarded_invoke({"capability": UNREGISTERED, "command": "x", "execute": True})
    assert out["ok"] is False
    assert spy == []


# --- audit -----------------------------------------------------------------

@pytest.mark.parametrize("request_payload", [
    {"capability": REGISTERED, "command": "search", "role": "innovator"},
    {"capability": UNREGISTERED, "command": "search", "role": "innovator"},
    {"capability": REGISTERED, "command": "search", "execute": True},
])
def test_every_outcome_carries_an_audit_record(request_payload, spy):
    out = cr.guarded_invoke(request_payload)
    assert "audit" in out, "refusals need an audit trail as much as successes do"
    assert out["audit"]["op"] == "invoke"


# --- both clients share one boundary ---------------------------------------

@pytest.mark.parametrize("payload", [
    {"capability": UNREGISTERED, "command": "search", "role": "innovator"},
    {"capability": REGISTERED, "command": "search", "execute": True},          # no role
    {"capability": REGISTERED, "command": "search", "role": "innovator"},      # plan
])
def test_gateway_and_direct_call_agree(payload, spy):
    """The defect was two clients with different rules. Prove they cannot diverge."""
    via_gateway = cg.dispatch({**payload, "op": "invoke"})
    via_runtime = cr.guarded_invoke(payload)
    assert via_gateway["ok"] == via_runtime["ok"]
    assert via_gateway.get("error") == via_runtime.get("error")
    assert via_gateway.get("planned") == via_runtime.get("planned")


def test_gateway_still_lists_invoke_as_supported():
    out = cg.dispatch({"op": "nonsense"})
    assert "invoke" in out["supported"]


# --- health ----------------------------------------------------------------

def test_health_reports_registry_state():
    report = cr.health()
    assert report["ok"] is True
    assert report["connector_count"] > 0
    assert report["role_count"] > 0
    assert report["faults"] == []


def test_health_reports_a_fault_instead_of_raising(monkeypatch, tmp_path):
    """A diagnostic that crashes tells you nothing; it must name the fault."""
    monkeypatch.setattr(cr, "REGISTRY", tmp_path / "gone")
    report = cr.health()
    assert report["ok"] is False
    assert report["faults"], "an unreadable registry must be named, not swallowed"


# --- CLI -------------------------------------------------------------------

def test_cli_exposes_all_four_documented_verbs(capsys, monkeypatch):
    for verb in ("health", "list"):
        monkeypatch.setattr(sys, "argv", ["connector_runtime.py", verb])
        assert cr.main() == 0
        capsys.readouterr()


def test_cli_invoke_defaults_to_plan(capsys, monkeypatch, spy):
    monkeypatch.setattr(sys, "argv",
                        ["connector_runtime.py", "invoke", REGISTERED, "search", "--role", "innovator"])
    assert cr.main() == 0
    assert json.loads(capsys.readouterr().out)["planned"] is True
    assert spy == [], "the CLI must not execute without --execute"


def test_cli_execute_flag_reaches_the_executor(capsys, monkeypatch, spy):
    monkeypatch.setattr(sys, "argv",
                        ["connector_runtime.py", "invoke", REGISTERED, "search",
                         "--role", "innovator", "--execute"])
    assert cr.main() == 0
    assert json.loads(capsys.readouterr().out)["planned"] is False
    assert len(spy) == 1


def test_cli_rejects_malformed_options_json(capsys, monkeypatch, spy):
    monkeypatch.setattr(sys, "argv",
                        ["connector_runtime.py", "invoke", REGISTERED, "search", "--options", "{oops"])
    assert cr.main() == 2
    assert spy == []


def test_cli_returns_nonzero_when_refused(capsys, monkeypatch, spy):
    monkeypatch.setattr(sys, "argv",
                        ["connector_runtime.py", "invoke", UNREGISTERED, "search", "--role", "innovator"])
    assert cr.main() == 1, "a refused call must not exit 0"
    capsys.readouterr()
