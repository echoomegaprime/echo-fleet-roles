# Source of Truth

Checked: 2026-08-09 (America/Chicago).

Implementation was grounded in the current official Codex and ChatGPT plugin manual fetched through the official OpenAI documentation skill. Reviewed subjects included plugin manifests, bundled skills, local marketplace structure, lifecycle hooks, plugin data directories, plugin hook trust, and installation behavior.

Official references:

- <https://developers.openai.com/plugins/build/plugins>
- <https://learn.chatgpt.com/docs/plugins>
- <https://learn.chatgpt.com/docs/hooks>

Decisions derived from current documentation:

- Codex uses `.codex-plugin/plugin.json`; the plugin declares `skills` and `hooks` with root-relative `./` paths.
- The repo-scoped marketplace lives at `.agents/plugins/marketplace.json` and points to the bundled plugin.
- Hook commands use `PLUGIN_ROOT`; hook state is stored outside the immutable plugin directory.
- Plugin hook definitions require explicit trust review.
- A host restart/new session may be needed once after initial plugin installation, but role transitions do not require new terminals or processes after the plugin is loaded.

Rejected older patterns:

- The legacy 29-role split that kept reverse engineering in a separate plugin.
- Private boot-prompt paths embedded in a public registry.
- Treating a role label as an authorization grant.
- The stale MIT field on the Claude plugin, which conflicted with the source's proprietary license.
