# Default Project Goal Dispatch

At 10:00 PM America/Chicago, run `project-continuity-suite/bin/continuity --json portfolio due`. For each returned project, dispatch at most one goal that is approved, due, dependency-satisfied, unlocked, and preflight-compliant. Start different project tasks concurrently, but preserve one active code-changing goal per project. Never infer approval, bypass failed gates, or execute held work. Record task IDs and dispatch outcomes.
