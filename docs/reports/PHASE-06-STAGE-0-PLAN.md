# Phase 06 — Stage 0 Plan and Requirements Matrix

**Date:** 2026-08-14
**Base:** `86503b3930192dd46de7ce500384c246d236fcd4` (`origin/main`)
**Branch:** `arena/019fffa4-coachos-fitness-coaching-platf`
**Status:** Approved implementation in progress; this document is not a completion claim.

## Recovery record

The resumed checkout contained no interrupted changes: `HEAD` equaled the verified base, `git status --short --branch` showed only the branch header, and both `git diff --stat` and `git diff --check` were empty. No Phase 06 report, plan, domain app, migration, test, or frontend Stage 7 artifact existed locally or remotely. Consequently, there was no diff to preserve or safely recover. Work proceeds from the verified base on the Arena-fixed branch rather than pretending that Gates 1–7 already passed.

## Scope boundary

Included only:

- bilingual (`fa-IR`, `en-US`) exercise definitions, translations, aliases, filters, and Persian keyboard-variant-normalized search;
- mandatory media rights/provenance metadata and platform-admin API moderation;
- organization-scoped program hierarchy, prescriptions, templates/cloning, version increments, coach-athlete authorization, and immutable assignment snapshots;
- coach/owner exercise and program-builder UI.

Excluded: workout execution, set actual logging, rest timers, pain/fatigue, durable offline sync, messaging, nutrition, billing, marketplace, AI, wearables, and every Phase 07+ domain. Arabic localization is prohibited. Program assignment creates no `WorkoutSession` or execution record.

## Sequential gates

| Gate | Deliverable / acceptance evidence | Initial state |
|---|---|---|
| 0 | Recovery inspection, scope, requirements matrix, implementation plan | In progress |
| 1 | Exercise domain models, constraints, migration, model tests | Not run |
| 2 | Bilingual translations/aliases, normalized search and filters, tests | Not run |
| 3 | Media asset rights/provenance validation and moderation API, tests | Not run |
| 4 | Program hierarchy and prescription persistence, atomic API, tests | Not run |
| 5 | Template clone, versioning, immutable snapshot serialization, tests | Not run |
| 6 | Authentication, role authorization, tenant isolation, assignment policy, API query bounds | Not run |
| 7 | Coach/owner frontend, dictionaries, RTL/LTR, accessibility tests, lint/type/test/build | Not run |
| 8 | Adversarial security/authz/tenant/media/query/localization/accessibility review | Not started |
| 9 | Clean-checkout-equivalent full validation, report/tracking docs, commit/push/PR/checks | Not started |

A later gate may not be marked passed solely because this table says so; command output and test artifacts are required.

## Requirements traceability matrix

| Requirement | Source | Planned artifacts | Verification |
|---|---|---|---|
| REQ-I18N-002 keyboard variants (`ي/ی`, `ك/ک`) | PRD US-I18N-002, ADR-018 | normalized translation and alias fields; shared normalizer | exact/alias search tests; locale parity scan |
| REQ-EX-001 bilingual catalog and filters | PRD US-EX-001 | Exercise, ExerciseTranslation, ExerciseAlias; list/detail API | canonical + tenant visibility/filter/query tests |
| REQ-EX-002 private exercise + provenance | PRD US-EX-002 | MediaAsset + one-to-one MediaRights; atomic create | missing/invalid rights rejected; tenant isolation tests |
| REQ-EX-003 moderation | PRD US-EX-003 | platform-admin queue/decision API; rights review checks | non-admin denied; unsafe publication rejected |
| REQ-PRG-001 hierarchy/prescriptions | PRD US-PRG-001 | Program → phase → week → day → workout → item → set | atomic nested create/detail tests; ordering constraints |
| REQ-PRG-002 reusable templates | PRD US-PRG-002 | deep clone service/API | independent-copy mutation test |
| REQ-PRG-003 assignment snapshot | PRD US-PRG-003, ADR-015 | assignment + frozen JSON payload + source version | source edit does not mutate snapshot; immutability test |
| Tenant/RBAC controls | Authorization architecture | active membership and owner/coach policies; coach-athlete link | cross-tenant, athlete, suspended, unassigned coach negative tests |
| Coach/owner UI | Phase 06 scope guard, UX specs | catalog search/filter and keyboard-usable dual-pane builder | component, RTL/LTR, dictionary, a11y target tests |

## Design decisions for this implementation

1. PostgreSQL remains the production target; JSON arrays are used for portable structured tags in CI's SQLite test database. Normalized indexed text fields make deterministic keyboard-variant matching testable without implying Arabic locale support.
2. API callers supply `org_id`; every organization-owned queryset is additionally intersected with active server-side membership. Header tenancy never grants access.
3. Canonical exercises are readable by active organization members; private exercises are readable only inside their organization. Coaches/owners may create private exercises. Athlete mutation is denied.
4. Every media asset must have exactly one rights record. Publication requires commercial-use permission and review metadata. No public object URL or signed URL generation is introduced.
5. Nested program create and clone are atomic. Uniqueness constraints preserve sibling ordering. Updates increment `version`.
6. Snapshot payloads are generated server-side from ordered relations, stored on assignment, and cannot be modified through model `save()` after creation. Assignment does not implement Phase 07 scheduling/execution.
7. Owner can assign to any active athlete in the tenant. Coach requires an active `CoachAthleteAssignment` in that tenant.
8. Frontend Phase 06 is a coach/owner workspace only and does not add athlete execution behavior or durable offline persistence.
