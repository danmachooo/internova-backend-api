# PLAN.md — INTERNOVA Working Memory

> This is the active task tracker for the Codex agent.
> Update this file after every completed step — mark `[x]`, add notes, flag the next step.
> Read this file at every session start after AGENTS.md and CONTEXT.md.

---

## How to Use This File

- `[ ]` — Not started
- `[~]` — In progress (currently active)
- `[x]` — Complete
- `[!]` — Blocked — reason noted inline

**At session start:** Find the first `[~]` or `[ ]` step and continue from there.
**After each step:** Mark it `[x]`, add a short note of what was done, set the next step to `[~]`.
**When blocked:** Mark `[!]` and describe what is blocking it.

---

## Build Order Summary

| # | App / Task | Status |
|---|---|---|
| 1 | accounts | `[x]` |
| 2 | batches | `[x]` |
| 3 | interns | `[x]` |
| 4 | assessments | `[x]` |
| 5 | attendance | `[x]` |
| 6 | dar | `[x]` |
| 7 | calendar | `[x]` |
| 8 | leaves | `[x]` |
| 9 | projects | `[x]` |
| 10 | assets | `[x]` |
| 11 | notifications | `[x]` |
| 12 | feature_access | `[x]` |
| 14 | seed_dev | `[x]` |
| 15 | deployment / prod config | `[x]` |
| 16 | post-review hardening fixes | `[x]` |
| 17 | README documentation | `[x]` |
| 18 | Render deployment support | `[x]` |

---

## Active Task

> **Task 18 - Render deployment support** is complete.
> No further active build steps remain in the current plan.

---

## 1. accounts

**Depends on:** nothing — build this first
**Provides:** `User` model, JWT auth, permission classes used by all other apps

### Summary Checklist
- [x] Model
- [x] Migrations
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Permissions
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **1.1** Write `User` model in `apps/accounts/models.py`
  - Extends `AbstractBaseUser` + `PermissionsMixin`
  - Fields: `id` (UUID), `email`, `name`, `role`, `status`, `last_login_at`, `is_active`, `is_staff`, `created_at`, `updated_at`
  - `RoleChoices`: `superadmin`, `staffadmin`, `intern`
  - `StatusChoices`: `active`, `inactive`
  - Custom `UserManager` with `create_user()` and `create_superuser()`
  - `USERNAME_FIELD = 'email'`
  - `Meta.db_table = 'accounts_user'`
  - Indexes on `role`, `status`

- [x] **1.2** Set `AUTH_USER_MODEL = 'accounts.User'` in `config/settings/base.py`

- [x] **1.3** Run `/migrate accounts` — verify no destructive operations

- [x] **1.4** Write permission classes in `apps/accounts/permissions.py`
  - `IsSuperAdmin`, `IsAdmin`, `IsIntern`, `IsAdminOrIntern`, `IsAdminOrSelf`

- [x] **1.5** Write serializers in `apps/accounts/serializers.py`
  - `UserListSerializer` — id, name, email, role, status
  - `UserDetailSerializer` — all fields, password write-only
  - `LoginSerializer` — email, password

- [x] **1.6** Write views in `apps/accounts/views.py`
  - `LoginView` — validate credentials, update `last_login_at`, return access + refresh tokens
  - `LogoutView` — blacklist refresh token
  - `MeView` — GET/PATCH own profile
  - `ChangePasswordView` — validate old password, set new
  - `AdminUserViewSet` — CRUD for admin users (SuperAdmin only)

- [x] **1.7** Write URLs in `apps/accounts/urls.py`
  - `POST auth/login/`
  - `POST auth/logout/`
  - `POST auth/refresh/` (simplejwt built-in)
  - `GET/PATCH auth/me/`
  - `POST auth/change-password/`
  - `GET/POST/PATCH/DELETE admins/`

- [x] **1.8** Write tests
  - `test_login_success`
  - `test_login_invalid_credentials`
  - `test_login_inactive_account`
  - `test_logout_blacklists_token`
  - `test_me_returns_own_profile`
  - `test_change_password_success`
  - `test_admin_crud_superadmin_only`

