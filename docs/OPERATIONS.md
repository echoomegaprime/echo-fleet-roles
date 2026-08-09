# Operations

## Common commands

```powershell
echo-role --json list
echo-role --json current
echo-role --json context pentester
echo-role --json switch architect --expected-current commander --idempotency-key design-1 --reason "system design"
echo-role --json history --limit 25
```

Use a deterministic idempotency key for retryable automation. Use `--expected-current` when multiple agents or processes may update the shared state. Exit code `2` means invalid input, an invalid registry, or a state conflict.

The default state path is `%LOCALAPPDATA%\EchoFleetRoles\state.sqlite3` on Windows and `$XDG_STATE_HOME/echo-fleet-roles/state.sqlite3` on POSIX. Set `ECHO_ROLE_STATE` for hooks or `--state` for the CLI to use an isolated store.

## Choosing roles

- Commander coordinates priority and integration.
- Architect designs; Builder implements; Enhancer hardens; Judge verifies; Harbormaster controls release.
- Reverse Engineer handles clean-room analysis and reconstruction.
- Pentester handles authorized offensive, defensive, detection, validation, and purple-team workflows within registered scope.
- Compliance Officer validates evidence and control obligations.

Do not switch merely to accumulate capabilities. Switch when the material workflow and responsibility actually change.
