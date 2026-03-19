# INTERNOVA — CONTEXT.md

> This file is the single source of truth for the Codex agent working on the INTERNOVA Django REST Framework backend.
> Read this entire file before writing any code. Do not skip sections.

---

## 0. Agent Rules (Read First)

These rules are non-negotiable. Follow them in every task.

1. **Always ask before implementing.** If a task is ambiguous, list your assumptions and confirm before writing code.
2. **Never modify migration files manually.** Only run `makemigrations` and `migrate`. Never edit files inside `migrations/` by hand.
3. **Always check Schema.md before touching any model.** Every field, type, constraint, and index is defined there. Do not add, rename, or remove fields without referencing it.
4. **Always follow the services layer pattern.** Business logic lives in `services.py`. Views only handle HTTP. Serializers only handle validation and shape. No exceptions.
5. **Never put ORM queries in views or serializers.** All queryset logic belongs in `services.py` or model managers.
6. **Never hardcode choice strings.** Always use `TextChoices` enums.
7. **Never use `datetime.now()`.** Always use `django.utils.timezone.now()`.
8. **Always use `save(update_fields=[...])` for partial updates.** Never call `.save()` with no arguments unless creating a new record.
9. **Never expose `correct_index` to interns** in any serializer or API response.
10. **Never accept a score from the client** on assessment submissions. Always compute server-side in `AssessmentService.submit()`.
11. **Always use `get_object_or_404`** — never manually catch `DoesNotExist`.
12. **Always wrap multi-step writes in `@transaction.atomic`.**
13. **Always return `HTTP_201_CREATED` for POST responses that create a resource.**
14. **Never store plaintext passwords or tokens.** Use `set_password()` and `write_only=True` on serializer fields.
15. **Never expose `company_account_password` in any list or detail serializer.**

---

## 1. Project Overview

INTERNOVA is an intern management platform. It manages:

- Admin and intern user accounts with JWT auth
- Intern onboarding via registration requests and approval workflow
- Batch management (groups of interns per intake period)
- Skill-based assessments — interns take all published assessments after approval; admin reviews scores and manually assigns intern role
- Daily attendance tracking with auto-classification (clock-in/out)
- Daily Activity Reports (DAR) — PDF uploads per intern per day
- Project assignment and tracking
- Laptop/asset inventory + intern-filed issue reports
- Leave requests with type, business day computation, and approval workflow
- Calendar events, holidays, and business day configuration
- Role-based notifications with per-reader read state
- Feature access toggles per role

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Framework | Django 5.x |
| API | Django REST Framework |
| Database | PostgreSQL 16+ |
| Auth | djangorestframework-simplejwt |
| File Storage | django-storages (S3/local) |
| CORS | django-cors-headers |
| Filtering | django-filter |
| Config | python-decouple |

---

## 3. Project Structure

```
internova/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── api_urls.py
│   └── exceptions.py
├── apps/
│   ├── accounts/       # User model, JWT auth
│   ├── batches/        # Batch CRUD
│   ├── interns/        # InternProfile, registration requests
│   ├── attendance/     # Attendance records, clock-in/out
│   ├── dar/            # Daily Activity Reports
│   ├── projects/       # Projects + intern assignments
│   ├── assets/         # Laptops + issue reports
│   ├── leaves/         # Leave requests
│   ├── assessments/    # Assessments, pages, questions, attempts
│   ├── calendar/       # Events, holidays, settings
│   ├── notifications/  # Notifications + read state
│   └── feature_access/ # Feature toggles
└── .env
```

Each app follows this internal structure:

```
apps/<app>/
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── services.py      ← all business logic lives here
├── filters.py       ← django-filter FilterSet classes
├── permissions.py   ← app-specific permission classes if needed
└── tests/
    ├── test_models.py
    ├── test_services.py
    └── test_views.py
```

---

## 4. Authentication