- [x] **1.9** Run `python manage.py test apps.accounts --verbosity=2` — all passing

**Notes:**
- Bootstrapped the Django project and `accounts` app from an empty repo scaffold.
- Added `common/models.py` for the shared `BaseModel`, the split settings package, `config/api_urls.py`, and the project exception handler.
- Implemented `apps/accounts/services.py` so auth and admin-user logic stays out of views.
- Generated `apps/accounts/migrations/0001_initial.py`, applied migrations safely, and ran `python manage.py test apps.accounts --verbosity=2` with 11 passing tests.

---

## 2. batches

**Depends on:** accounts (User FK for future intern assignment)
**Provides:** `Batch` model used by `interns_internprofile`

### Summary Checklist
- [x] Model
- [x] Migrations
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Filters
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **2.1** Write `Batch` model — fields: `id`, `name`, `start_date`, `end_date`, `status`, `progress`. `Meta.db_table = 'batches_batch'`
- [x] **2.2** Run `/migrate batches`
- [x] **2.3** Write `BatchListSerializer`, `BatchDetailSerializer`
- [x] **2.4** Write `BatchViewSet` with `interns` custom action (`GET /batches/{id}/interns/`)
- [x] **2.5** Write `BatchFilter` — filter by `status`
- [x] **2.6** Write URLs — register `BatchViewSet` via router
- [x] **2.7** Write tests — CRUD, filter by status, intern list action, intern-cannot-access
- [x] **2.8** Run tests — all passing

**Notes:**
- Added the `batches` app scaffold, router, model admin, serializers, filter, and tests.
- Registered `apps.batches` in `config/settings/base.py` and included `apps.batches.urls` in `config/api_urls.py`.
- The `GET /api/v1/batches/{id}/interns/` action safely returns an empty list until the `interns` app exists, which keeps the app scaffold complete without crossing app boundaries early.
- Generated `apps/batches/migrations/0001_initial.py`, applied migrations safely, and ran `python manage.py test apps.batches --verbosity=2` with 7 passing tests.

---

## 3. interns

**Depends on:** accounts, batches
**Provides:** `InternProfile`, `InternRegistrationRequest` — used by attendance, dar, assessments, leaves, projects, assets

### Summary Checklist
- [x] Models
- [x] Migrations
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Services
- [x] Filters
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **3.1** Write `InternProfile` model
  - OneToOne with `accounts.User`
  - FK to `batches.Batch` (nullable)
  - Fields per Schema.md — including `intern_role` (nullable), `github_username`, assessment fields
  - Custom manager: `active()`, `in_batch()`, `awaiting_role_assignment()`

- [x] **3.2** Write `InternRegistrationRequest` model
  - Fields per Schema.md — including `github_username`
  - `password` hashed with `make_password()` on save

- [x] **3.3** Run `/migrate interns`

- [x] **3.4** Write `InternService` in `apps/interns/services.py`
  - `approve_registration(registration_id, decided_by)` — `@transaction.atomic`, creates `User` + `InternProfile`
  - `deny_registration(registration_id, decided_by)`

- [x] **3.5** Write serializers
  - `InternListSerializer`, `InternDetailSerializer`
  - `InternRegistrationRequestSerializer`
  - `AssessmentResultSummarySerializer` (for intern detail)

- [x] **3.6** Write `InternViewSet` — CRUD + `hours_breakdown` action
- [x] **3.7** Write `RegistrationViewSet` — list, retrieve, approve, deny actions
- [x] **3.8** Write `InternFilter` — filter by batch, role, status, assessment_completed
- [x] **3.9** Write URLs — `GET /intern-roles/`, `/interns/`, `/interns/hours-breakdown/`, `/registrations/`
- [x] **3.10** Write tests — registration flow, approval creates profile, denial, permission checks
- [x] **3.11** Run tests — all passing

