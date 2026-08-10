# Claude Code Instructions

Read AGENTS.md and README.md before acting.

This repository exposes a production-safe Echo Desktop operations API. Do not add generic shell, unrestricted filesystem, credential retrieval, process-kill, deployment, or secret-vault tools. Extend the bounded API with structured inputs, redacted outputs, deterministic evidence, and tests.

Before writing a new Python function, search the ECHO function library when that capability is available. Reuse a suitable function rather than duplicating it.