- Single custom `User` model extending `AbstractBaseUser`. `AUTH_USER_MODEL = 'accounts.User'`.
- Three roles: `superadmin`, `staffadmin`, `intern` — stored as `role` field using `TextChoices`.
- JWT via simplejwt. Tokens passed as `Authorization: Bearer <access_token>`.
- Refresh token blacklisting enabled — `rest_framework_simplejwt.token_blacklist` in `INSTALLED_APPS`.
- On login: validate credentials → update `last_login_at` → return access + refresh tokens.

### Permission Classes (defined in `apps/accounts/permissions.py`)

| Class | Grants access to |
|---|---|
| `IsSuperAdmin` | role == superadmin |
| `IsAdmin` | role in (superadmin, staffadmin) |
| `IsIntern` | role == intern |
| `IsAdminOrIntern` | any authenticated user |
| `IsAdminOrSelf` | admin sees all; intern sees only own objects |

---

## 5. Database — Table Names and Relationships

> Full field definitions, types, constraints, and indexes are in **Schema.md**. Always read Schema.md before modifying any model.

### Table Names

| App | Table(s) |
|---|---|
| accounts | `accounts_user` |
| interns | `interns_internprofile`, `interns_internregistrationrequest` |
| batches | `batches_batch` |
| attendance | `attendance_attendancerecord` |
| dar | `dar_dailyactivityreport` |
| projects | `projects_project`, `projects_project_assigned_interns` |
| assets | `assets_laptop`, `assets_laptopissuereport` |
| leaves | `leaves_leaverequest` |
| assessments | `assessments_assessment`, `assessments_assessmentpage`, `assessments_assessmentquestion`, `assessments_internattempt` |
| calendar | `calendar_calendarevent`, `calendar_holiday`, `calendar_calendarsettings` |
| notifications | `notifications_notification`, `notifications_notificationreadstate` |
| feature_access | `feature_access_featureaccessconfig` |

### Key Relationships

```
accounts_user
├── 1:1  → interns_internprofile         (role='intern' only)
│           └── N:1 → batches_batch
├── 1:N  → interns_internregistrationrequest
├── 1:N  → attendance_attendancerecord
├── 1:N  → dar_dailyactivityreport
├── M:N  → projects_project              (via projects_project_assigned_interns)
├── 1:N  → assets_laptop                 (assigned_to_id)
├── 1:N  → assets_laptopissuereport      (intern_id + resolved_by_id)
├── 1:N  → leaves_leaverequest           (intern_id + decided_by_id)
├── 1:N  → assessments_internattempt
│           └── N:1 → assessments_assessment
│                       └── 1:N → assessments_assessmentpage
│                                   └── 1:N → assessments_assessmentquestion
└── 1:N  → notifications_notificationreadstate
            └── N:1 → notifications_notification

calendar_calendarsettings          (singleton — id=1)
feature_access_featureaccessconfig (singleton — id=1)
```

### Critical Schema Notes

- `interns_internprofile.intern_role` is **NULL by default** — set by admin after reviewing assessment scores.
- `leaves_leaverequest` uses `from_date` / `to_date` — **not** `start_date` / `end_date`.
- `leaves_leaverequest.business_days` is **computed server-side** on submission — never accept from client.
- `assessments_internattempt` has `UNIQUE (intern_id, assessment_id)` — one attempt per intern per assessment.
- `assessments_assessmentquestion.correct_index` is **never returned to interns** in any API response.

---

## 6. API Endpoints

All endpoints are prefixed with `/api/v1/`. Auth via `Authorization: Bearer <token>` unless marked Public.

### Auth — `apps/accounts`

| Method | Endpoint | Auth |
|---|---|---|
| POST | /api/v1/auth/login/ | Public |
| POST | /api/v1/auth/refresh/ | Public |
| POST | /api/v1/auth/logout/ | Authenticated |
| GET | /api/v1/auth/me/ | Authenticated |
| PATCH | /api/v1/auth/me/ | Authenticated |
| POST | /api/v1/auth/change-password/ | Authenticated |

### Admin Management — `apps/accounts`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/admins/ | SuperAdmin |
| POST | /api/v1/admins/ | SuperAdmin |
| GET | /api/v1/admins/{id}/ | SuperAdmin |
| PATCH | /api/v1/admins/{id}/ | SuperAdmin |
| DELETE | /api/v1/admins/{id}/ | SuperAdmin |