**Notes:**
- Added `InternProfile` and `InternRegistrationRequest` with schema-aligned fields, indexes, manager helpers, and hashed registration passwords.
- Implemented the `InternService` approval/denial flow in a transaction, plus intern creation, update, delete, hours breakdown, and assessment-attempt fallback support.
- Wired the `interns` app into `config/settings/base.py` and `config/api_urls.py`, then generated `apps/interns/migrations/0001_initial.py`.
- Ran `python manage.py test apps.interns --verbosity=2` with 11 passing tests.

---

## 4. assessments

**Depends on:** accounts, interns (updates InternProfile on attempt submit)
**Provides:** `Assessment`, `AssessmentPage`, `AssessmentQuestion`, `InternAttempt`

### Summary Checklist
- [x] Models
- [x] Migrations
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Services
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **4.1** Write models — `Assessment`, `AssessmentPage`, `AssessmentQuestion`, `InternAttempt`
  - `AssessmentQuestion.clean()` — validate `choices` length and `correct_index` range
  - `unique_together` on `(page, order)` and `(assessment, order)` and `(intern, assessment)`
  - `Assessment.publish()` and `unpublish()` methods

- [x] **4.2** Run `/migrate assessments`

- [x] **4.3** Write `AssessmentService` in `apps/assessments/services.py`
  - `submit(attempt, answers)` — compute score server-side, update `InternProfile` aggregate
  - `_update_intern_aggregate(intern)` — recompute `assessment_score` and `assessment_completed_at`

- [x] **4.4** Write serializers — split by role (intern never sees `correct_index`)
  - `AssessmentQuestionSerializer` (intern-safe)
  - `AssessmentQuestionAdminSerializer` (includes `correct_index`)
  - `AssessmentPageSerializer`, `AssessmentSerializer`, `AssessmentAdminSerializer`
  - `InternAttemptSerializer`

- [x] **4.5** Write `AssessmentViewSet` — publish/unpublish actions, role-split serializers, intern sees published only
- [x] **4.6** Write `InternAttemptViewSet` — create (intern only), submit action
- [x] **4.7** Write URLs — `/assessments/`, `/attempts/`, nested page/question routes
- [x] **4.8** Write tests
  - `correct_index` never in intern response
  - Score computed server-side
  - Duplicate attempt rejected
  - Resubmit rejected
  - Admin cannot start attempt

- [x] **4.9** Run tests — all passing

**Notes:**
- Added the assessment domain models, server-side scoring service, role-split serializers, nested page/question routes, and attempt endpoints.
- Wired `apps.assessments` into `config/settings/base.py` and `config/api_urls.py`, then generated `apps/assessments/migrations/0001_initial.py`.
- Replaced the interns attempt fallback with the real `InternAttempt`-backed behavior and updated shared object-permission handling for intern-owned attempts.
- Ran `python manage.py test apps.assessments --verbosity=2` with 7 passing tests.

---

## 5. attendance

**Depends on:** accounts, interns
**Provides:** `AttendanceRecord`, clock-in/out, weekly summary

### Summary Checklist
- [x] Model
- [x] Migrations
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Services
- [x] Filters
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **5.1** Write `AttendanceRecord` model — `unique_together = ('intern', 'date')`
- [x] **5.2** Run `/migrate attendance`
- [x] **5.3** Write `AttendanceService` — `classify()`, `compute_hours()`, `clock_in()`, `clock_out()`
- [x] **5.4** Write serializers — `AttendanceRecordSerializer` (hours + status read-only)
- [x] **5.5** Write `AttendanceViewSet` — admin CRUD + `my` action for intern
- [x] **5.6** Write `ClockInView`, `ClockOutView` — intern only
- [x] **5.7** Write `WeeklyAttendanceSummaryView` — aggregated Mon–Fri counts
- [x] **5.8** Write `AttendanceFilter` — filter by intern, date, status
- [x] **5.9** Write URLs
- [x] **5.10** Write tests — clock-in success, duplicate rejected, classification accuracy, summary format
- [x] **5.11** Run tests — all passing

**Notes:**
- Added the attendance model, classification/hour computation service, intern clock-in/out endpoints, admin CRUD, filter, and weekly summary endpoint.
- Wired `apps.attendance` into `config/settings/base.py` and `config/api_urls.py`, then generated `apps/attendance/migrations/0001_initial.py`.
- Synced `InternProfile.rendered_hours` from inside the attendance service using a function-level import to avoid cross-app circular imports.
- Ran `python manage.py test apps.attendance --verbosity=2` with 7 passing tests.

