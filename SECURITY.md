# Security Policy

## Supported versions

Security fixes are applied to the latest tagged release on `main`.

## Reporting

Report suspected vulnerabilities privately to `bobbymcwilliams@echo-op.com`. Do not include credentials, access tokens, client data, or exploit artifacts in a public issue.

## Boundaries

- A role never grants authority or permissions; host policy and explicit authorization remain controlling.
- The runtime stores no secrets and does not access the network.
- Hook code is fail-open for host availability and read-only with respect to role state.
- Plugin hooks require user trust before execution.
- Security testing roles require a defined target, authorization boundaries, permitted test classes, exclusions, and stop conditions before active execution.

Dependencies are intentionally limited to the Python standard library. Release artifacts are hash-pinned and certified against an exact commit.