### Batches — `apps/batches`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/batches/ | Admin |
| POST | /api/v1/batches/ | Admin |
| GET | /api/v1/batches/{id}/ | Admin |
| PATCH | /api/v1/batches/{id}/ | Admin |
| DELETE | /api/v1/batches/{id}/ | Admin |
| GET | /api/v1/batches/{id}/interns/ | Admin |

### Interns — `apps/interns`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/interns/ | Admin |
| POST | /api/v1/interns/ | Admin |
| GET | /api/v1/interns/{id}/ | Admin or Self |
| PATCH | /api/v1/interns/{id}/ | Admin or Self |
| DELETE | /api/v1/interns/{id}/ | Admin |
| GET | /api/v1/intern-roles/ | Public |
| GET | /api/v1/interns/hours-breakdown/ | Admin |
| GET | /api/v1/interns/{id}/attempts/ | Admin |

### Registration — `apps/interns`

| Method | Endpoint | Auth |
|---|---|---|
| POST | /api/v1/registrations/ | Public |
| GET | /api/v1/registrations/ | Admin |
| GET | /api/v1/registrations/{id}/ | Admin |
| POST | /api/v1/registrations/{id}/approve/ | Admin |
| POST | /api/v1/registrations/{id}/deny/ | Admin |

### Attendance — `apps/attendance`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/attendance/ | Admin |
| POST | /api/v1/attendance/ | Admin |
| GET | /api/v1/attendance/{id}/ | Admin or Self |
| PATCH | /api/v1/attendance/{id}/ | Admin |
| POST | /api/v1/attendance/clock-in/ | Intern |
| POST | /api/v1/attendance/clock-out/ | Intern |
| GET | /api/v1/attendance/summary/weekly/ | Admin |
| GET | /api/v1/attendance/my/ | Intern |

### DAR — `apps/dar`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/dar/ | Admin |
| POST | /api/v1/dar/ | Intern |
| GET | /api/v1/dar/{id}/ | Admin or Self |
| DELETE | /api/v1/dar/{id}/ | Admin |
| GET | /api/v1/dar/missing/ | Admin |
| GET | /api/v1/dar/my/ | Intern |

### Projects — `apps/projects`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/projects/ | Admin |
| POST | /api/v1/projects/ | Admin |
| GET | /api/v1/projects/{id}/ | Admin |
| PATCH | /api/v1/projects/{id}/ | Admin |
| DELETE | /api/v1/projects/{id}/ | Admin |
| POST | /api/v1/projects/{id}/assign/ | Admin |
| DELETE | /api/v1/projects/{id}/assign/{internId}/ | Admin |

### Assets — `apps/assets`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/laptops/ | Admin |
| POST | /api/v1/laptops/ | Admin |
| GET | /api/v1/laptops/{id}/ | Admin |
| PATCH | /api/v1/laptops/{id}/ | Admin |
| DELETE | /api/v1/laptops/{id}/ | Admin |
| GET | /api/v1/laptop-issues/ | Admin or Intern |
| POST | /api/v1/laptop-issues/ | Intern |
| GET | /api/v1/laptop-issues/{id}/ | Admin or Self |
| PATCH | /api/v1/laptop-issues/{id}/ | Admin |

### Leaves — `apps/leaves`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/leaves/ | Admin or Intern |
| POST | /api/v1/leaves/ | Intern |
| GET | /api/v1/leaves/{id}/ | Admin or Self |
| POST | /api/v1/leaves/{id}/approve/ | Admin |
| POST | /api/v1/leaves/{id}/deny/ | Admin |

