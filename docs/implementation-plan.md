# Implementation Plan

> Automation-owned working plan. Keep this synchronized with reality while respecting human-owned decisions.

## v0.2 implementation

The v0.2 redesign intentionally keeps GitKeepr small and bounded.

### Phase 1 — behavioral contract

- [x] explicit-only activation through exact trusted `/gitkeepr run` or manual dispatch;
- [x] remove automatic PR-open/synchronize/review/ordinary-comment activation;
- [x] default `GITKEEPR_MAX_CYCLES` to 2;
- [x] make Build operate as a finalizer and address all safely actionable remaining work in a turn;
- [x] replace transient/blocking status machine with `ready` and `needs-supervisor`;
- [x] make exhausted cycles a successful supervisor checkpoint;
- [x] add PR-HEAD ownership checks and `superseded` semantics;
- [x] preserve GitHub App credential refresh/retry and agent Git-boundary protections;
- [x] retire the external-helper/no-build/direct-reply protocol;
- [ ] complete automated contract CI on the implementation PR;
- [ ] complete live v0.2 smoke validation on the VPS.

### Phase 2 — structural polish

After the behavioral contract is validated:

- evaluate moving deterministic orchestration out of the monolithic YAML/Bash workflow into a small testable module;
- define a thin harness boundary so OpenCode can later be replaced by or coexist with Codex CLI/Pi without changing the v0.2 workflow contract;
- keep provisioning concerns separate from core finalization semantics where practical.

Do not begin Phase 2 by adding abstractions for hypothetical needs. Use the validated v0.2 behavior as the contract.

## Deliberate constraints

- GitHub Actions remains the control plane.
- GitHub PR/branch remains the shared durable source of truth.
- No custom queue/database/dispatcher/polling service.
- No generic verification-command framework.
- No global VPS concurrency lock without an observed problem.
- No automatic GitHub App creation/installation.