---

## 6. dar

**Depends on:** accounts, interns
**Provides:** `DailyActivityReport`, PDF upload, missing report detection

### Summary Checklist
- [x] Model
- [x] Migrations
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **6.1** Write `DailyActivityReport` model — `unique_together = ('intern', 'date')`, custom upload path
- [x] **6.2** Run `/migrate dar`
- [x] **6.3** Write serializer — validate PDF only, max 10MB
- [x] **6.4** Write `DARViewSet` — `MultiPartParser`, `missing` action, `my` action
- [x] **6.5** Write URLs
- [x] **6.6** Write tests — upload success, wrong file type rejected, oversized rejected, missing report detection
- [x] **6.7** Run tests — all passing

**Notes:**
- Created the `dar` app scaffold, wired it into settings and API URLs, and added `DailyActivityReport` with the schema-aligned table name, indexes, uniqueness constraint, and upload path.
- Added DAR submission and missing-report logic in `apps/dar/services.py`, serializer-side PDF and size validation, and a role-aware `DARViewSet` with `missing` and `my` actions.
- Generated `apps/dar/migrations/0001_initial.py`, applied it safely, and ran `python manage.py test apps.dar --verbosity=2` with 10 passing tests.
---

## 7. calendar

**Depends on:** nothing (standalone, but provides services to leaves)
**Provides:** `CalendarEvent`, `Holiday`, `CalendarSettings`, `CalendarService`

### Summary Checklist
- [x] Models
- [x] Migrations
- [x] Services
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **7.1** Write `CalendarEvent`, `Holiday`, `CalendarSettings` models
  - `CalendarSettings` — singleton pattern, `pk=1`, `get()` classmethod
- [x] **7.2** Run `/migrate calendar`
- [x] **7.3** Write `CalendarService` — `is_weekend()`, `is_holiday()`, `count_business_days()`, `estimate_end_date()`
  - Include JS→Python weekday normalization
- [x] **7.4** Write serializers
- [x] **7.5** Write `CalendarEventViewSet`, `HolidayViewSet`, `CalendarSettingsView`
- [x] **7.6** Write URLs
- [x] **7.7** Write tests — business day counting, singleton enforcement, holiday detection
- [x] **7.8** Run tests — all passing

**Notes:**
- Scaffolded the `calendar` app with `CalendarEvent`, `Holiday`, and singleton `CalendarSettings`, plus calendar services, serializers, views, URLs, admin registration, and tests.
- Registered `django.contrib.postgres` and `apps.calendar` in `config/settings/base.py`, then included `apps.calendar.urls` in `config/api_urls.py`.
- Generated `apps/calendar/migrations/0001_initial.py` and `apps/calendar/migrations/0002_alter_calendarsettings_weekend_days.py`, applied them safely, and ran `python manage.py test apps.calendar --verbosity=2` with 10 passing tests.

---

## 8. leaves

**Depends on:** accounts, interns, calendar (CalendarService for business days), notifications
**Provides:** `LeaveRequest`, approval workflow

### Summary Checklist
- [x] Model
- [x] Migrations
- [x] Services
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Filters
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **8.1** Write `LeaveRequest` model — `from_date`, `to_date`, `business_days`, `type`, `admin_note`
- [x] **8.2** Run `/migrate leaves`
- [x] **8.3** Write `LeaveService` — `approve()`, `deny()`, both `@transaction.atomic`, trigger notifications
- [x] **8.4** Write serializer — `business_days` computed in `create()`, `from_date`/`to_date` validated
- [x] **8.5** Write `LeaveRequestViewSet` — `get_queryset()` filters by role, `approve`/`deny` actions
- [x] **8.6** Write `LeaveRequestFilter` — type, status, date range
- [x] **8.7** Write URLs
- [x] **8.8** Write tests — submit with type, business days computed, approve flow, deny with note, wrong role
- [x] **8.9** Run tests — all passing

