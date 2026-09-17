# External Helpers

External helpers are optional, non-invasive supplements. They are not part of GitKeepr core and GitKeepr does not depend on them.

The first documented helper is ChatGPT Chat Scheduled tasks, but the protocol is intentionally generic. In the intended model the helper acts through the user's GitHub identity, so GitKeepr sees its interaction as a normal trusted human comment.

## Waiting-human review

A helper may inspect PRs in `gitkeepr:waiting-human` as a substitute/supplement for human review.

A scheduled run should focus on **one PR only** for quality.

Priority:

1. `waiting-human` PR where a new Copilot review appeared after the helper's last review of the same HEAD;
2. `waiting-human` PR not yet reviewed by that helper on the current HEAD;
3. among equivalent candidates, the oldest waiting candidate.

The helper reads the current diff, CI, GitKeepr review, human discussion, and Copilot review/inline comments, and verifies stale findings against current HEAD.

If there are no actionable findings, post a top-level PR comment with:

- a concise PASS/review result;
- `<!-- gitkeepr-external-review:v1 source=<source> head=<sha> -->`;
- `<!-- gitkeepr:no-build -->`.

If actionable findings exist, post one top-level comment containing the relevant findings plus the external-review marker, **without** `gitkeepr:no-build`. That trusted comment starts the normal Build loop.

Normally a helper reviews one HEAD once. Exception: if a newer Copilot review for the same HEAD appears after the helper's last review, it may review the same HEAD again.

## Blocked PRs

Only when there is no higher-priority `waiting-human` candidate, a helper may inspect a `gitkeepr:blocked` PR.

It may attempt an initial unblock if the available context supports a safe, concrete action. It must not invent missing product decisions. If the block requires human input, it may leave a top-level explanatory comment with external-review + no-build markers so the same unchanged situation is not reprocessed every hour.

A new relevant input (human comment, new commit, or new Copilot review) can justify re-evaluation.
