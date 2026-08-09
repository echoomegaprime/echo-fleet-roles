# Architecture

## Components

The canonical registry declares 30 roles. Each entry maps a stable role name to one primary skill, composed skills, scoped capability patterns, and capability families. Aliases are normalized at the registry boundary.

`echo_fleet_roles.registry` validates the registry strictly. `echo_fleet_roles.state` stores one current role and an append-only transition history in SQLite with WAL, atomic transactions, unique idempotency keys, and expected-current fencing. `echo_fleet_roles.runtime` returns a host-neutral context packet. The CLI exposes list, current, context, switch, history, and validate operations.

Both host plugins package the same 30 role skills and an additional control skill named `echo-role-switching`. The Codex SessionStart and UserPromptSubmit hooks read the current state and inject the selected role's primary skill and capability families. The hook is read-only and fail-open.

## Role transitions

```text
objective phase changes
        |
        v
inspect current role -> select narrowest matching role -> atomic switch
        |                                               |
        +---- conflict: reread and reassess <------------+
                                                        |
                                                        v
                                  load primary skill and continue same session
```

Role changes are specialization changes. Tool availability, credentials, network access, and authorization remain owned by the host and engagement scope.
