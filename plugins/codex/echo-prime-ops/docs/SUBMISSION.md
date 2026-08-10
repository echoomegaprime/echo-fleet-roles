# Submission readiness

## Distribution verdict

Private/workspace distribution is the intended and implemented release. Public-directory submission is
`BLOCKED BY EXTERNAL DEPENDENCY` because it requires verified organization/owner portal access, production
review state, and public privacy and terms URLs that are not currently live. The private ChatGPT connection is
real and recorded as `plugin_asdk_app_6a787751cb4481918fb8308849782e86`; no URL, test-account credential, or
portal approval is fabricated.

## Prepared review material

- Display name, subtitle, functional description, category, developer, version, changelog, tool annotations,
  tool justifications, five positive cases, three negative cases, security model, data-use explanation,
  retention policy, authentication instructions, and production MCP URL.
- `chatgpt-app-submission.json` is an internal review artifact generated from the actual five tools.
- The MCP resource has explicit output schemas, narrow scopes, exact resource binding, and no write surface.

## External requirements before public submission

1. Complete current OpenAI organization verification with an owner or administrator account.
2. Publish truthful privacy-policy and terms-of-service pages, then verify HTTP 200 and content.
3. Provide review-safe identity access without sharing a password in source, submissions, or chat.
4. Run current portal validation, domain verification, country availability, screenshots only if the portal
   requires them, and all positive/negative review cases.

## Submission controls

Do not submit automatically. Submission requires explicit user authorization and authenticated portal access.
Temporary tunnels, localhost, fabricated screenshots, unverified policy URLs, and private cluster addresses are
not valid public evidence. Any portal schema drift supersedes the internal JSON artifact and must be reconciled
against current official documentation.
