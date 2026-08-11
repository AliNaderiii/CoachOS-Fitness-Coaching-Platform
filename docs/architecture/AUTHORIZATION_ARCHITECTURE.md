# Authorization Architecture — CoachOS

**Version:** 1.0.0 Phase 03  
**Status:** Proposed / Accepted as direction (ADR-006 RBAC+ABAC accepted)  
**Pattern:** Two-tier — RBAC (Organization role) + Object-level ABAC (CoachAthleteAssignment + Consent + Organization scope)

---

## 1. Principles

1. **Server-side enforcement 100%** — client route guards are cosmetic only.
2. **Tenant isolation mandatory:** Every tenant-scoped query filters via `organization_id` derived from authenticated server context (`request.org_id` via OrgScopeMiddleware), never trusting client-supplied params alone.
3. **UUIDv7 not authorization:** Non-guessable IDs do not replace checks.
4. **Cross-tenant obscurity:** Return 404 Not Found preferred over 403 when resource belongs to other tenant, to avoid enumeration; 403 when explicitly assigned but suspended or consent missing.
5. **Least privilege:** Owner does NOT automatically get raw progress photos or private messages — requires consent or audited escalation.
6. **Break-glass admin:** Platform admin reads of Tier3/4 sensitive data require MFA + audit + documented reason; not routine.

---

## 2. RBAC Roles (P0)

| Role | Code | Scope Level | Membership Status Required | Description |
|------|------|-------------|----------------------------|-------------|
| Platform Admin | `platform_admin` | Global | `is_platform_admin=true` + MFA | Moderates global catalog, manages tenants, reads global audit, suspends users — all actions audited |
| Organization Owner | `owner` | Org tenant | Membership `active` + role owner | Creates org, manages members, invites coach/athlete, reassigns, reads org audit, reads aggregate progress but not raw photos without consent |
| Coach | `coach` | Org tenant | Membership `active` + role coach | Creates programs, templates, assigns to assigned athletes only, reads assigned athlete logs/photos with consent, messages assigned athletes |
| Athlete | `athlete` | Org tenant | Membership `active` + role athlete | Self-access only: own today view, own sessions, own set logs, own progress photos, own messages; cannot read other athletes |
| Support Staff (optional) | `support` | Org tenant | Membership `active` role support | Read-only assistance — can read org member list, read aggregate logs? DENIED for Tier4 photos and private messages |

**Future P1:** Nutrition Professional `nutritionist` — consent-gated via `ConsentRecord` type `nutrition_sharing`.

---

## 3. Organization Boundaries & Active Context

- User may belong to multiple organizations (multiple Membership rows). Session holds `active_organization_id` switchable via org picker.
- Middleware sets `request.org_id` from active membership.
- Every tenant-scoped queryset must use `for_org(request.org_id)` helper which adds `WHERE organization_id = :org_id`.
- Attempt to request resource with different org's ID → return 404/403 (never leak existence).
- Invitation flow: creating invitation requires Owner or Coach (Coach can invite athlete only). Invitation token hash stored, expiry 7 days.

---

## 4. Object-Level Assignment Rules (ABAC)

### 4.1 Coach-Athlete Assignment (`CoachAthleteAssignment` active)
- Coach can CREATE/READ/UPDATE programs assigned? Can READ athlete if assignment active.
- Athlete can READ own data only.
- Owner can READ assignment list, can create/revoke assignments, can reassign athlete to different coach.
- Assignment must be within same organization — cross-org assignment creation fails 400.

### 4.2 Program & Template
- **Create:** Owner, Coach within org.
- **Read Templates:** Owner, Coach of same org (org-private templates). Global canonical templates? Actually canonical = platform-published exercises, but programs are org-private — Owner/Coach only.
- **Read Assigned Snapshots:** Athlete can read only snapshots bound to own ProgramAssignment.
- **Assign to Athlete:** Owner any org athlete, Coach only assigned athletes (check ABAC).
- **Snapshot:** Auto-created immutable on assignment; athlete reads bound version; coach cannot mutate historical snapshot.

