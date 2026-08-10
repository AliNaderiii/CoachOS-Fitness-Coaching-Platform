# API Contract & Endpoint Specification — CoachOS

**Document version:** 1.0.0 (Phase 01 Baseline)  
**Last updated:** 2026-08-10  
**Base URL:** `/api/v1`  
**Content-Type:** `application/json` (unless multipart for media uploads)  
**Supported Locales:** `fa-IR` (Persian), `en-US` (English)  
**Strict constraint:** Arabic is explicitly out of scope.

---

## 1. Global API Architectural Standards

### 1.1 Authentication & Session Header
All endpoints (except public registration, login, and health endpoints) require an authenticated session or Bearer token header:
```http
Authorization: Bearer <access_token>
```
Or secure `HttpOnly; SameSite=Lax` session cookie.

### 1.2 Localization & Content Negotiation
Clients communicate language preferences via standard HTTP headers or user profile defaults:
```http
Accept-Language: fa-IR, fa;q=0.9, en;q=0.8
```
All localized error codes and catalog entities return responses conforming to the negotiated locale.

### 1.3 Standardized Error Response Envelope
To prevent sensitive data leakage while providing actionable, localized feedback, all errors conform to the standard RFC 7807 problem structure:
```json
{
  "error": {
    "code": "permission_denied",
    "message_key": "errors.authz.unassigned_athlete",
    "detail": "You do not possess an active assignment for this athlete.",
    "field_errors": {},
    "timestamp": "2026-08-10T14:30:00Z"
  }
}
```

### 1.4 Common HTTP Status Codes
- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created.
- `204 No Content`: Successful mutation with no response body.
- `400 Bad Request`: Validation failure or malformed JSON payload.
- `401 Unauthorized`: Missing, expired, or invalid authentication credentials.
- `403 Forbidden`: Authenticated caller lacks required role or object-level assignment.
- `404 Not Found`: Target entity does not exist or belongs to another tenant (cross-tenant obscurity).
- `409 Conflict`: Unique constraint violation (e.g., duplicate slug or email).
- `410 Gone`: Expired invitation or password reset token.
- `429 Too Many Requests`: Rate limit breached.
- `500 Internal Server Error`: Unhandled server exception (sanitized in production).

---

## 2. Authentication & Identity Endpoints (`/api/v1/auth`)

### 2.1 User Registration
- **Path:** `POST /api/v1/auth/register`
- **Auth:** Public (Rate limited: 5 req/min)
- **Request Body:**
  ```json
  {
    "email": "coach.reza@example.com",
    "password": "SecurePassword123!",
    "display_name": "Reza Rahimi",
    "preferred_locale": "fa-IR",
    "invitation_token": "optional_token_string"
  }
  ```
- **Response `201 Created`:**
  ```json
  {
    "user": {
      "id": "01913c7a-5b12-7000-8000-000000000001",
      "email": "coach.reza@example.com",
      "display_name": "Reza Rahimi",
      "preferred_locale": "fa-IR",
      "timezone": "Asia/Tehran"
    },
    "token": "eyJhbGciOi..."
  }
  ```

### 2.2 User Login
- **Path:** `POST /api/v1/auth/login`
- **Auth:** Public (Rate limited: 5 failed attempts/15 min)
- **Request Body:**
  ```json
  {
    "email": "coach.reza@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "user": {
      "id": "01913c7a-5b12-7000-8000-000000000001",
      "email": "coach.reza@example.com",
      "display_name": "Reza Rahimi",
      "preferred_locale": "fa-IR",
      "is_platform_admin": false
    },
    "memberships": [
      {
        "organization_id": "01913c7a-5b12-7000-8000-000000000010",
        "organization_name": "Alborz Fitness",
        "organization_slug": "alborz-fitness",
        "role": "coach",
        "status": "active"
      }
    ],
    "access_token": "eyJhbGciOi...",
    "refresh_token": "def50200..."
  }
  ```

### 2.3 Current User Profile & Locale Switcher
- **Path:** `GET /api/v1/auth/me` | `PATCH /api/v1/auth/me`
- **Auth:** Authenticated User
- **PATCH Request Body:**
  ```json
  {
    "display_name": "Reza Rahimi",
    "preferred_locale": "fa-IR",
    "preferred_unit": "kg",
    "timezone": "Asia/Tehran"
  }
  ```

---

## 3. Organization & Tenancy Endpoints (`/api/v1/organizations`)

### 3.1 Create Organization Workspace
- **Path:** `POST /api/v1/organizations`
- **Auth:** Authenticated User
- **Request Body:**
  ```json
  {
    "name": "Alborz Fitness Club",
    "slug": "alborz-fitness",
    "primary_location": {
      "name": "Central Facility",
      "address_line1": "Valiasr St, Tehran",
      "city": "Tehran",
      "phone": "+982188888888"
    }
  }
  ```
