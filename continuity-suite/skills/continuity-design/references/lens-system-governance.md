# Design-system governance

## Generalized principles

- Create an explicit publication boundary where proposed system changes have a named scope, rationale, owner, review state, version, release note, and effective audience before downstream consumers receive them.
- Document governed assets through canonical purpose, anatomy, properties, states, content limits, accessibility requirements, usage guidance, implementation linkage, ownership, and last-reviewed status.
- Separate contribution, review, approval, publication, administration, and consumption rights so authority is proportional to consequence and visible at the relevant scope.
- Treat deprecation as a lifecycle with announcement, affected scope, replacement, compatibility period, migration steps, deadline, support path, and final removal rather than a deleted asset.
- Place change and migration information both in durable release history and near affected assets so consumers can connect a system version to operational consequences.
- Make governance health inspectable through ownership, adoption, unresolved divergence, accessibility coverage, stale guidance, deprecated usage, and release status without treating usage volume as proof of quality.

## Variation levers

- Use lightweight review for low-risk documentation changes and stronger approval for semantic tokens, shared components, accessibility, or destructive migrations.
- Assign ownership by component domain while retaining system-wide publication standards.
- Support experimental, candidate, stable, deprecated, and retired lifecycle states.
- Publish release notes at both system and affected-asset levels.
- Allow bounded local exceptions with owner, rationale, expiry, and convergence plan.

## Tensions and tradeoffs

- Central control improves coherence while slowing domain teams.
- Broad contribution improves relevance while increasing review load.
- Backward compatibility protects consumers while prolonging inconsistency.
- Adoption metrics reveal reach while rewarding popular but poor patterns.
- Local exceptions accelerate delivery while becoming permanent forks.

## Failure modes

- Saving a library silently publishes it.
- Documentation lacks owner or review date.
- Approval authority is implied by workspace membership.
- Deprecated assets disappear without replacement or migration guidance.
- Release notes do not identify affected components or consumers.
- Exceptions have no expiry or convergence plan.
- Governance dashboards equate usage with correctness.

## Anti-patterns

- Unversioned shared library.
- Documentation as screenshots only.
- One owner for every domain.
- Publish rights for all contributors.
- Breaking rename without aliases or migration.
- Changelog detached from affected assets.
- Permanent experimental status.
- Exception registry with no accountability.
- Adoption leaderboard as quality score.

## Acceptance and review questions

- Does publication require explicit scope, rationale, owner, review state, version, release note, and audience?
- Does canonical documentation cover purpose, anatomy, properties, states, content, accessibility, usage, implementation, ownership, and review freshness?
- Are contribution, review, approval, publication, administration, and consumption rights distinct?
- Does deprecation preserve affected scope, replacement, compatibility, migration, deadline, support, and history?
- Can consumers find changes both in release history and beside affected assets?
- Are exceptions owned, bounded, reviewable, and time-limited?
- Are health signals interpreted as evidence rather than automatic proof of quality?
- Is guidance limited to visible governance mechanisms rather than claiming hidden organizational practice?
