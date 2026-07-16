# Continuity Quickstart

This guide walks through a first local Continuity install: install into one project, keep execution disabled, configure project behavior, verify health, then use the installed skills and slash commands.

Use this path when you want Continuity available in a project without turning on unattended implementation yet.

## 1. Start From The Suite Checkout

Run installation from the Continuity suite checkout and point it at one target repository.

```text
cd /path/to/continuity-suite-checkout
python3 continuity-suite/installer/install.py \
  --project-root /path/to/project \
  --project-id example-project \
  --integration-branch main \
  --validation "pnpm typecheck"
```

Add more `--validation` flags for commands that should always be run before delivery:

```text
python3 continuity-suite/installer/install.py \
  --project-root /path/to/project \
  --project-id example-project \
  --integration-branch main \
  --validation "pnpm typecheck" \
  --validation "pnpm test"
```

For a project-only trial that ignores saved personal defaults, add `--ignore-user-defaults`.

Do not pass `--enable-execution` during the first local install. Do not pass `--require-signed-approvals` unless the project intentionally needs SSH-signed approval receipts.

## 2. Move Into The Project

After installation, daily use happens inside the project.

```text
cd /path/to/project
.agents/continuity/bin/continuity --project-root "$PWD" --json project doctor
.agents/continuity/bin/continuity --project-root "$PWD" workflow status
```

For the first local pass, the important result is:

```text
execution_enabled: false
```

With execution disabled, Continuity can capture notes, triage context, search memory, build plans, and record human approvals without requiring SSH trust setup, external audit checkpoints, or GitHub check names.

## 3. Configure Local Behavior

Ask Continuity what it recommends for this repository:

```text
.agents/continuity/bin/continuity --project-root "$PWD" --json project recommendations
```

For a guided setup, run:

```text
.agents/continuity/bin/continuity --project-root "$PWD" project configure --interactive --actor "your-name"
```

When the prompt asks whether to enable real product-code execution, answer `N`.

For a repeatable local configuration, save an answers file like this:

```json
{
  "validation_commands": ["pnpm typecheck"],
  "security_commands": [],
  "github_required_checks": [],
  "github_required_reviewers": 0,
  "github_cli_merge_enabled": false,
  "agent_surfaces": {
    "primary": "codex",
    "enabled": ["codex", "claude-code", "cursor"]
  },
  "scheduler": {
    "provider": "none"
  },
  "execution_enabled": false
}
```

Then apply it:

```text
.agents/continuity/bin/continuity \
  --project-root "$PWD" \
  --json project configure \
  --answers-file /path/to/continuity-local.json \
  --actor "your-name"
```

Run doctor again after configuration:

```text
.agents/continuity/bin/continuity --project-root "$PWD" --json project doctor
```

## 4. Use The Skills

Continuity installs canonical skills under `.agents/skills/` and project-specific behavior under `.agents/skills/continuity-local/SKILL.md`. Each task-specific skill applies that local behavior automatically.

In Codex, invoke the skills by name:

```text
$continuity
$continuity-capture
$continuity-triage
$continuity-memory
$continuity-roadmap
$continuity-plan
$continuity-dispatch
$continuity-execute
$continuity-test
$continuity-merge
$continuity-report
```

In slash-command hosts, use the generated shims:

```text
/continuity
/continuity-capture
/continuity-triage
/continuity-memory
/continuity-roadmap
/continuity-plan
/continuity-dispatch
/continuity-execute
/continuity-test
/continuity-merge
/continuity-report
```

The most common local flow is:

```text
/continuity-capture   capture meeting notes, feedback, a PRD, or a feature request
/continuity-triage    classify each captured item and route it
/continuity-memory    retrieve or promote trusted project knowledge
/continuity-roadmap   inspect roadmap context and links
/continuity-plan      draft a reviewable plan from selected current-goal inputs
/continuity-dispatch  record exact human approval or keep the goal awaiting feedback
/continuity-report    summarize status, blockers, and decisions needed
```

If slash commands are not available in the current host, ask the agent to use the matching `$continuity-*` skill or open the installed `SKILL.md` file directly.

## 5. Manually Trigger A Stage

Manual stage starts do not need a new skill. Use `workflow status` to identify the current stage and next allowed skill, then invoke that stage-specific slash command yourself.

