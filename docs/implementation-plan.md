# Implementation Plan

> Automation-owned working plan. Keep this synchronized with reality while respecting human-owned decisions.

## v0.2 implementation

The v0.2 redesign intentionally keeps GitKeepr small and bounded.

### Phase 1 — behavioral contract

- [x] explicit-only activation through exact trusted `/gitkeepr run` or manual dispatch;
- [x] remove automatic PR-open/synchronize/review/ordinary-comment activation;
- [x] default `GITKEEPR_FINALIZATION_CYCLES` to 2;
- [x] make Build operate as a finalizer and address all safely actionable remaining work in a turn;
- [x] replace transient/blocking status machine with `ready` and `needs-supervisor`;
- [x] make exhausted cycles a successful supervisor checkpoint;
- [x] add PR-HEAD ownership checks and `superseded` semantics;
- [x] preserve GitHub App credential refresh/retry and agent Git-boundary protections;
- [x] retire the external-helper/no-build/direct-reply protocol;
- [x] complete automated contract CI on the implementation PR;
- [x] dogfood the implementation PR on the VPS for explicit activation, two-cycle `needs-supervisor`, non-recursive Build pushes, and real `superseded` behavior.

Phase 1 is complete when those implementation contracts are green. The broader pre-release/rollout checklist in `docs/testing.md` is intentionally **not** a merge prerequisite for this implementation PR.

### Phase 2 — structural polish

After the behavioral contract is merged and stable:

- evaluate moving deterministic orchestration out of the monolithic YAML/Bash workflow into a small testable module;
- define a thin harness boundary so OpenCode can later be replaced by or coexist with Codex CLI/Pi without changing the v0.2 workflow contract;
- keep provisioning concerns separate from core finalization semantics where practical.

Do not begin Phase 2 by adding abstractions for hypothetical needs. Use the validated v0.2 behavior as the contract.

### Pre-release / rollout validation

Post-merge E2E on the real persistent VPS runner has verified the `ready` path, explicit command path, ordinary-comment suppression, duplicate-delivery idempotence, manual dispatch, bounded `needs-supervisor`, and `superseded` behavior.

Intentional provider/App-auth failure injection and a fresh post-merge fork PR remain optional validation gaps documented in `docs/testing.md`; neither is a known release blocker.

## Deliberate constraints

- GitHub Actions remains the control plane.
- GitHub PR/branch remains the shared durable source of truth.
- No custom queue/database/dispatcher/polling service.
- No generic verification-command framework.
- No global VPS concurrency lock without an observed problem.
- No automatic GitHub App creation/installation.
