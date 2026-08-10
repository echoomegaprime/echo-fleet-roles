# Echo Desktop Ops Agent Instructions

Read README.md before changing this plugin.

The plugin is a bounded operations API. Preserve these invariants:

- Never expose arbitrary shell execution.
- Never return credential values, OAuth tokens, environment values, private keys, or customer data.
- Keep project file reads repository-bound and block secret-bearing paths.
- Build, test, audit, and package actions must remain allowlisted.
- Release promotion requires a package or release report with every mandatory check passing.
- Add tests for every new tool and security boundary.
- Keep tool output structured, bounded, redacted, and evidence-oriented.