**Notes:**
- Scaffolded the `leaves` app with the schema-aligned `LeaveRequest` model, service-driven submit/approve/deny flow, serializers, role-aware viewset, filters, URLs, admin registration, and tests.
- Wired `apps.leaves` into `config/settings/base.py` and included `apps.leaves.urls` in `config/api_urls.py`, then generated `apps/leaves/migrations/0001_initial.py`.
- Ran `python manage.py test apps.leaves --verbosity=2` with 9 passing tests after applying the new migration safely.

---

## 9. projects

**Depends on:** accounts, interns
**Provides:** `Project`, intern-project ManyToMany assignment

### Summary Checklist
- [x] Model
- [x] Migrations
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **9.1** Write `Project` model — ManyToMany to `accounts.User` via `assigned_interns`
- [x] **9.2** Run `/migrate projects`
- [x] **9.3** Write serializers — `ProjectListSerializer`, `ProjectDetailSerializer` (with assigned intern names)
- [x] **9.4** Write `ProjectViewSet` — `assign` and `unassign` custom actions
- [x] **9.5** Write URLs
- [x] **9.6** Write tests — CRUD, assign intern, remove intern, intern cannot modify
- [x] **9.7** Run tests — all passing

**Notes:**
- Scaffolded the `projects` app with the schema-aligned `Project` model, assignment service methods, split serializers, admin-only viewset, routes, admin registration, and tests.
- Wired `apps.projects` into `config/settings/base.py` and included `apps.projects.urls` in `config/api_urls.py`, then generated `apps/projects/migrations/0001_initial.py`.
- Ran `python manage.py test apps.projects --verbosity=2` with 7 passing tests after applying the migration safely.

---

## 10. assets

**Depends on:** accounts, interns
**Provides:** `Laptop`, `LaptopIssueReport`

### Summary Checklist
- [x] Models
- [x] Migrations
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **10.1** Write `Laptop` model — `GenericIPAddressField`, `assigned_to` nullable FK
- [x] **10.2** Write `LaptopIssueReport` model — intern files, admin resolves
- [x] **10.3** Run `/migrate assets`
- [x] **10.4** Write serializers for both models
- [x] **10.5** Write `LaptopViewSet` (admin only), `LaptopIssueReportViewSet` (intern files, admin manages)
- [x] **10.6** Write URLs
- [x] **10.7** Write tests — laptop CRUD, issue report submit, admin resolves, intern sees own only
- [x] **10.8** Run tests — all passing

**Notes:**
- Scaffolded the `assets` app with the `Laptop` and `LaptopIssueReport` models, service-layer status/issue logic, serializers, admin/intern viewsets, routes, admin registration, and tests.
- Wired `apps.assets` into `config/settings/base.py` and included `apps.assets.urls` in `config/api_urls.py`, then generated `apps/assets/migrations/0001_initial.py`.
- Ran `python manage.py test apps.assets --verbosity=2` with 9 passing tests after applying the migration safely.

---

## 11. notifications

**Depends on:** accounts
**Provides:** `Notification`, `NotificationReadState`, `NotificationService` — called by leaves, assessments, attendance

### Summary Checklist
- [x] Models
- [x] Migrations
- [x] Services
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **11.1** Write `Notification`, `NotificationReadState` models
  - `unique_together = ('notification', 'reader')` on read state
- [x] **11.2** Run `/migrate notifications`
- [x] **11.3** Write `NotificationService.push()` — central notification creation method
- [x] **11.4** Write serializer — annotate `read` field based on current user's read state
- [x] **11.5** Write `NotificationViewSet` — `get_queryset()` filters by audience, `read` action
- [x] **11.6** Write URLs
- [x] **11.7** Write tests — audience filtering (all/admin/intern/intern:<id>), mark read, admin can delete
- [x] **11.8** Run tests — all passing