- **Response `201 Created`:** Returns Organization and primary Location records.

### 3.2 Dispatch Organization Invitation
- **Path:** `POST /api/v1/organizations/{org_id}/invitations`
- **Auth:** Requires `Owner` role (or `Coach` inviting an Athlete)
- **Request Body:**
  ```json
  {
    "email": "athlete.neda@example.com",
    "role": "athlete",
    "assigned_coach_id": "01913c7a-5b12-7000-8000-000000000001"
  }
  ```
- **Response `201 Created`:**
  ```json
  {
    "invitation_id": "01913c7a-5b12-7000-8000-000000000050",
    "email": "athlete.neda@example.com",
    "role": "athlete",
    "expires_at": "2026-08-17T14:00:00Z"
  }
  ```

### 3.3 Manage Members & Revoke Roles
- **Path:** `PATCH /api/v1/organizations/{org_id}/members/{membership_id}`
- **Auth:** Requires `Owner` role
- **Request Body:**
  ```json
  {
    "status": "suspended"
  }
  ```

---

## 4. Exercise Library Endpoints (`/api/v1/exercises`)

### 4.1 Search & Filter Exercises
- **Path:** `GET /api/v1/exercises`
- **Auth:** Authenticated User (returns canonical + org-private exercises)
- **Query Parameters:**
  - `q`: Search string (supports Persian character variant folding, e.g., `پرس سینه`).
  - `muscle`: Filter by muscle tag (e.g., `quadriceps`).
  - `movement_pattern`: Filter (e.g., `squat`, `horizontal_push`).
  - `equipment`: Filter (e.g., `barbell`, `dumbbell`).
  - `locale`: Active translation filter (`fa-IR` or `en-US`).
- **Response `200 OK`:**
  ```json
  {
    "count": 42,
    "results": [
      {
        "id": "01913c7a-5b12-7000-8000-000000000100",
        "name": "اسکوات از پشت با هالتر",
        "name_en": "Barbell Back Squat",
        "movement_pattern": "squat",
        "primary_muscles": ["quadriceps", "glutes"],
        "equipment_required": ["barbell", "squat_rack"],
        "difficulty": "intermediate",
        "media_thumbnail_url": "https://storage.coachos.fit/media/thumb_squat.webp?sig=..."
      }
    ]
  }
  ```

### 4.2 Create Custom Private Exercise
- **Path:** `POST /api/v1/exercises`
- **Auth:** Requires `Coach` or `Owner` role
- **Request Body:**
  ```json
  {
    "movement_pattern": "lunge",
    "difficulty": "intermediate",
    "primary_muscles": ["glutes", "hamstrings"],
    "equipment_required": ["dumbbell"],
    "translations": {
      "fa-IR": {
        "name": "لانج با دمبل به عقب",
        "instructions": "پای راست را به عقب ببرید...",
        "coaching_cues": ["زانو عمود بماند", "سینه بالا"]
      },
      "en-US": {
        "name": "Dumbbell Reverse Lunge",
        "instructions": "Step back with right leg...",
        "coaching_cues": ["Keep torso upright"]
      }
    },
    "media": {
      "storage_key": "org_uploads/0191.../lunge.mp4",
      "rights": {
        "license_type": "original_production",
        "creator_attribution": "Alborz Fitness Media",
        "permitted_commercial_use": true
      }
    }
  }
  ```

---

## 5. Training Programming Endpoints (`/api/v1/programs`)

### 5.1 Program Builder Tree CRUD
- **Path:** `POST /api/v1/programs` | `GET /api/v1/programs/{id}`
- **Auth:** Requires `Coach` or `Owner` role
- **Request Body (Nested Hierarchy):**
  ```json
  {
    "title": "8-Week Hypertrophy Mesocycle",
    "target_goal": "hypertrophy",
    "is_template": true,
    "phases": [
      {
        "name": "Phase 1: Accumulation",
        "sequence_order": 1,
        "duration_weeks": 4,
        "weeks": [
          {
            "week_number": 1,
            "days": [
              {
                "day_number": 1,
                "title": "Upper Body Strength",
                "workout": {
                  "title": "Upper Body Push/Pull",
                  "items": [
                    {
                      "exercise_id": "01913c7a-5b12-7000-8000-000000000100",
                      "sequence_order": 1,
                      "group_key": "A1",
                      "rest_seconds_between_sets": 90,
                      "coach_notes": "Focus on controlled 3s eccentric",
                      "prescriptions": [
                        {
                          "set_index": 1,
                          "target_reps": "8",
                          "target_load": "80 kg",
                          "target_rpe": 8.0,
                          "tempo": "3-1-1-0"
                        }
                      ]
                    }
                  ]
                }
              }
            ]
          }
        ]
      }
    ]
  }
  ```

