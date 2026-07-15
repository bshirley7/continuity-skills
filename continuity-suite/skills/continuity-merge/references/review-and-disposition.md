# Review and Disposition

Read this reference before merge assessment and whenever human review evidence is recorded.

## Readiness review

Confirm the tested local head equals the remote branch and PR head, the PR base matches configuration, the diff is goal-focused, required artifacts are present, private state is absent, and every pre-human-review gate is current. Base freshness must follow repository policy and be evidenced.

## Assessment outcomes

- **Passed:** evidence is current and the draft PR is ready for human review. The goal may become `review-ready`.
- **Failed:** name each exact mismatch or missing gate. Keep the PR draft and route remediation without implying human approval.
- **Stale:** a source, commit, branch, plan, behavior, command, PR head, or base condition changed after evidence. Rerun the affected stages.

## Human dispositions

| Disposition | Meaning | Next path |
| --- | --- | --- |
| `approved` | Human review approves the current PR but merge has not been recorded | Remain `review-ready` |
| `changes-requested` | Human requests rework | Dispatch for explicit in-scope resume, or planning for changed scope |
| `merged` | Human merge occurred and merge evidence is supplied | Mark completed and report outcome |
| `closed` | Human closes delivery without merge | Cancel and preserve history |

Do not infer disposition from comments, check status, approval rules, or the existence of a merge commit. Record facts supplied or verified through the authorized workflow. In a signed-approval project, every disposition requires a trusted SSH receipt bound to the current plan and attempt; the signing key is selected and controlled by the human, never the agent.

## Rework examples

In scope: adjust the approved label order. Archive the attempt, invalidate downstream evidence, obtain explicit resume authorization, and retest. In a signed-approval project, record that authorization with the human's trusted SSH key.

Changed scope: add user-configurable layouts. Revise the plan, reassess risks and slices, and obtain fresh approval.

## Handoff checklist

- Assessment cites test record, heads, base, PR, diff, and artifacts.
- Blockers distinguish machine evidence from human action.
- Human identity, disposition, timestamp, PR, and merge commit when applicable are factual.
- The next skill and command match `workflow status`.
- No assessment or report performs the merge.
