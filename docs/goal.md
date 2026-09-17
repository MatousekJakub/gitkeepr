# Product Goal

> Human-owned source of truth. Automation may clarify factual details, but must not change the approved goal or scope without an explicit human instruction.

GitKeepr should make an AI Build ↔ Review loop practical to reuse on new repositories without searching old chats, copying large workflows by hand, or rebuilding runner setup from memory.

## V1 goal

A user should be able to:

- prepare one Ubuntu/Debian VPS with `gitkeepr server init`;
- configure a private GitHub repository with `gitkeepr init`;
- add a repository-specific persistent runner with `gitkeepr runner add owner/repo`;
- choose Build/Review models and variants through repository variables;
- use PR creation, pushes, trusted comments, submitted reviews, and manual dispatch as triggers;
- let Build and Review iterate until `PASS` or a clear blocked state;
- recover from failures without hidden state;
- understand the entire setup from this repository alone.

## Design values

- Prefer a small number of obvious moving parts.
- Prefer GitHub-native mechanisms over custom dispatchers, databases, webhooks, polling services, or queues.
- Prefer explicit shell commands and documented GitHub configuration over magic.
- Do not create abstractions without an observed need.
- It is valid to delete or simplify code instead of adding features.
- AI `PASS` is not the same thing as CI success or human approval.

## Explicit non-goals for V1

- No Issue → plan → approval → PR workflow.
- No global VPS concurrency manager.
- No generic deterministic verification framework beyond the agent running relevant tests and normal repository CI.
- No Dependabot-specific integration.
- No standard setup for public target repositories using persistent self-hosted runners.
- No automated creation or installation of the GitHub App.
- No special bot-trigger trust framework for external helpers.
- No custom scheduler, webhook service, dispatcher service, database, or polling loop.