### Assessments — `apps/assessments`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/assessments/ | Admin or Intern (intern: published only) |
| POST | /api/v1/assessments/ | Admin |
| GET | /api/v1/assessments/{id}/ | Admin or Intern |
| PATCH | /api/v1/assessments/{id}/ | Admin |
| DELETE | /api/v1/assessments/{id}/ | Admin |
| POST | /api/v1/assessments/{id}/publish/ | Admin |
| POST | /api/v1/assessments/{id}/unpublish/ | Admin |
| GET | /api/v1/assessments/{id}/pages/ | Admin |
| POST | /api/v1/assessments/{id}/pages/ | Admin |
| PATCH | /api/v1/assessments/{id}/pages/{pageId}/ | Admin |
| DELETE | /api/v1/assessments/{id}/pages/{pageId}/ | Admin |
| POST | /api/v1/assessments/{id}/pages/{pageId}/questions/ | Admin |
| PATCH | /api/v1/assessments/{id}/pages/{pageId}/questions/{qId}/ | Admin |
| DELETE | /api/v1/assessments/{id}/pages/{pageId}/questions/{qId}/ | Admin |
| GET | /api/v1/attempts/ | Admin or Intern |
| POST | /api/v1/attempts/ | Intern |
| GET | /api/v1/attempts/{id}/ | Admin or Self |
| POST | /api/v1/attempts/{id}/submit/ | Intern |

### Calendar — `apps/calendar`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/events/ | Admin or Intern |
| POST | /api/v1/events/ | Admin |
| PATCH | /api/v1/events/{id}/ | Admin |
| DELETE | /api/v1/events/{id}/ | Admin |
| GET | /api/v1/calendar/settings/ | Admin |
| PATCH | /api/v1/calendar/settings/ | Admin |
| POST | /api/v1/calendar/holidays/ | Admin |
| DELETE | /api/v1/calendar/holidays/{id}/ | Admin |

### Notifications — `apps/notifications`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/notifications/ | Authenticated |
| POST | /api/v1/notifications/ | Admin |
| POST | /api/v1/notifications/{id}/read/ | Authenticated |
| DELETE | /api/v1/notifications/{id}/ | Admin |

### Feature Access — `apps/feature_access`

| Method | Endpoint | Auth |
|---|---|---|
| GET | /api/v1/feature-access/ | SuperAdmin |
| PATCH | /api/v1/feature-access/ | SuperAdmin |

---

## 7. Services Layer Pattern

All business logic lives in `services.py`. This is the most important architectural rule in this project.

```
Request → View → Serializer (validate) → Service (logic) → Response
```

- **Views** — get object, call service, return response. Nothing else.
- **Serializers** — validate input shape and field-level rules. No ORM calls.
- **Services** — all logic: DB writes, status transitions, notifications, aggregations.
- **Models** — field definitions, `clean()` validation, custom managers. No business logic.

### Existing Services

| File | Responsibilities |
|---|---|
| `apps/leaves/services.py` | `LeaveService.approve()`, `LeaveService.deny()` |
| `apps/attendance/services.py` | `AttendanceService.classify()`, `AttendanceService.compute_hours()` |
| `apps/assessments/services.py` | `AssessmentService.submit()`, `AssessmentService._update_intern_aggregate()` |
| `apps/calendar/services.py` | `CalendarService.count_business_days()`, `CalendarService.estimate_end_date()` |
| `apps/notifications/services.py` | `NotificationService.push()` |
| `apps/interns/services.py` | `InternService.approve_registration()` |

---

## 8. Assessment Flow

```
Admin creates Assessment
  → adds Pages (ordered sections)
  → adds Questions per Page (multiple choice, choices as JSONB, correct_index)
  → publishes Assessment (is_published=True)

Intern registration approved → User + InternProfile created, intern_role=NULL
Intern logs in → sees all published assessments
Intern starts attempt → POST /api/v1/attempts/ { "assessment": "<uuid>" }
Intern submits answers → POST /api/v1/attempts/{id}/submit/
  { "answers": [{ "question_id": "...", "selected_index": 2 }] }
  → score computed server-side in AssessmentService.submit()
  → InternProfile.assessment_score updated (average across all attempts)
  → InternProfile.assessment_completed_at set when all published assessments done

Admin reviews scores → GET /api/v1/interns/{id}/attempts/
Admin assigns role  → PATCH /api/v1/interns/{id}/ { "intern_role": "Developer" }
```

