# Binding-Time Principle

**Type:** DESIGN PRINCIPLE — not code-enforced. No pass/fail gate in `core/contracts.py`. Informs contract authoring only.
**Applies to:** New contract design, permission grants, tool access decisions

## Principle

Failure *origin* and failure *manifestation* are often decoupled. A permission
grant made at session-start (dev/binding time) can surface as a runtime exploit
turns later. Shadow's current contracts are skewed toward runtime post-checks —
high false-positive pressure, low leverage.

The higher-leverage control placement is **binding time**: when tools and
permissions are granted, scoped, and logged, not when they are invoked.

## Design implications

1. **Prefer pre-checks over post-checks** when the failure class is about
   what is *possible* (permission scope), not what is *happening* (response behavior).

2. **Tag violation origin** — new contracts should set `origin_stage` on
   `Violation` to one of `dev` | `runtime` | `maintenance` so session_audit
   can distinguish systemic (binding-time) failures from transient noise.

3. **Session-start audit** — at the opening of each autonomous session, a
   `PermissionScopeContract` pre-check should enumerate active tool permissions
   and log any that exceed the declared task scope to `#shadow-log`.

## Origin

Derived from: *Securing Computer-Use Agents: A Unified Architecture-Lifecycle
Framework* (arXiv cs.CL, 2026). Treat as a taxonomy/design prompt, not an
empirical result — the paper lacks a deployed case study.

## Failure modes this addresses

- FM-015 (wrong target/scope on push or write)
- FM-017 (writes to dangerous paths — preventable at grant time, not just invocation)
- Any future FM where a runtime violation is actually a dev-time misconfiguration