### 4.3 Workout Logs & Actuals
- **Create/log set:** Athlete self primary; Coach proxy log allowed? Proposed yes but flagged `logged_by=coach` for audit; Owner cannot log sets for athlete.
- **Read logs:** Athlete own logs only; Coach only assigned athlete logs; Owner own org athletes logs (aggregate operational allowed) but with audit? Owner reading individual set logs allowed? Proposed: Owner can read own org athletes logs for operational reporting (not Tier3/4 sensitive raw photos/pain details? set logs are Tier2 operational, so Owner allowed). Platform admin audited.
- **Sensitive health (FeedbackFlag, BodyMetric):** Assigned Coach only + Athlete self; Owner aggregate (average RPE, flagged count) but not raw individual pain details — raw requires audited escalation. Support DENIED.

### 4.4 Progress Media & Photos
- **Upload:** Athlete only own photos + must have consent record? Actually consent modal before upload for coach view. Photo upload blocked until consent logged (UI mandatory but backend also enforces ConsentRecord existence).
- **View photo:** Athlete self; Assigned Coach only if explicit consent active; Owner denied unless explicit consent granted via same ConsentRecord + audited escalation; Platform admin strict audited escalation + documented reason; Support DENIED zero access.
- **Revoke:** Athlete can revoke consent at any time via Profile → Privacy → immediate effect invalidates signed URLs + blocks further queries.

### 4.5 Messages & Threads
- **Send:** Athlete ↔ assigned Coach + Owner? Owner can message staff and athletes? Proposed yes but within org.
- **Read threads:** Only participants (sender/recipient) + Owner escalation audited? For P0, owner escalation not allowed to read private 1:1 athlete-coach threads without audited reason — to preserve trust. So default: Assigned threads only; Owner admin escalation only with audit (break-glass). Support DENIED.
- **Cross-tenant message:** 404.

### 4.6 Exercise Library
- **Create canonical:** Platform admin direct publish.
- **Create private custom:** Owner, Coach org-private.
- **Read catalog:** All authenticated — canonical + org-private.
- **Moderate/Approve:** Platform admin full authority + audit.
- **Archive:** Org private only org members; canonical only admin.

---

## 5. Sensitive Resource Access Matrix (Detailed)