**Notes:**
- Scaffolded the `notifications` app with schema-aligned `Notification` and `NotificationReadState` models, admin registration, `NotificationService`, serializer, viewset, routes, and tests.
- Wired `apps.notifications` into `config/settings/base.py` and included `apps.notifications.urls` in `config/api_urls.py`, then generated `apps/notifications/migrations/0001_initial.py`.
- Implemented audience-aware queryset filtering with per-user `read` annotation and a service-backed `read` action that creates `NotificationReadState` idempotently.
- Ran `python manage.py test apps.notifications --verbosity=2` with 12 passing tests after applying the migration safely.

---

## 12. feature_access

**Depends on:** nothing (singleton, standalone)
**Provides:** `FeatureAccessConfig` — feature toggle config per role

### Summary Checklist
- [x] Model
- [x] Migrations
- [x] Serializers
- [x] Views
- [x] URLs
- [x] Tests
- [x] Verified

### Detailed Steps

- [x] **12.1** Write `FeatureAccessConfig` model — singleton (`pk=1`), `admin_features` JSONB, `intern_features` JSONB
  - Always-on enforcement in `save()` for dashboard, profile, notifications, leaves
- [x] **12.2** Run `/migrate feature_access`
- [x] **12.3** Write serializer — validate keys match known feature lists
- [x] **12.4** Write `FeatureAccessView` — GET + PATCH, SuperAdmin only
- [x] **12.5** Write URLs
- [x] **12.6** Write tests — get config, update toggle, always-on features cannot be disabled, staffadmin rejected
- [x] **12.7** Run tests — all passing

**Notes:**
- Scaffolded the `feature_access` app from scratch with a singleton `FeatureAccessConfig` model, admin registration, serializer validation, SuperAdmin-only GET/PATCH view, route, and test coverage.
- Wired `apps.feature_access` into `config/settings/base.py` and `config/api_urls.py`, then generated and applied `apps/feature_access/migrations/0001_initial.py`.
- Enforced always-on server-side features in `FeatureAccessConfig.save()` and verified the target app with `python manage.py test apps.feature_access --verbosity=2` (6 passing tests).

---

## 14. seed_dev

**Depends on:** all apps complete
**Provides:** `python manage.py seed_dev` — idempotent dev data population

### Summary Checklist
- [x] Management command created
- [x] DEBUG guard added
- [x] All apps seeded
- [x] Idempotency verified
- [x] Verified

### Detailed Steps

- [x] **14.1** Create management command at `apps/accounts/management/commands/seed_dev.py`
- [x] **14.2** Add `DEBUG` guard — raise `CommandError` if not in debug mode
- [x] **14.3** Seed in dependency order:
  - [x] 2 admin users (superadmin + staffadmin)
  - [x] 3 batches
  - [x] 5 interns with profiles
  - [x] 4 published assessments (Frontend, Backend, QA, BA) — 2 pages, 5 questions each
  - [x] Attendance records (25 records across 5 days, 5 interns)
  - [x] DAR records (4 records)
  - [x] 4 projects with intern assignments
  - [x] 5 laptops
  - [x] 4 calendar events
  - [x] `CalendarSettings` — `weekend_days=[0, 6]`
  - [x] `FeatureAccessConfig` — defaults
  - [x] 4 notifications

- [x] **14.4** Use `get_or_create` throughout — never `create()`
- [x] **14.5** Run `python manage.py seed_dev` twice — confirm no duplicates on second run
- [x] **14.6** Update PLAN.md

**Notes:**
- Added the consolidated seed command in `apps/accounts/management/commands/seed_dev.py` with a `DEBUG` guard, per-app seed blocks, and confirmation output for each seeded section.
- Seeded 2 admin users, 3 batches, 5 interns with profiles, 4 published assessments with 8 pages and 40 questions, 25 attendance records, 4 DAR records, 4 projects, 5 laptops, 4 calendar events, singleton calendar and feature-access configs, and 4 notifications.
- Verified idempotency by running `python manage.py seed_dev` twice with `DEBUG=True` in the shell environment and confirming the final counts stayed at the expected totals with no duplicates.

---

## 15. deployment / prod config

**Depends on:** everything complete and tested
**Provides:** Production-ready settings, S3 file storage, Supabase DB connection

