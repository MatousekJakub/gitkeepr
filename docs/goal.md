# Product Goal

> Human-owned source of truth. Automation may clarify factual details, but must not change the approved goal or scope without an explicit human instruction.

GitKeepr should provide a small, reliable bridge between a ChatGPT-led development workflow and agents that can work inside the real project environment.

## v0.2 goal

A user should be able to:

- prepare one Ubuntu/Debian VPS with `gitkeepr server init`;
- configure a private GitHub repository and persistent runner;
- let ChatGPT/user perform most planning and implementation through the normal PR;
- explicitly request bounded finalization with `/gitkeepr run`;
- let Build and independent Review use shell, tests, repository context, and optional MCP/browser tools;
- stop after a small configured budget instead of trying to converge indefinitely;
- treat unresolved work as a normal supervisor checkpoint;
- allow external actors to update the PR without GitKeepr racing or overwriting them;
- recover from failures without a custom database, dispatcher, or hidden orchestration state.

## Design values

- ChatGPT/user orchestration is primary; GitKeepr supplies missing real-environment capabilities.
- GitHub PR/branch is the durable shared source of truth.
- Prefer explicit activation over ambient event-driven automation.
- Prefer short bounded work over long autonomous loops.
- Prefer GitHub-native mechanisms over custom queues, databases, webhooks, or polling services.
- Separate agent reasoning from workflow-owned Git/GitHub mutations.
- Do not create abstractions without an observed need.
- It is valid to delete or simplify code instead of adding features.
- AI `PASS` is not CI success or merge approval.

## Explicit non-goals

- No Issue -> plan -> approval -> PR workflow.
- No attempt to make GitKeepr the user's main UX or primary orchestrator.
- No automatic reaction to every PR push, comment, or review.
- No global VPS concurrency manager.
- No generic deterministic verification framework beyond project CI and agent-selected relevant tests.
- No standard persistent-runner setup for arbitrary public target repositories.
- No automated creation or installation of the GitHub App.
- No custom scheduler, webhook service, dispatcher service, database, or polling loop.