| Resource | Create Who | Read Who | Update Who | Archive/Delete Who | Export Who | Share | Revoke Access | Consent Required? | Audited? |
|----------|------------|----------|------------|--------------------|------------|-------|---------------|-------------------|----------|
| User/Profile | Self (register) + Invite | Self + Org members limited + Assigned Coach/Athlete + Admin audited | Self only (admin can suspend) | Self erasure request + Admin execute | Self (privacy export) | No | Owner can suspend membership | No (self) | Yes auth changes |
| Organization Settings | Owner, Admin | Owner, Coach limited, Athlete branding only, Support read, Admin all | Owner, Admin audited | Owner, Admin audited | Owner? aggregate export? | No | Owner suspend | No | Yes |
| Location primary | Owner, Admin | All org members read-only | Owner, Admin | None MVP — archive via org archive | Owner aggregate | No | — | No | Yes location_updated |
| Invitation | Owner (coach/athlete), Coach (athlete only), Admin all | Owner sees org invites, Coach sees own sent? Athlete sees own? | N/A (single-use) | Owner/Admin can revoke (mark revoked) | No | No | Creator can revoke before acceptance | No | Yes sent/accepted/revoked |
| Membership | Via invitation acceptance + Owner direct? | Owner sees org roster, self sees own | Owner can suspend active→suspended, Admin any | Soft archive via suspended | Owner aggregate? | No | Owner suspend | No | Yes status_changed |
| CoachAthleteAssignment | Owner, Coach? (Owner any, Coach self-assignment?? Proposal: Owner any athlete to coach, Coach can assign self to athlete if org? Actually coach can be auto assigned when they invite athlete) | Owner sees all, Coach sees own assigned athletes, Athlete sees assigned coaches | Owner can reassign, Coach can? No, only Owner reassign prefer — avoid coach stealing athlete | Archive via status | Owner can export assignment list | No | Owner archive | No but assignment is authz basis | Yes |
| Exercise canonical | Admin | All authenticated | Admin only | Admin audited archive | Admin export? | No | — | No | Yes publish |
| Exercise private custom | Owner, Coach org scope | Org members only (Owner, Coach, Athlete of org) | Authoring org Coach/Owner | Author org private only | No | No private outside org | — | No | Yes created |
| Program / Template | Owner, Coach org scope | Owner, Coach org templates; Athlete assigned snapshot only | Author + Owner? Coach owner of template | Author + Owner soft archive | Owner aggregate? | Clone only within org | N/A | No | Yes created/updated |
| ProgramAssignment + Snapshot | Owner any org athlete, Coach assigned athletes only | Athlete self snapshot, Coach assigned athlete assignment, Owner org assignments | No update to snapshot immutable — only status archived/completed via new version? | Archive status | Owner athlete aggregated? | No | Owner/Coach can archive assignment | No | Yes assigned |
| WorkoutSession | System creates scheduled sessions from assignment; athlete starts session | Athlete self, Assigned Coach, Owner org operational, Admin audited | Athlete self in_progress → completed, Coach proxy? | No delete — archive via parent assignment | Self + Owner aggregate + Coach assigned | No | — | No | Yes session completed |
| SetLog | Athlete self (primary) + Coach proxy flagged | Athlete self, Assigned Coach, Owner org | Athlete can update own uncompleted session set? Proposed allow before session complete | No delete | Self + Owner aggregate + Coach assigned export | No | — | No | Yes? Maybe not audit each set, but session completion audit includes volume |
| FeedbackFlag (pain/fatigue) | Athlete self | Athlete self, Assigned Coach only, Owner aggregate count not raw, Support read? Support read flags summary? Actually Support read flags allowed per PRD table Read Flags but not raw photos — propose Support can read flag type/severity but not private notes? Conservative: Support can read but not private notes. Admin audited | Coach can resolve is_resolved flag | Archive? No — resolved status | Athlete self + Coach assigned + Owner aggregate | Share with coach auto via notification | Athlete cannot revoke flag itself but coach resolves | No (self) but marked as subjective | Yes flagged |
| BodyMetric | Athlete self | Athlete self, Assigned Coach with consent? For MVP weight metric is Tier3? Actually body weight is Tier3 sensitive — require consent similar to photos? Proposal: Assigned Coach with consent for weight? But PRD says pain flags coach only, and progress photos consent. Body metrics maybe also consent? Let's set consent required for body metrics in P0 for consistency — Owner aggregate only. | Athlete self | Athlete can delete own? via erasure | Self + Coach assigned (with consent) | No | Athlete revoke | Yes photo-type consent or body_metrics consent | Yes body_metric.read audited for coach? |
| ProgressPhoto | Athlete self + consent pre-grant | Athlete self, Assigned Coach with active consent, Owner only with consent + audited escalation, Admin audited escalation, Support DENIED | Athlete can archive own? Actually delete via erasure | Athlete self via delete? Propose allow delete own photo; else erasure pipeline deletes all | Self + consent grantee? Actually export includes photo metadata? Proposed export includes photo files via ZIP? Yes private export includes own photos only | Share via consent grant/revoke | Athlete revoke consent immediate | Yes explicit affirmative | Yes photo.viewed audited |
| Message Thread/Message | Assigned Coach, Athlete, Owner? Owner can message staff/athletes | Participants only + Owner escalation audited, Admin audited escalation only, Support DENIED | No update to content immutable? Allow edit window? Proposed no edit for P0 — immutable | No delete — archive thread? | Participants can export own? Privacy export includes messages? Proposed yes own messages included | No external share | N/A | No | Yes if admin escalation read |
| Notification | System creates | Recipient self only | Recipient marks read | No delete — read_at | No | No | — | No | No |
| NotificationPreference | User self | Self only | Self only | Self | No | No | — | No | No |
| AuditEvent | System/Service only | Platform Admin global, Owner own org tenant only (tenant-scoped), Coach/ Athlete none, Support org read? Support org audit read per PRD yes Org Read | STRICTLY FORBIDDEN immutable — no update/delete by any app role; DB-level REVOKE | FORBIDDEN | Admin global export, Owner org export via? Owner can export org audit? Proposed yes Owner can export own org audit trail | No | — | No but audit of sensitive reads | Self immutable |
| ExportRequest | Athlete self (or any user self) | Requestor self + Admin? Admin can see? Actually export is self only | System updates status | No delete — retention until expiry | Self via email link | No | — | No (self) | Yes export_requested/completed |
| ErasureRequest | Athlete self with password confirm | Requestor self + Admin audit | System | Retention until completed | Via anonymization | No | — | N/A | Yes erasure |

