# Contributing

Open a focused branch, preserve unrelated changes, and add tests for every contract change. New roles require a role skill in both host plugins, a strict registry entry, an alias decision, documentation, and a passing verification suite. Changes to scopes or security workflows require a security review. Do not add credentials, internal network addresses, private infrastructure paths, client data, or personal data.

Run `pwsh -NoProfile -File .\scripts\verify.ps1` before submitting. A release is not complete until hosted CI and exact-commit certification pass.