### 5.2 Assign Program to Athlete (Snapshot Generation)
- **Path:** `POST /api/v1/programs/{program_id}/assign`
- **Auth:** Requires `Coach` or `Owner` role assigned to athlete
- **Request Body:**
  ```json
  {
    "athlete_user_id": "01913c7a-5b12-7000-8000-000000000020",
    "start_date": "2026-08-17"
  }
  ```
- **Response `201 Created`:** Returns `ProgramAssignment` record with frozen `snapshot_payload`.

---

## 6. Athlete Workout Execution Endpoints (`/api/v1/athlete`)

### 6.1 Get "Today's Workout"
- **Path:** `GET /api/v1/athlete/today`
- **Auth:** Authenticated Athlete (`P-ATH`)
- **Response `200 OK`:**
  ```json
  {
    "has_scheduled_workout": true,
    "workout_session_id": "01913c7a-5b12-7000-8000-000000000300",
    "scheduled_date": "2026-08-10",
    "status": "scheduled",
    "workout_title": "Upper Body Push/Pull",
    "items": [
      {
        "item_id": "01913c7a-5b12-7000-8000-000000000310",
        "exercise_name": "اسکوات از پشت با هالتر",
        "exercise_name_en": "Barbell Back Squat",
        "group_key": "A1",
        "demo_video_signed_url": "https://storage.coachos.fit/videos/squat.mp4?sig=...",
        "coach_notes": "Focus on controlled 3s eccentric",
        "prescriptions": [
          {
            "set_index": 1,
            "target_reps": "8",
            "target_load": "80 kg",
            "target_rpe": 8.0,
            "tempo": "3-1-1-0"
          }
        ],
        "previous_performance": {
          "date": "2026-08-03",
          "logged_load_kg": 77.5,
          "logged_reps": 8
        }
      }
    ]
  }
  ```

### 6.2 Log Set Actuals
- **Path:** `POST /api/v1/workout-sessions/{session_id}/sets`
- **Auth:** Authenticated Athlete (must own `{session_id}`)
- **Request Body:**
  ```json
  {
    "exercise_id": "01913c7a-5b12-7000-8000-000000000100",
    "set_index": 1,
    "actual_reps": 8,
    "actual_load_kg": 80.0,
    "actual_rpe": 8.5,
    "is_completed": true,
    "notes": "Felt solid on rep 8"
  }
  ```

### 6.3 Complete Workout Session & Feedback
- **Path:** `POST /api/v1/workout-sessions/{session_id}/complete`
- **Auth:** Authenticated Athlete
- **Request Body:**
  ```json
  {
    "session_rpe": 8.0,
    "fatigue_score": 3,
    "athlete_notes": "Great pump today, shoulder felt fine.",
    "feedback_flags": [
      {
        "flag_type": "joint_pain",
        "anatomical_location": "Left Wrist",
        "severity": "mild",
        "details": "Slight pinch on last set of bench press"
      }
    ]
  }
  ```

---

## 7. Contextual Communication Endpoints (`/api/v1/messages`)

### 7.1 Send Contextual Message
- **Path:** `POST /api/v1/messages`
- **Auth:** Authenticated Coach or Athlete (must have active assignment)
- **Request Body:**
  ```json
  {
    "recipient_user_id": "01913c7a-5b12-7000-8000-000000000001",
    "workout_session_id": "01913c7a-5b12-7000-8000-000000000300",
    "content": "Should I increase load by 2.5kg next week on squats?"
  }
  ```

---

## 8. Platform Administration & Privacy Endpoints (`/api/v1/admin` & `/api/v1/privacy`)

### 8.1 Exercise Moderation Queue
- **Path:** `GET /api/v1/admin/moderation/exercises` | `POST /api/v1/admin/moderation/exercises/{id}/approve`
- **Auth:** Requires `is_platform_admin = true`

### 8.2 Audit Log Inspection
- **Path:** `GET /api/v1/admin/audit-logs`
- **Auth:** Requires `is_platform_admin = true` or `Owner` (tenant-scoped)
- **Query Parameters:** `org_id`, `actor_id`, `action_type`, `start_date`, `end_date`.

### 8.3 Athlete Data Portability Export
- **Path:** `POST /api/v1/privacy/export-request`
- **Auth:** Authenticated User
- **Response `202 Accepted`:** Initiates background job producing encrypted export `.zip`.

### 8.4 Athlete Account Erasure Request
- **Path:** `POST /api/v1/privacy/forget-me`
- **Auth:** Authenticated User (requires password re-verification)
