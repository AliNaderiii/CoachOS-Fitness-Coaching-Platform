# API Contract — CoachOS

**Status:** Strategy outline (Phase 00). Detailed OpenAPI in Phase 03–05+.  
**Last updated:** 2026-08-10  

---

## 1. API principles

1. **API-first** — web, future native, and integrations use the same HTTP API  
2. **Versioned** — prefix `/api/v1/`  
3. **JSON** request/response unless media upload  
4. **Auth** required except health, open docs (if exposed), and auth endpoints  
5. **Errors** — consistent problem shape; **no sensitive leakage**; i18n-ready error codes  
6. **Idempotency** — for invites accept, payment webhooks (later), client retries on logs  
7. **Pagination** — cursor or limit/offset standardized  
8. **Tenant context** — derived from auth session/token + membership, not client trust alone  

## 2. Error envelope (draft)

```json
{
  "error": {
    "code": "permission_denied",
    "message_key": "errors.permission_denied",
    "details": {}
  }
}
```

- Clients localize `message_key` via fa/en resources  
- Servers may include a fallback `message` in the requester’s preferred locale only if carefully reviewed  
- Never hardcode only English in clients  

## 3. Auth endpoints (draft)

| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/v1/auth/register` | Email registration |
| POST | `/api/v1/auth/login` | Session or token pair |
| POST | `/api/v1/auth/logout` | Invalidate |
| POST | `/api/v1/auth/password/reset-request` | Rate limited |
| POST | `/api/v1/auth/password/reset-confirm` | Tokenized |
| GET | `/api/v1/me` | Profile + locale + memberships |

Exact session-vs-JWT choice: Phase 03/05 ADR.

## 4. Resource groups (P0)

| Group | Examples |
|-------|----------|
| Organizations | CRUD subset, members, invitations |
| Exercises | Search, filter, favorites, coach private CRUD, admin moderate |
| Programs | Builder tree, templates, versions, assign |
| Athlete training | Today, calendar, sessions, set logs |
| Messages | Threads, messages |
| Notifications | List, mark read, preferences |
| Admin | Users/orgs moderation, audit query |
| Health | `/health` `/ready` liveness/readiness |

## 5. Authorization contract

Every handler must:

1. Authenticate  
2. Resolve actor memberships  
3. Enforce object scope (org, assignment)  
4. Emit audit event when policy requires  

Cross-tenant responses return **404 or 403** consistently (prefer not to leak existence of foreign IDs — decide per resource in Phase 03).

## 6. i18n contract

- `Accept-Language` and/or user profile locale  
- Catalog payloads include available translations or requested locale fields  
- Validation error keys stable for client-side fa/en maps  

## 7. Media

- Upload via authenticated multipart or presigned PUT  
- Download via **signed URL** with TTL  
- Metadata includes rights fields before publish  

## 8. OpenAPI

- Generated from backend (DRF Spectacular or equivalent) in Phase 04+  
- Published artifact in CI for contract drift checks (target)  

## 9. Out of scope paths (do not invent yet)

- `/marketplace/*`  
- `/ai/*` production endpoints  
- `/nutrition/*` until Phase 09  
- `/billing/*` until Phase 10  

## 10. Related

- `docs/DATA_MODEL.md`  
- `docs/SECURITY_AND_PRIVACY.md`  
- Phase 03 architecture package  