**Critical rules:**
- `correct_index` is never returned to interns — use split serializers
- Score is always computed server-side — never trusted from client
- One attempt per intern per assessment — enforced by DB unique constraint

---

## 9. Key Business Rules

### Attendance Auto-Classification
Runs in `AttendanceService.classify()` on every clock-in/out:

| Status | Condition |
|---|---|
| present | login < 09:00, logout >= 17:00 |
| late | login >= 09:00 |
| undertime | logout < 17:00 |
| overtime | logout >= 18:00 |
| absent | no login record |

### Leave Request
- Fields: `from_date`, `to_date`, `type` (sick/vacation/emergency/other), `reason`, `admin_note`
- `business_days` computed server-side by `CalendarService.count_business_days()` on submission
- Approval/denial triggers a notification to the intern

### Business Day Logic
Defined in `apps/calendar/services.py`. Accounts for `CalendarSettings.weekend_days` and `Holiday` records.
Python `weekday()` uses 0=Mon. JS mock used 0=Sun. Normalization map exists in `CalendarService`.

### Notifications Audience
- Values: `all`, `admin`, `intern`, `intern:<uuid>`
- Filter: show if `audience == 'all'` OR `audience == role` OR `audience == 'intern:<user.id>'`
- Read state tracked in `NotificationReadState` — not a JSON blob on the notification

### Singletons
`CalendarSettings` and `FeatureAccessConfig` always have `pk=1`. Enforce in `save()`. Use `get_or_create(pk=1)`.

### Feature Flags
- Admin always-on: `dashboard`, `profile`, `notifications`, `leaves`
- Intern always-on: `dashboard`, `profile`, `notifications`
- Enforce server-side — not just client-side

---

## 10. Coding Conventions

- All PKs: `UUIDField(default=uuid.uuid4, editable=False)`
- All models inherit `BaseModel` which provides `id`, `created_at`, `updated_at`
- All choices: `TextChoices` enums — never raw strings
- All timestamps: `timezone.now()` — never `datetime.now()`
- All partial saves: `save(update_fields=[...])`
- All multi-step writes: `@transaction.atomic`
- All file uploads: validate `content_type` and `size` in serializer
- DAR: path `dar/{intern_id}/{date}_{filename}.pdf`, max 10MB, `application/pdf` only
- Avatar: path `avatars/{user_id}.{ext}`, max 2MB, `image/jpeg` or `image/png`
- Error shape: `{ "error": "..." }` or `{ "errors": {...} }` via custom exception handler
- Always `select_related` / `prefetch_related` on querysets touching related objects
- Always separate list vs detail serializers on models with many fields

---

## 11. Aggregated Endpoints

Computed, not stored. Implement logic in `services.py`.

| Endpoint | Logic |
|---|---|
| `GET /api/v1/attendance/summary/weekly/` | Count records grouped by status per day for Mon–Fri of requested week. Return 0 for missing days. Param: `?week_start=YYYY-MM-DD` |
| `GET /api/v1/interns/hours-breakdown/` | `rendered_hours` and `required_hours` per intern. Param: `?batch_id=<uuid>` optional |
| `GET /api/v1/dar/missing/?date=YYYY-MM-DD` | Active interns with no submitted DAR for the given date |

---

## 12. Seed Command

```bash
python manage.py seed_dev
```

Creates: 2 admin users, 5 interns, 3 batches, 4 published assessments (Frontend/Backend/QA/BA), attendance records, DAR records, projects, laptops, events, holidays, notifications. Initializes `CalendarSettings` and `FeatureAccessConfig` to defaults.

---

## 13. Environment Variables

```env
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/internova
CORS_ALLOWED_ORIGINS=http://localhost:3000
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
# Prod only
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=
```

---

## 14. Reference Files

| File | Purpose |
|---|---|
| `Schema.md` | Full DB schema — all tables, fields, types, constraints, indexes |
| `DevelopmentGuide.md` | Setup, patterns, full code examples, common pitfalls |
| `AGENTS.md` | Agent-specific task instructions and workflow rules |