### Summary Checklist
- [x] prod.py settings complete
- [x] S3/Supabase storage configured
- [x] Environment variables documented
- [x] ALLOWED_HOSTS and CORS set
- [x] DEBUG=False verified
- [x] Verified

### Detailed Steps

- [x] **15.1** Finalize `config/settings/prod.py`
  - `DEBUG = False`
  - `ALLOWED_HOSTS` from env
  - `CORS_ALLOWED_ORIGINS` from env

- [x] **15.2** Configure database for production
  - Use Supabase pooled connection string (port 6543, `?pgbouncer=true`)
  - Use `dj-database-url` for parsing
  - Set `conn_max_age=60`

- [x] **15.3** Configure S3/Supabase Storage for file uploads
  - DAR PDFs and avatars
  - `AWS_DEFAULT_ACL = 'private'`

- [x] **15.4** Verify all env vars are documented in `.env.example`
- [x] **15.5** Run `python manage.py check --deploy` - resolve all warnings
- [x] **15.6** Run full test suite - `python manage.py test apps --verbosity=2`
- [x] **15.7** Update PLAN.md - mark deployment complete

**Notes:**
- Finalized `config/settings/prod.py` with required env validation, `DEBUG = False`, env-driven hosts/CORS/CSRF settings, HTTPS security settings, and S3-backed media storage.
- Added `dj-database-url` parsing for the Supabase pooled Postgres connection string with `conn_max_age=60`.
- Added the missing `.env.example` and `requirements.txt` files so deployment inputs and Python dependencies are documented in the repo.
- Verified production settings with `python manage.py check --deploy --settings=config.settings.prod` under explicit production env vars and ran `python manage.py test apps --verbosity=2` with 106 passing tests.

---

## 16. post-review hardening fixes

**Depends on:** completed build and review pass
**Provides:** safer production defaults, validation hardening, and regression coverage for review findings

### Summary Checklist
- [x] Secret-handling guardrails updated
- [x] Duplicate-email validation hardened
- [x] Invalid date input handling hardened
- [x] Duplicate attempt race handling hardened
- [x] Production env validation hardened
- [x] Tests added and passing
- [x] Verified

### Detailed Steps

- [x] **16.1** Add repo secret-handling guardrails
  - Update `.gitignore` to exclude `.env`, caches, local DB files, and compiled Python artifacts

- [x] **16.2** Fix duplicate-email validation paths
  - Prevent 500s on admin/intern create-update flows and registration approval
  - Return DRF validation errors instead of DB integrity errors

- [x] **16.3** Fix invalid `week_start` handling on attendance summary
  - Return 400 for malformed `YYYY-MM-DD` values instead of silently falling back

- [x] **16.4** Fix duplicate assessment-attempt race handling
  - Convert DB uniqueness collisions into a stable validation error

- [x] **16.5** Harden production env validation
  - Require non-empty production `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS`

- [x] **16.6** Add regression tests and run affected suites
  - `python manage.py test apps.accounts --verbosity=2`
  - `python manage.py test apps.interns --verbosity=2`
  - `python manage.py test apps.attendance --verbosity=2`
  - `python manage.py test apps.assessments --verbosity=2`
  - `python manage.py check --deploy --settings=config.settings.prod`

- [x] **16.7** Update PLAN.md and MEMORY.md

**Notes:**
- Added repo-level ignore rules for `.env`, compiled Python artifacts, and local SQLite files to reduce accidental secret and local-artifact commits.
- Hardened duplicate-email handling across account and intern write paths so create, update, registration, and approval flows return field-level validation errors instead of DB integrity failures.
- Updated weekly attendance summary validation to reject malformed `week_start` values with a 400 response and converted assessment-attempt uniqueness races into a stable validation error.
- Hardened production settings so `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` must be non-empty in production.
- Verified with `python manage.py test apps.accounts --verbosity=2`, `python manage.py test apps.interns --verbosity=2`, `python manage.py test apps.attendance --verbosity=2`, `python manage.py test apps.assessments --verbosity=2`, and `python manage.py check --deploy --settings=config.settings.prod`.

---

## 17. README documentation