```text
.agents/continuity/bin/continuity --project-root "$PWD" workflow status
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --note-id <note-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --goal-id <goal-id>
```

Use these manual triggers:

| When you want to run | Invoke | Notes |
| --- | --- | --- |
| Route the next Continuity action | `/continuity` | Reads project health and handoff state, then routes to the right workflow. |
| Capture new input | `/continuity-capture` | Creates private atomic notes from meetings, feedback, decisions, risks, PRDs, or feature requests. |
| Classify captured notes | `/continuity-triage` | Use after capture, or whenever `workflow status` lists triage as the next skill. |
| Retrieve project context | `/continuity-memory` | Use before planning or when trusted memory needs review or promotion. |
| Retrieve roadmap context | `/continuity-roadmap` | Use before planning or when a note should be linked to roadmap context. |
| Draft or revise a plan | `/continuity-plan` | Use only after selected notes and context are ready for a reviewable goal. |
| Approve, queue, or manually start a goal | `/continuity-dispatch` | Records human approval and scheduling decisions; manual start still requires every listed gate. |
| Execute an approved dispatched goal | `/continuity-execute` | Use only when `workflow status --goal-id <goal-id>` lists execution as allowed. Requires `execution_enabled: true`. |
| Run final validation and evidence capture | `/continuity-test` | Use after implementation, before merge readiness. |
| Assess PR and merge readiness | `/continuity-merge` | Use after final validation and a pushed PR. Human merge disposition is still separate. |
| Summarize state and decisions | `/continuity-report` | Use any time a status, blocker, or morning-style decision report is needed. |

The CLI is the state recorder and gatekeeper; the skills are the manual triggers for agent work. Do not add a generic "run next step" command that crosses approval, dispatch, execution, test, merge, or completion boundaries automatically.

## 6. Record A Local Approval

When `$continuity-plan` creates a goal that is ready for review, inspect the exact plan version and use the command shown by `workflow status`.

```text
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --goal-id <goal-id>
.agents/continuity/bin/continuity --project-root "$PWD" goal approve <goal-id> \
  --version <version> \
  --approved-by "Approving Human Name" \
  --authorization-text "Approve <goal-id> plan v<version>"
```

For local installs, approval needs a recorded human identity and exact authorization text. SSH signing is only required when `.continuity/config.json` has `require_signed_approvals: true`.

Approval does not start product-code execution while `execution_enabled` is `false`.

## 7. Work From The Machine Handoff

Use `workflow status` before and after each skill:

```text
.agents/continuity/bin/continuity --project-root "$PWD" workflow status
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --capture-id <capture-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --note-id <note-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --goal-id <goal-id>
```

Treat this output as the handoff. It lists the current stage, blockers, next skill, human requirements, and exact allowed command templates. Do not infer approval, dispatch, merge, or completion from conversation context alone.

For manual work, start with `$continuity-workflow` or `/continuity-workflow`. It follows the machine-selected skill sequence continuously, including remediation and reruns, and pauses only for an action explicitly marked `human_required`. Resume the same workflow after recording the approval; completed stages are discovered from canonical state and are not repeated.

## 8. Turn On Execution Later

Execution is a separate production-readiness step. Before setting `execution_enabled` to `true`, configure:

- exact hosted GitHub check names and reviewer requirements
- an external audit checkpoint and verified encrypted backup
- scheduler provider and registration, if scheduled work should run
- trusted SSH approvers only if the project requires signed approval receipts

Use [Production Pilot](production-pilot.md) for the controlled off-hours path. Keep local installs in analysis-and-planning mode until those requirements are intentionally in place.

## Troubleshooting

If doctor reports `execution is enabled but no required GitHub checks are configured`, the project is no longer in local-only mode. Set `execution_enabled` back to `false` or configure the exact hosted check names before enabling execution.

If doctor reports a missing external audit checkpoint, execution is enabled. Disable execution for local setup, or complete the production audit and backup flow.

If an approval asks for an SSH signing key, the project has `require_signed_approvals: true`. For a local-only project, make an explicit reviewed configuration change that sets `.continuity/config.json` `require_signed_approvals` to `false`. For a project that intentionally requires signed approvals, configure `.continuity/trusted-approvers` through protected human review.

If the online release check says `release not found`, local work can still continue when `project doctor` reports no managed-file drift and the installed suite manifest is healthy.
