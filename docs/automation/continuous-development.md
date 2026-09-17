# Continuous Bootstrap Development

> Automation-owned working instructions. This file may be improved by the scheduled developer. It must not override the human-owned goal, architecture, security model, or approved decisions.

## Purpose

During the temporary bootstrap period, a ChatGPT Scheduled task runs once per hour and continues improving this repository directly on `main`.

The task is a development helper, not a product feature. It may eventually be disabled permanently.

## Required behavior for every run

1. Read the human-owned source-of-truth documents first:
   - `docs/goal.md`
   - `docs/architecture.md`
   - `docs/decisions.md`
   - `docs/security.md`
2. Read the current implementation and automation-owned planning/testing notes.
3. Inspect the current state before deciding what to change.
4. Choose one focused, high-value iteration.
5. Prefer correctness, security, tests, documentation, deletion, and simplification over adding abstractions.
6. Do not invent new product requirements.
7. Do not change approved scope merely because another design seems interesting.
8. Verify the change with the best available local/repository checks.
9. Commit useful changes directly to `main`.
10. Update automation-owned notes when that meaningfully improves continuity between runs.

## Persistence

This file, `docs/implementation-plan.md`, `docs/known-issues.md`, and `docs/testing.md` are the persistent working memory between scheduled runs. Keep them useful and concise; do not turn them into a diary.

## When the project looks complete

Do not permanently stop just because one or several runs return PASS/no-change. Each hourly run should independently look for:

- correctness bugs;
- security gaps;
- divergence from approved docs;
- incomplete setup/recovery paths;
- missing tests;
- confusing UX;
- unnecessary complexity;
- opportunities to simplify without changing requirements.

A valid run may still conclude that no justified repository change exists. Do not create work merely to make a commit.

## Hard boundaries

- Frequency remains once per hour; do not attempt to modify it.
- Do not weaken fork/self-hosted-runner boundaries.
- Do not introduce polling, a custom dispatcher, a database, or a queue unless a human changes the product decision.
- Do not turn the simple shell CLI into a framework without an observed need.
