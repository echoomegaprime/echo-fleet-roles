# Security policy

## Supported versions

Version 1.x receives security fixes while it is the active private/workspace release.

## Reporting

Report security issues privately through the support channel at https://echo-op.com/support.
Do not include credentials, access tokens, personal data, client records, or exploit details in
public issues.

## Boundaries

The plugin is a client bundle for an OAuth-protected MCP resource. Authorization is enforced by
the server on every protected call. Tool annotations and skill instructions are routing metadata,
not authorization. The v1 resource exposes no write, shell, browser, deployment, admin, generic
SDK-invoke, or destructive capability.

## Secret handling

Secrets remain in process environment, Echo Vault, or the identity provider. They must not be
stored in the plugin package, `.app.json`, tool results, logs, screenshots, or widget state.

## Dependencies

The bundle adds no runtime package dependency. The existing Python MCP service and its locked
repository dependencies remain subject to repository audit and update policy.
