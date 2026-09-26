# Operations and Recovery

## Result semantics

- `gitkeepr:ready`: the bounded finalization run reached Review `PASS` for the current PR HEAD.
- `gitkeepr:needs-supervisor`: GitKeepr completed its configured cycle budget but Review still returned `CONTINUE`.
- `superseded`: another actor changed the PR HEAD while GitKeepr was working. The run exits without changing PR labels or publishing stale review output.
- Actions failure: infrastructure, harness, credential, invalid-output, or other technical failure. No persistent failure label is written.

Neither `ready` nor Review `PASS` means repository CI is green or that the PR should be merged without further supervision.

## Starting work

Normal PR activity does not start GitKeepr.

Use a trusted top-level PR comment containing exactly:

```
/gitkeepr run
```

or use the workflow's manual `workflow_dispatch` input.

A new command starts a new bounded finalization attempt. Ordinary comments and reviews remain available to the agents as context for the next run.

## Supervisor checkpoints

`needs-supervisor` is an expected state. A human or ChatGPT supervisor should inspect the current diff, GitKeepr review output, repository CI, and relevant PR discussion, then choose one of:

- fix the remaining issue directly;
- add clarifying context to the PR and start another `/gitkeepr run`;
- make a product decision that the worker must not invent;
- leave the PR for later.

A supervisor may also retry a technical Actions failure after repairing infrastructure or authentication.

## Superseded runs

A superseded run is not retried automatically. The newer PR HEAD is authoritative. Inspect that state first and explicitly start another run only when finalization is still useful.

This rule intentionally allows ChatGPT, the user, another coding tool, or another process to make several commits without racing a GitKeepr run.

## Common recovery

- OpenCode/provider authentication: rerun `opencode auth login` as `github-runner`.
- GitHub App key rotation: update the server key/configuration and rerun `gitkeepr runner add owner/repo`.
- Broken runner: rerun `runner add`; unhealthy existing installations can be reconfigured.
- Expired GitHub App installation token during a run: GitKeepr refreshes credentials and retries the credentialed push once.
- External branch update: allow the current run to finish as `superseded`, then decide whether to start a fresh run.

## Resource contention

There is no global VPS concurrency manager. Repository-level GitHub Actions concurrency serializes GitKeepr runs for the same PR. Add broader resource controls only after observing real contention.