---

## 6. Organization Owner Visibility Distinction (Important)

Per NFR and PRD:

- **Aggregate Organization Analytics:** Owner can view counts: number athletes, weekly active, adherence percentages, volume aggregates, flagged counts — without seeing raw personal notes or photos.
- **Individual Operational Data:** Owner can view individual athlete scheduled workouts, completion status, set counts, adherence dates, but not raw pain details beyond severity type? Actually spec says Owner own org athletes aggregate/audit — for pain flags, Owner aggregate/audit per PRD. So Owner sees existence of pain flags but not detailed private notes without audited escalation.
- **Sensitive Health-Adjacent:** FeedbackFlag details, BodyMetric values, ProgressPhoto image bytes — Owner only with explicit athlete consent + audited escalation.
- **Progress Media:** Owner only if explicit consent + audit; otherwise DENIED.
- **Private Messages:** Owner only via audited escalation break-glass.
- **Reason:** Protect athlete trust, prevent gym owner overreach, comply with privacy-by-design.

Do NOT grant Owner automatic access to every raw personal health record or progress photo — explicit rule.

---

## 7. Platform-Admin Break-Glass Access

- Admin normally can see global organizations directory, user directory, exercise moderation queue, audit logs.
- For Tier3/4 sensitive reads (progress photo, message content, body metrics, pain flag details), admin must:
  1. Provide `is_platform_admin=true` + MFA verified session.
  2. Supply documented reason parameter (e.g., abuse report, copyright takedown).
  3. System logs `admin.break_glass_access` AuditEvent with actor, target, reason, IP hash.
  4. If possible, notify athlete? Proposal deferred pending legal review — at least audit.
- Admin cannot mutate AuditEvent, cannot delete export/erasure requests arbitrarily? Can execute erasure per request.

---

## 8. P1 Nutritionist Consent Access (Future)

- NutritionProfessional assignment requires explicit athlete consent via `ConsentRecord` type `nutrition_sharing`.
- Consent grant allows Nutritionist to read: training schedule (WorkoutSessions without? Actually training context allowed), body metrics, meal plans (P1), but NOT progress photos unless separate consent type `progress_photo` also granted to Nutritionist.
- Revocation immediate — blocks future reads, invalidates signed URLs if applicable (photos).
- Owner does not bypass consent.

---

## 9. Role Suspension Behavior

- Membership status `suspended` immediate effect:
  - All org-scoped API calls with `request.org_id` equal to suspended org return 403 Forbidden.
  - `CoachAthleteAssignment` linked? Proposed when coach suspended, assignments status becomes `archived` automatically via signal; athlete still belongs to org but needs new coach; sessions previously logged preserved but new logs blocked? Athlete membership not suspended — athlete still active but unassigned coach? Edge handling: if suspended coach, athlete assignment archived, owner notified to reassign.
  - Athlete suspended: cannot log sets, cannot access today, but existing historical data retained? Proposed retain but block further actions until unsuspended.
  - Login still allowed but org context blocked? Actually `is_active` User vs Membership status distinction: User is_active global blocks login; Membership suspended blocks org access only.
- Audit log records suspension with actor and reason.

