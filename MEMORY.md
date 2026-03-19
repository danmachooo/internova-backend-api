# MEMORY.md — INTERNOVA Long-term Memory

> This file stores bugs, fixes, quirks, migration notes, and learned patterns for the INTERNOVA backend.
> Read this file at every session start after AGENTS.md.
> Update this file whenever a bug is fixed, a quirk is discovered, or a non-obvious pattern is established.

---

## How to Use This File

**When debugging:** Scan the Bugs & Fixes section before investigating — the issue may already be documented.
**When writing models:** Scan Known Quirks before adding any field — naming traps and conventions are recorded here.
**When running migrations:** Scan Migration Notes before applying — past conflicts and fixes are documented.
**When adding a new entry:** Add to the top of the relevant section. Use the full format below.

### Entry Format

```
### [YYYY-MM-DD] Short title
- **App:** apps/<app>
- **Severity:** Low | Medium | High
- **Description:** What happened or what was discovered
- **Root Cause:** Why it happened
- **Fix:** What was done to resolve it
- **Affected Files:** List of files touched
```

---

## Categories

1. [Bugs & Fixes](#1-bugs--fixes)
2. [Known Quirks](#2-known-quirks)
3. [Migration Notes](#3-migration-notes)
4. [Patterns Learned](#4-patterns-learned)

---

## 1. Bugs & Fixes

> Bugs that were found and fixed. Check here before investigating any error.

---

### [2026-03-19] Repo root was missing ignore rules for secrets and local artifacts

- **App:** project configuration
- **Severity:** High
- **Description:** The repository root had an empty `.gitignore`, so `.env`, local SQLite files, and compiled Python artifacts were all eligible to be committed accidentally.
- **Root Cause:** Source-control guardrails had not been added after the backend scaffold was created.
- **Fix:** Added ignore rules for `.env`, `__pycache__/`, `*.py[cod]`, `db.sqlite3`, and `test_db.sqlite3`.
- **Affected Files:** `.gitignore`

### [2026-03-19] Duplicate email writes could surface as DB integrity errors

- **App:** apps/accounts, apps/interns
- **Severity:** High
- **Description:** Account profile updates, admin user writes, intern writes, and registration approval could hit the unique `accounts_user.email` constraint and return a server error instead of a field-level validation response.
- **Root Cause:** Several write paths saved `User.email` directly without checking for an existing account first, and serializer-level uniqueness handling was inconsistent across endpoints.
- **Fix:** Added shared duplicate-email validation in serializers and services so those flows now raise DRF `ValidationError` on the `email` field before any DB constraint failure can occur.
- **Affected Files:** `apps/accounts/serializers.py`, `apps/accounts/services.py`, `apps/accounts/tests/test_views.py`, `apps/interns/serializers.py`, `apps/interns/services.py`, `apps/interns/tests/test_views.py`

### [2026-03-19] Invalid weekly attendance summary dates silently fell back to today

- **App:** apps/attendance
- **Severity:** Medium
- **Description:** `GET /api/v1/attendance/summary/weekly/?week_start=...` accepted malformed dates and returned a summary for the current week instead of rejecting the request.
- **Root Cause:** The view treated `parse_date()` failures the same as a missing query param and defaulted to `timezone.localdate()`.
- **Fix:** Added explicit validation so malformed `week_start` values now return a 400 with a field-level error.
- **Affected Files:** `apps/attendance/views.py`, `apps/attendance/tests/test_views.py`

### [2026-03-19] Assessment attempt creation race could still crash on duplicate starts

- **App:** apps/assessments
- **Severity:** Medium
- **Description:** Two near-simultaneous attempt-create requests for the same intern and assessment could bypass the pre-check and hit the DB uniqueness constraint, causing a server error.
- **Root Cause:** The view checked for an existing attempt before `objects.create()`, but the actual uniqueness guarantee lives at the database layer.
- **Fix:** Wrapped attempt creation in `IntegrityError` handling and translated duplicate-key races into the same DRF validation error used by the normal duplicate-attempt path.
- **Affected Files:** `apps/assessments/views.py`, `apps/assessments/tests/test_views.py`

### [2026-03-19] Chat was already removed from code but persisted in project docs

- **App:** project documentation
- **Severity:** Medium
- **Description:** The codebase no longer contained an `apps/chat` package, routes, or settings entries, but the master docs still described chat as an active backend feature and the plan still marked it as the current app.
- **Root Cause:** Documentation and working-memory files were not updated after the chat feature was removed from scope.
- **Fix:** Removed chat references from `AGENTS.md`, `CONTEXT.md`, `SCHEMA.md`, and `PLAN.md`, then advanced the active task tracking to `feature_access`.
- **Affected Files:** `AGENTS.md`, `CONTEXT.md`, `SCHEMA.md`, `PLAN.md`

### [2026-03-19] CalendarSettings weekend-days array SQL broke SQLite test runs

- **App:** apps/calendar
- **Severity:** High
- **Description:** The initial `CalendarSettings.weekend_days` implementation passed migrations but crashed every calendar model, service, and view test with `sqlite3.OperationalError: unrecognized token ":"`.
- **Root Cause:** Django's PostgreSQL `ArrayField` emits `::integer[]` placeholder SQL during inserts, which SQLite cannot execute in this repo's test database.
- **Fix:** Replaced the raw `ArrayField` usage with a calendar-local `SQLiteCompatibleIntegerArrayField` that keeps PostgreSQL array behavior in production while serializing to text safely on SQLite during tests.
- **Affected Files:** `apps/calendar/models.py`, `apps/calendar/migrations/0002_alter_calendarsettings_weekend_days.py`

---

### [2026-03-19] DAR missing-report action built its response through serializer input mode

- **App:** apps/dar
- **Severity:** Medium
- **Description:** `GET /api/v1/dar/missing/` crashed during tests instead of returning the list of interns missing a DAR for the requested date.
- **Root Cause:** The view instantiated a serializer in input-validation mode for a response payload, which caused an assertion failure during request handling.
- **Fix:** Replaced the serializer indirection in `apps/dar/views.py` with an explicit response payload and kept strict `YYYY-MM-DD` query parsing via `parse_date()`.
- **Affected Files:** `apps/dar/views.py`

---

### [2026-03-19] `IsAdminOrSelf` did not recognize objects owned through `intern`

- **App:** apps/accounts
- **Severity:** Medium
- **Description:** Intern users could not retrieve their own `InternAttempt` records even after the `assessments` app was scaffolded.
- **Root Cause:** `IsAdminOrSelf.has_object_permission()` only treated direct user objects and models with a `.user` relation as “self”, but `InternAttempt` is owned through its `.intern` foreign key.
- **Fix:** Extended `IsAdminOrSelf` in `apps/accounts/permissions.py` to allow objects with an `.intern` attribute when it matches `request.user`.
- **Affected Files:** `apps/accounts/permissions.py`

---

### [2026-03-19] Custom User inherited Django `last_login` unexpectedly

- **App:** apps/accounts
- **Severity:** High
- **Description:** The initial custom `User` model inherited Django's built-in `last_login` field, which would have created an extra database column not defined in `SCHEMA.md`.
- **Root Cause:** `AbstractBaseUser` includes a nullable `last_login` field by default. Without explicitly disabling it, Django adds it to the model even when the project intends to use only `last_login_at`.
- **Fix:** Set `last_login = None` on `apps/accounts/models.py` and kept `last_login_at` as the only login timestamp field used by the service and API layer.
- **Affected Files:** `apps/accounts/models.py`, `apps/accounts/migrations/0001_initial.py`

---

### [2026-03-19] Strict DEBUG parsing broke startup when shell env used non-boolean values

- **App:** config/settings
- **Severity:** Medium
- **Description:** `python manage.py check` failed during settings import with `ValueError: Invalid truth value: release`, so Django could not boot even though the repo `.env` file had a valid boolean value.
- **Root Cause:** `python-decouple` boolean casting used a shell-level `DEBUG=release` value from the wider environment, and the direct `cast=bool` parsing was too strict for this workspace.
- **Fix:** Replaced the strict cast with a tolerant `env_flag()` helper in `config/settings/base.py` so settings startup treats only standard truthy strings as `True` and safely falls back to `False` otherwise.
- **Affected Files:** `config/settings/base.py`

---

### [2026-03-19] Circular import between cross-app services

- **App:** Any app that calls `NotificationService`, `CalendarService`, or other cross-app services
- **Severity:** High
- **Description:** `ImportError: cannot import name 'X' from partially initialized module` when one service imports another service at the module level and a transitive dependency creates a cycle.
- **Root Cause:** Module-level cross-app imports in `services.py` cause circular dependencies when Django initializes apps. e.g. `apps/leaves/services.py` importing `from apps.notifications.services import NotificationService` at the top of the file.
- **Fix:** Move all cross-app service imports inside the function body where they are used — not at the module level.
- **Affected Files:** Any `services.py` that imports from another app's `services.py`

```python
# ❌ WRONG — module-level import
from apps.notifications.services import NotificationService

class LeaveService:
    @staticmethod
    def approve(leave, decided_by):
        NotificationService.push(...)

# ✅ CORRECT — function-level import
class LeaveService:
    @staticmethod
    def approve(leave, decided_by):
        from apps.notifications.services import NotificationService
        NotificationService.push(...)
```

---

### [2026-03-19] Using start_date / end_date on LeaveRequest causes field errors

- **App:** apps/leaves
- **Severity:** High
- **Description:** `FieldError: Cannot resolve keyword 'start_date' into field` or silent data errors when filtering or serializing `LeaveRequest`.
- **Root Cause:** The leave fields were renamed during schema v2. The correct field names are `from_date` and `to_date`. Using the old names `start_date` / `end_date` causes ORM errors or serializer mismatches.
- **Fix:** Always use `from_date` and `to_date` on `LeaveRequest`. Search codebase for `start_date` and `end_date` references in `apps/leaves/` and replace.
- **Affected Files:** `apps/leaves/models.py`, `apps/leaves/serializers.py`, `apps/leaves/filters.py`, `apps/leaves/views.py`

---

### [2026-03-19] Score accepted from client on assessment submit

- **App:** apps/assessments
- **Severity:** High
- **Description:** If `score` is included in the submit request body and the serializer does not explicitly mark it as `read_only`, DRF will accept and overwrite the computed score with the client-supplied value.
- **Root Cause:** Missing `read_only_fields` declaration on `InternAttemptSerializer`.
- **Fix:** Mark `score`, `completed`, and `completed_at` as `read_only` on `InternAttemptSerializer`. Score is always computed in `AssessmentService.submit()`.
- **Affected Files:** `apps/assessments/serializers.py`

```python
class InternAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternAttempt
        fields = '__all__'
        read_only_fields = ['id', 'score', 'completed', 'completed_at', 'created_at']
```

---

### [2026-03-19] correct_index exposed to interns via shared serializer

- **App:** apps/assessments
- **Severity:** High
- **Description:** `correct_index` appeared in the intern-facing assessment API response when a single serializer was used for both admins and interns.
- **Root Cause:** Using `AssessmentQuestionAdminSerializer` (which includes `correct_index`) for all roles instead of switching based on `request.user.role`.
- **Fix:** Use split serializers. Interns always receive `AssessmentQuestionSerializer` (no `correct_index`). Admins receive `AssessmentQuestionAdminSerializer`. Switch in `get_serializer_class()`.
- **Affected Files:** `apps/assessments/serializers.py`, `apps/assessments/views.py`

---

## 2. Known Quirks

> Non-obvious project-specific behaviors, naming conventions, and gotchas that are easy to get wrong.

---

### Batch interns action is intentionally empty until interns app exists

- **App:** apps/batches
- **Quirk:** `GET /api/v1/batches/{id}/interns/` currently returns `[]` while the `interns` app is not yet scaffolded.
- **Why:** The build order places `batches` before `interns`, but the endpoint belongs to the `batches` API contract. The implementation uses a safe service fallback so the app can be completed without violating the one-app-at-a-time rule.
- **Rule:** Keep the fallback in `apps/batches/services.py` until `apps/interns` exists, then replace it with a real `InternProfile` query using `select_related('user')` when Step 3 is implemented.

---

### Attendance service owns InternProfile rendered-hours syncing

- **App:** apps/attendance, apps/interns
- **Quirk:** `InternProfile.rendered_hours` is not updated directly by intern/profile views. It is synchronized from attendance totals whenever attendance records are created, updated, clocked in, or clocked out.
- **Why:** `rendered_hours` is a denormalized aggregate of attendance data, so letting other apps edit it directly would drift from the real attendance history.
- **Rule:** Always let `AttendanceService._sync_rendered_hours()` update `InternProfile.rendered_hours`, and keep the cross-app `InternProfile` import inside the attendance service method body to avoid circular imports.

---

### Leave request date field names are non-standard

- **App:** apps/leaves
- **Quirk:** `LeaveRequest` uses `from_date` and `to_date` — not `start_date` and `end_date` which is the more common Django convention.
- **Why:** Schema was updated in v2 to match the frontend mock store naming. The rename is intentional and permanent.
- **Rule:** Always use `from_date` / `to_date` everywhere — models, serializers, filters, views, tests.

---

### intern_role on InternProfile is intentionally NULL

- **App:** apps/interns
- **Quirk:** `InternProfile.intern_role` has no default value and is `null=True`. This is intentional — not a missing field.
- **Why:** Role is assigned by admin after reviewing assessment scores. An intern who just registered and got approved has no role yet.
- **Rule:** Never add a default to `intern_role`. Never assume it is set. Always handle `None` when reading it.

---

### CalendarSettings uses JS weekday convention, not Python

- **App:** apps/calendar
- **Quirk:** `CalendarSettings.weekend_days` stores weekday integers using the JavaScript `getUTCDay()` convention: `0 = Sunday`, `6 = Saturday`. Python's `date.weekday()` uses `0 = Monday`, `6 = Sunday`.
- **Why:** The mock store frontend used JavaScript's convention and the data was migrated as-is.
- **Rule:** Always normalize through `CalendarService`. Never compare `weekend_days` values directly against `date.weekday()`. Use the `JS_TO_PYTHON` map in `CalendarService.is_weekend()`.

```python
JS_TO_PYTHON = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
python_weekend = {JS_TO_PYTHON[d] for d in settings.weekend_days}
return date.weekday() in python_weekend
```

---

### Singletons always use pk=1 — never .first() or .create()

- **App:** apps/calendar, apps/feature_access
- **Quirk:** `CalendarSettings` and `FeatureAccessConfig` are singleton models. They always have exactly one row with `pk=1`.
- **Rule:**
  - Always access via `Model.get()` classmethod — never `.objects.first()` or `.objects.all()[0]`
  - Always update via `update_or_create(pk=1, defaults={...})` — never `.create()`
- Enforce `self.pk = 1` in `save()` so accidental creates are corrected

---

### Leave notifications may be a no-op until the notifications app exists

- **App:** apps/leaves, apps/notifications
- **Quirk:** `LeaveService.approve()` and `LeaveService.deny()` are written to trigger notifications, but the current scaffold uses a guarded function-level import so the leaves app still works before `apps/notifications` is built.
- **Why:** Build order places `leaves` before `notifications`, and hard-importing `NotificationService` would break this app before Step 11.
- **Rule:** Keep the guarded function-level import in `apps/leaves/services.py` until the notifications app is scaffolded, then replace the no-op fallback with the real `NotificationService.push()` flow.

---

### Registration request uses make_password not set_password

- **App:** apps/interns
- **Quirk:** `InternRegistrationRequest` stores a hashed password before a `User` instance exists. Django's `set_password()` requires a `User` instance — it cannot be used here.
- **Rule:** Use `django.contrib.auth.hashers.make_password(raw_password)` when hashing the password on `InternRegistrationRequest`. Use `User.set_password()` only after the `User` object is created during approval.
- **Affected Files:** `apps/interns/models.py` or `apps/interns/serializers.py` (wherever the password is saved)

---

### company_account_password must never appear in serializer output

- **App:** apps/interns
- **Quirk:** `InternProfile.company_account_password` is a display-only IT-issued credential. It must never be returned in any API response.
- **Rule:** Always exclude `company_account_password` from serializer `fields` lists, or mark `write_only=True`. Double-check on both `InternListSerializer` and `InternDetailSerializer`.

---

### assessment_score on InternProfile is a denormalized aggregate

- **App:** apps/interns, apps/assessments
- **Quirk:** `InternProfile.assessment_score` is not computed on the fly — it is stored and updated by `AssessmentService._update_intern_aggregate()` after every attempt submission.
- **Rule:** Never update `assessment_score` directly in a view or serializer. Never compute it inline in a queryset annotation as the primary value. Always trigger the update through `AssessmentService._update_intern_aggregate(intern)` after any attempt is submitted or modified.

---

### business_days on LeaveRequest is always server-computed

- **App:** apps/leaves
- **Quirk:** `LeaveRequest.business_days` looks like a regular integer field but is never accepted from the client. It is computed on submission using `CalendarService.count_business_days()`.
- **Rule:** Mark `business_days` as `read_only` on `LeaveRequestSerializer`. Compute it in `serializer.create()` before saving.

---

### Notifications must always go through NotificationService.push()

- **App:** apps/notifications
- **Quirk:** `Notification` objects must never be created directly with `Notification.objects.create()` in views or other services.
- **Rule:** Always use `NotificationService.push(title, message, audience, type)`. This ensures consistent structure and makes it easy to swap delivery mechanisms (e.g. adding WebSockets later) without touching every caller.

---

### seed_dev must be idempotent

- **App:** apps/accounts (management command)
- **Quirk:** Running `python manage.py seed_dev` twice on the same database must produce identical results — no duplicate records, no errors.
- **Rule:** Use `get_or_create()` for every record in the seed command. Never use `create()`. Test idempotency by running the command twice in sequence.

---

## 3. Migration Notes

> Migration-specific issues, conflicts, and resolutions. Check here before running makemigrations.

---

### [2026-03-19] Schema v2 — fields renamed and tables replaced

- **App:** apps/interns, apps/leaves, apps/assessments
- **Description:** Schema was updated from v1 to v2 during initial design. Several breaking changes were made before any migrations were run, so no migration conflict exists. However, these renames must never be reversed.
- **Changes:**
  - `interns_internregistrationrequest` — old `interns_assessmentresult` table removed entirely, replaced by `assessments_*` tables
  - `leaves_leaverequest` — `start_date` renamed to `from_date`, `end_date` renamed to `to_date`
  - `interns_internprofile.intern_role` — changed from `NOT NULL` to `NULL`
- **Rule:** If any migration is generated that reverses these (e.g. renames `from_date` back to `start_date`), stop immediately and report to developer.

---

### AUTH_USER_MODEL must be set before first migration

- **App:** apps/accounts, config/settings
- **Description:** `AUTH_USER_MODEL = 'accounts.User'` must be set in `config/settings/base.py` before running any migration in any app. If this is missing, Django will create auth tables using its default User model and a reset will be required.
- **Rule:** Confirm `AUTH_USER_MODEL` is set before running `makemigrations` for the first time. Run `python manage.py check` — it will warn if this is missing.

---

### django.contrib.postgres required for ArrayField

- **App:** apps/calendar
- **Description:** `CalendarSettings.weekend_days` uses `ArrayField(models.IntegerField())` which requires `django.contrib.postgres` in `INSTALLED_APPS`.
- **Fix:** Add `'django.contrib.postgres'` to `DJANGO_APPS` in `config/settings/base.py` before generating the calendar migration.
- **Affected Files:** `config/settings/base.py`

---

## 4. Patterns Learned

> Reusable patterns established in this project. Reference when writing new code.

---

### Split serializers for role-sensitive fields

When a model has fields that must be hidden from certain roles, use two serializers switched in `get_serializer_class()`.

```python
def get_serializer_class(self):
    if self.request.user.role == RoleChoices.INTERN:
        return SafeSerializer       # hides sensitive fields
    return AdminSerializer          # includes all fields
```

**Applies to:** `AssessmentQuestion` (`correct_index`), `InternProfile` (`company_account_password`)

---

### Role-based get_queryset filtering

Interns should only see their own records. Admins see all. Always implement this in `get_queryset()` — never in the view action.

```python
def get_queryset(self):
    user = self.request.user
    if user.role == RoleChoices.INTERN:
        return Model.objects.filter(intern=user).order_by('-created_at')
    return Model.objects.select_related('intern').order_by('-created_at')
```

**Applies to:** `LeaveRequest`, `AttendanceRecord`, `DailyActivityReport`, `LaptopIssueReport`, `InternAttempt`

---

### @transaction.atomic on all multi-step service writes

Any service method that writes to more than one table must be wrapped in `@transaction.atomic`. This ensures partial writes are rolled back on failure.

```python
@staticmethod
@transaction.atomic
def approve_registration(reg_id, decided_by):
    # Creates User + InternProfile + updates Registration in one atomic block
    ...
```

**Applies to:** `InternService.approve_registration()`, `LeaveService.approve()`, `LeaveService.deny()`, `AssessmentService.submit()`

---

### Function-level imports for cross-app services

All imports of services from other apps must be done at the function level — never at the module level — to avoid circular imports.

```python
# Inside the function, not at the top of the file
def approve(leave, decided_by):
    from apps.notifications.services import NotificationService
    NotificationService.push(...)
```

**Applies to:** Any service that calls `NotificationService`, `CalendarService`, or any other cross-app service.

---

### Singleton access pattern

Both `CalendarSettings` and `FeatureAccessConfig` follow the same singleton pattern.

```python
class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
```

**Applies to:** `apps/calendar/models.py`, `apps/feature_access/models.py`

---

### perform_create for injecting request.user

Use `perform_create()` on ViewSets to inject the authenticated user as a field — never rely on the client sending it.

```python
def perform_create(self, serializer):
    serializer.save(intern=self.request.user)
```

**Applies to:** `DARViewSet`, `LaptopIssueReportViewSet`, `LeaveRequestViewSet`, `InternAttemptViewSet`

---

### save(update_fields=[...]) for all partial updates

Never call `.save()` with no arguments on an existing record unless all fields need updating. Always specify `update_fields` to avoid overwriting unrelated fields and triggering unnecessary signals.

```python
# ✅ Always do this for partial updates
leave.status = LeaveStatusChoices.APPROVED
leave.decided_at = timezone.now()
leave.save(update_fields=['status', 'decided_at', 'decided_by'])
```

**Applies to:** All service methods that update existing records.
