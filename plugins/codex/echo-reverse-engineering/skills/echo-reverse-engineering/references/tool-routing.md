# Reverse-engineering tool routing

Discover live capabilities before use. Names and health can move; this reference records the verified routing pattern, not a frozen inventory.

## Web and web-app analysis

Use the ShadowGlass capability family through the scoped SDK broker.

| Need | Preferred operations |
|---|---|
| Isolation | `open`, `reserve`, `release`, `close` |
| Visual and semantic capture | `shot`, `text`, `ax`, `js` |
| Runtime behavior | `console`, `network`, `respbody`, `har` |
| Performance and variants | `perf`, `metrics`, `emulate` |
| Controlled interaction | `nav`, `click`, `clicktext`, `fill`, `wait` |

Capture routes, breakpoints, UI states, authentication and tenant behavior, local storage and service-worker behavior, API schemas, failures, headers, and caching. Never put cookies, tokens, authorization headers, or private response bodies in reports.

## Native binaries

Start with the live `echo.re.binary.*` surface:

- `health` verifies the analysis backend.
- `functions`, `imports`, and `strings` build the static map.
- `decompile_fn` performs focused decompilation after a function is selected.

Search the live catalog for Ghidra, decompiler, capa, FLOSS, YARA, debugger, sandbox, and firmware capabilities before assuming a tool exists. Use general node execution only as a governed fallback.

For untrusted artifacts: hash first, copy into an isolated case directory, disable unnecessary egress, take a snapshot, monitor filesystem/process/network effects, and destroy only the disposable environment after evidence export.

## Android and mobile packages

Use `echo.re.apk.decompile`, `scan_secrets`, `endpoints`, and `report` for the first static pass. Discover MobSF, Frida, emulator, and device-lab capabilities live before dynamic work. Use only authorized lab devices and record package hash, signing identity, permissions, components, endpoints, native libraries, trackers, and runtime observations.

## Firmware and embedded systems

Search the live capability catalog for firmware, binwalk, filesystem, SBOM, emulator, and hardware-lab routes. Preserve the original image, record its hash, and analyze partitions, boot flow, filesystems, update/signature logic, services, credentials, and trust boundaries. Do not flash a production or non-lab device merely to complete an analysis.

## Crucible and node placement

Probe `echo.crucible.health` before use and prefer a purpose-built capability over a general command surface. For `echo.prometheus.command`, use dry-run or non-mutating discovery first and keep tier-2/3 actions inside the signed, audited SDK path.

- CRUCIBLE: dynamic, hostile, exploit-development, debugger, and malware-lab work.
- ANVIL: static analysis, Ghidra, large artifacts, emulation, and compute-heavy jobs.
- HAMMER: orchestration and ShadowGlass browser acquisition; never detonate unknown code.
- FORGE: production control plane and evidence registration; never use it as the malware sandbox.

## Skill composition

Load only what the case needs:

- `$browser-automation` for complex browser driving.
- `$ethical-hacking-mastery` for authorized lab analysis.
- `$codex-security:threat-model`, `$codex-security:security-scan`, and `$codex-security:validation` for security proof.
- `$echo-frontier-infrastructure` for cluster/tool routing.
- `$echo-risk-action-review` before high-impact actions.
- `$echo-proofline-verification` for evidence chains.
- `$gui-building-prime` and the relevant frontend skill for a replacement interface.