---

## 10. Invitation Permissions

- Owner can invite: Coach, Athlete, Support (optional).
- Coach can invite: Athlete only (cannot invite other coaches or owners).
- Athlete cannot invite.
- Support can resend invitation? Per PRD, Support can resend only — but cannot create new.
- Invitation email uniqueness not enforced across orgs? Same email can have memberships in multiple orgs.
- Token: crypto random 32+ bytes, URL-safe base64, hash SHA256 stored, expiry 7 days, single-use.

---

## 11. API Permission Enforcement Points (DRF)

- `TenantScopedPermission` — checks `request.org_id` present + membership active.
- `RolePermission` — checks role in `['owner','coach','athlete','support','platform_admin']` per endpoint.
- `CoachAssignmentPermission` — for athlete data endpoints, verifies active `CoachAthleteAssignment`.
- `ConsentPermission` — for photo/body metric endpoints, verifies active `ConsentRecord`.
- `BreakGlassPermission` — for admin sensitive reads, checks MFA + logs audit.

Example DRF permission chain for `GET /api/v1/athletes/{id}/progress-photos`:
```
IsAuthenticated + TenantScopedPermission + 
( IsPlatformAdminBreakGlass OR (IsCoach AND CoachAssignmentPermission AND ConsentPermission) OR IsOwnerWithConsentAudited OR IsSelfAthlete ) + 
NOT Support
```

---

## 12. Negative Authorization Controls (Mandatory Tests)

Must have automated tests proving 403/404:

- Cross-tenant reads: coach of OrgA tries GET /api/v1/organizations/OrgB/members → 404/403
- Cross-tenant writes: coach of OrgA tries POST /api/v1/organizations/OrgB/programs → 403
- Unassigned coach access: Coach David not assigned to Athlete Neda tries GET Neda's sessions → 403
- Suspended membership: suspended coach calls any org-scoped endpoint → 403
- Unauthorized progress-photo access: Coach David unassigned tries GET Neda's photo → 403 + no signed URL generated
- Unauthorized message access: Coach David tries GET private thread between Sarah and Neda → 403
- Unauthorized audit-log access: Coach or Athlete GET /api/v1/organizations/{org}/audit-logs → 403, Owner can GET own org only, Admin global ok
- Unauthorized export/deletion: User A tries POST /api/v1/privacy/export-request for User B → 403 (only self), or GET another user's export result → 403

All tests mapped in `SECURITY_CONTROL_MATRIX.md` and `THREAT_MODEL.md`.

---

## 13. Data Classification Mapping

- Public metadata Tier0: Exercise canonical name, movement pattern, equipment taxonomy — open.
- Account Tier1: User, Organization, Membership — self + owner + admin.
- Operational Tier2: Programs, sessions, set logs — tenant + assignment.
- Sensitive health-adjacent Tier3: FeedbackFlag, BodyMetric — assignment + consent + audited.
- Progress media Tier4: Photo storage keys + signed URLs — consent + assignment + audited; NEVER public.
- Messages Tier2+ confidential — participants + audited escalation.
- Audit Tier5 immutable — admin + owner own org.
- Secrets Tier6 never in repo.

---

## 14. Logging Restrictions

- Debug logs must NOT contain: password_hash, raw email PII? Actually email is PII but needed for debugging? Propose redact or hash partially; health metrics, photo storage keys, message content, full JWT.
- Instead log: actor_id, organization_id, target_entity_type/id, action, timestamp, request_id.
- Audit logs contain ip_hash not raw IP.

---

## 15. Appendices — Permission Matrix Summary (condensed)

Same as PRD §6 permissions matrix but now explicit with consent and break-glass.

---

## 16. References

- `docs/PRD.md` §6 Permissions Matrix
- `docs/SECURITY_AND_PRIVACY.md` Data Classification
- `docs/DECISIONS.md` ADR-006, ADR-020, ADR-027
- `DOMAIN_MODULES.md`, `THREAT_MODEL.md`, `SECURITY_CONTROL_MATRIX.md`