**Depends on:** completed implementation and deployment config
**Provides:** top-level project onboarding and deployment guide

### Summary Checklist
- [x] README created
- [x] Local setup documented
- [x] Environment variables documented
- [x] Production deployment guidance documented
- [x] Internal docs references added
- [x] PLAN.md updated

### Detailed Steps

- [x] **17.1** Create top-level `README.md`
  - Project overview
  - Audience and internal-use note
  - Local setup
  - Environment configuration
  - Development commands
  - Production deployment guidance
  - References to internal docs

- [x] **17.2** Update PLAN.md

**Notes:**
- Added a full top-level `README.md` covering project overview, internal-use note, local setup, environment variables, development commands, production deployment guidance, and references to the internal documentation set.
- Documented a recommended local workflow using `venv`, `pip install -r requirements.txt`, `.env` copied from `.env.example`, migrations, `seed_dev`, and `runserver`.

---

## 18. Render deployment support

**Depends on:** completed implementation, production settings, and README
**Provides:** Render-ready runtime, static serving, and deployment configuration

### Summary Checklist
- [x] Render runtime dependencies added
- [x] Static serving configured for Render
- [x] Build and startup commands documented in repo
- [x] Render blueprint/config added
- [x] Render deployment guidance documented
- [x] Verified

### Detailed Steps

- [x] **18.1** Add Render runtime dependencies
  - Add `gunicorn`
  - Add `whitenoise`

- [x] **18.2** Configure static serving for production
  - Add WhiteNoise middleware
  - Use WhiteNoise staticfiles storage in production

- [x] **18.3** Add Render build/start config
  - Add `build.sh`
  - Add `render.yaml`

- [x] **18.4** Update README with Render deployment guidance

- [x] **18.5** Verify production config
  - Run `python manage.py check --deploy --settings=config.settings.prod`

- [x] **18.6** Update PLAN.md

**Notes:**
- Added `gunicorn` and `whitenoise` to `requirements.txt` for Render production runtime support.
- Enabled WhiteNoise middleware in base settings and switched production staticfiles storage to `CompressedManifestStaticFilesStorage`.
- Added `build.sh` and `render.yaml` so the repo includes Render-friendly build and startup commands.
- Updated `README.md` with a Render deployment section covering required environment variables and Render host examples.
- Verified production settings with `python manage.py check --deploy --settings=config.settings.prod`; the only remaining warning is `security.W021` when `SECURE_HSTS_PRELOAD` is intentionally set to `False`.

---

## Completed Tasks

- `accounts` — custom user model, JWT auth endpoints, permissions, migrations, and tests completed on 2026-03-19.
- `batches` — batch model, filterable CRUD API, intern list action scaffold, migrations, and tests completed on 2026-03-19.
- `interns` — profile and registration workflow models, services, CRUD endpoints, migrations, and tests completed on 2026-03-19.
- `assessments` — assessment authoring, publish workflow, attempt submission, scoring, migrations, and tests completed on 2026-03-19.
- `attendance` — attendance model, clock-in/out flow, summary endpoint, migrations, and tests completed on 2026-03-19.
- `dar` — DAR upload model, validation, missing-report detection, migrations, and tests completed on 2026-03-19.
- `calendar` — calendar events, holidays, singleton settings, business-day service, migrations, and tests completed on 2026-03-19.
- `leaves` — leave request workflow, business-day computation, approval/denial actions, migrations, and tests completed on 2026-03-19.
- `projects` — project CRUD, intern assignment actions, migrations, and tests completed on 2026-03-19.
- `assets` — laptop inventory, intern issue reporting, admin resolution flow, migrations, and tests completed on 2026-03-19.
- `notifications` — audience-targeted notifications, read-state tracking, migrations, and tests completed on 2026-03-19.
- `feature_access` — singleton feature toggle config, SuperAdmin API, migrations, and tests completed on 2026-03-19.
- `seed_dev` — consolidated management command, DEBUG guard, idempotent seeded dataset, and duplicate-safe verification completed on 2026-03-19.

---

## Blocked Items

> Nothing blocked. Items move here when a `[!]` is set on any step.

