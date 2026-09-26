# Knowledge and Tested Findings

This file records lessons that should not have to be rediscovered.

## Tested PoC baseline

The previous private proof-of-concept used:

- persistent Ubuntu ARM64 self-hosted runner;
- dedicated `github-runner` user;
- OpenCode installed in `~github-runner/.opencode/bin`;
- OpenCode provider authentication stored under the runner user;
- Build model `openai/gpt-5.6-luna`;
- Review model `openai/gpt-5.6-sol`;
- GitHub App mutations rather than the default Actions token;
- Build/Review loop with max cycles, no-progress protection, status labels, deterministic trigger keys, blocked UX, trusted discussion context, and direct-reply handling for comments that need no code change.

## v0.2 operational lessons

The v0.1.x history showed that most practical failures came from orchestration around otherwise useful Build/Review agents:

- automatic `synchronize` caused unrelated human/ChatGPT commits to start or queue work;
- ambient comment/review triggers required special direct-reply and status-preservation logic;
- no-progress detection had to distinguish changed findings on the same HEAD and created several state-machine edge cases;
- Copilot review identities/event delivery added trigger complexity without meaningful UX benefit;
- long loops increased token usage and exposed credential lifetime/finalization failures;
- transient labels could become stale after interrupted runs;
- external pushes could race a run that still believed it owned the previous HEAD.

v0.2 responds by using explicit activation, a default two-cycle budget, external supervision, durable result labels only, and optimistic PR-HEAD ownership.

A supervisor checkpoint is not a failure. `needs-supervisor` means the worker used its bounded budget and deliberately returned control to ChatGPT/human supervision.

## Important behavior learned from GitHub/Copilot

- A normal human `pull_request_review: submitted` event can trigger Actions.
- Real Copilot review did **not** reliably produce the repository `pull_request_review` workflow run expected by the PoC.
- `workflow_run` against Copilot's internal review workflow was not a useful trigger.
- Copilot inline-comment events can have separate approval/security behavior and are not the V1 automation path.
- Therefore GitKeepr does not depend on Copilot emitting a trigger. Copilot review is trusted discussion context and an explicit `/gitkeepr run` is the activation path.
- Copilot findings may be stale; agents must verify them against current HEAD before acting.

## Idempotence lesson

The PoC proved successful duplicate suppression by rerunning an already handled event and skipping checkout/model work.

A subtle PoC bug was identified: an AI review comment could receive the source-trigger processed marker even when the overall loop later failed/blocked. GitKeepr V1 must fix this: the source trigger is marked processed only when the loop successfully handles it. Blocked/failure comments use separate markers.

## Why persistent runners

Persistent runners keep OpenCode/provider auth and caches available across runs. Repository-level runners are used because the initial owner layout is a personal GitHub account rather than an organization-wide runner group.

## Why GitHub App mutations

The default Actions token is intentionally limited and Actions-originated activity has recursion/security semantics that were inconvenient for the tested loop. A dedicated App gives explicit, auditable permissions and a stable bot identity while leaving the top-level workflow token read-only where possible.

## Why no polling/custom dispatcher

The tested system can be driven by GitHub-native events plus ordinary human comments. Polling and a custom dispatcher were deliberately removed from the target architecture because they add state and operational burden without solving a current requirement.
