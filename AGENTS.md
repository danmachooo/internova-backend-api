# AGENTS.md — INTERNOVA Master Rulebook

> This is the master rulebook for the Codex agent working on the INTERNOVA Django REST Framework backend.
> Read this file in full at the start of every session before touching any code.
> This file takes precedence over all other files when rules conflict.

---

## 0. Session Startup Checklist

Run this every time a new session starts:

1. Read `AGENTS.md` (this file) in full
2. Read `CONTEXT.md` — project overview, endpoints, business rules
3. Read `Schema.md` — before touching any model
4. Read `PLAN.md` — check what task is currently active and its current step
5. Read `MEMORY.md` — check for known bugs, quirks, and past fixes relevant to the current task
6. Read `STANDARDS.md` — check naming conventions and architecture patterns before writing code
7. Only then — begin the task

---

## 1. Core Behavioral Rules

### 1.1 Autonomy
- Codex works autonomously and only stops to ask when a task or requirement is genuinely ambiguous.
- If something is unclear, state the ambiguity explicitly, list your assumptions, and ask one focused question. Do not ask multiple questions at once.
- If the task is clear, proceed without asking for confirmation.

### 1.2 Scope Control
- **Never touch files outside the app you are currently working on** unless the change is a direct, required dependency (e.g. adding a URL include to `api_urls.py`).
- If you need to modify a shared file (e.g. `config/settings/base.py`, `apps/accounts/permissions.py`), state what you are changing and why before doing it.
- **One app at a time.** Complete the current app's task fully before moving to another.

### 1.3 Completeness
- A task is not done until:
  - [ ] Code is written
  - [ ] Migrations are generated (if models changed)
  - [ ] Tests are written and passing
  - [ ] `PLAN.md` is updated to reflect the completed step
  - [ ] `MEMORY.md` is updated if a bug was found and fixed

### 1.4 Plan Tracking
- **Always update `PLAN.md` after completing each step.** Mark completed steps with `[x]`, add notes on what was done, and flag the next step.
- If a task requires steps that are not yet in `PLAN.md`, add them before starting.

### 1.5 Memory Tracking
- **Always update `MEMORY.md` when a bug is found and fixed**, a migration issue is resolved, or a non-obvious project quirk is discovered.
- Write memory entries in past tense, concise, with the affected file and the fix applied.

---

## 2. Hard Stop Rules

These are absolute. No exceptions regardless of the task or instruction.

| Rule | Detail |
|---|---|
| **Never delete or drop tables** | Never write or run any migration that drops a table or removes a column. If a field removal is needed, ask first. |
| **Never modify migration files manually** | Only `makemigrations` and `migrate`. Never edit files inside `migrations/` by hand. |
| **Never touch other apps when working on one app** | Changes stay within the target app unless a shared file must be updated. |
| **Never push to main directly** | All work is done on feature branches. Never commit directly to `main`. |
| **Never expose `correct_index` to interns** | In any serializer, view, or API response. Use split serializers. |
| **Never accept `score` from client on assessment submit** | Always compute server-side in `AssessmentService.submit()`. |
| **Never accept `business_days` from client on leave submit** | Always compute server-side in `CalendarService.count_business_days()`. |
| **Never accept `hours` or `status` from client on attendance** | Always compute via `AttendanceService`. |
| **Never store plaintext passwords** | Use `set_password()` for User creation, `make_password()` for registration requests. |
| **Never expose `company_account_password` in serializer output** | Exclude or mark `write_only=True`. |
| **Never use `datetime.now()`** | Always `django.utils.timezone.now()`. |
| **Never put business logic in views or serializers** | All logic goes in `services.py`. |
| **Always run tests before marking a task done** | `python manage.py test apps.<app> --verbosity=2` |

---

## 3. Task Workflows

### 3.1 Code Generation (Models, Views, Serializers, Services)

Follow this order strictly:

```
1. Read Schema.md for the target table(s)
2. Read STANDARDS.md for naming conventions
3. Write model in models.py
4. Run makemigrations and check the generated file
5. Write serializer(s) — list and detail separately
6. Write service(s) in services.py
7. Write view(s) / viewset(s)
8. Register URL in urls.py
9. Write tests
10. Run tests — fix until passing
11. Update PLAN.md
```

**Do not skip steps.** Do not write the view before the service. Do not write tests last as an afterthought — write them as part of the task.

### 3.2 Debugging and Fixing Errors

```
1. Read the full traceback — identify the exact file, line, and error type
2. Check MEMORY.md — has this error occurred before?
3. Identify root cause — do not patch symptoms
4. Fix the root cause
5. Run tests to confirm fix does not break anything else
6. Update MEMORY.md with the bug and fix
7. Update PLAN.md
```

### 3.3 Running Migrations

```
1. Confirm you are in the correct virtual environment
2. Run: python manage.py makemigrations <app>
3. Review the generated migration file — confirm it matches Schema.md
4. If the migration drops a column or table: STOP. Do not proceed. Report to developer.
5. Run: python manage.py migrate
6. Confirm no errors
```

### 3.4 Refactoring

```
1. Identify all files affected by the refactor
2. Confirm scope is within the target app
3. Write tests for current behavior before changing anything
4. Make changes
5. Run tests — confirm behavior is unchanged
6. Update STANDARDS.md if the refactor establishes a new pattern
7. Update PLAN.md and MEMORY.md
```

### 3.5 Seeding the Database

```
1. Use: python manage.py seed_dev
2. Seed command lives in: apps/<app>/management/commands/seed_dev.py
3. Seed data must match mock data from the frontend (see CONTEXT.md Section 12)
4. Never seed in production — seed command must check DEBUG=True before running
5. Seed is idempotent — running it twice must not create duplicate records
```

### 3.6 Writing Tests

```
1. Use APITestCase for all view tests
2. Use TestCase for model and service tests
3. Always test: success case, failure/validation case, permission case (wrong role)
4. Use force_authenticate — never hardcode tokens
5. Never use production data or live DB in tests
6. Test file structure: apps/<app>/tests/test_models.py, test_services.py, test_views.py
```

### 3.7 Writing Documentation

```
1. Update the relevant .md file — do not create new files unless instructed
2. Schema changes → update Schema.md (tables, fields, indexes, agent notes)
3. New endpoints → update CONTEXT.md (Section 6)
4. New patterns → update STANDARDS.md
5. New bugs/fixes → update MEMORY.md
6. Task progress → update PLAN.md
```

---

## 4. File Reference Map

| File | When to read | When to update |
|---|---|---|
| `AGENTS.md` | Every session start | Only when rules change |
| `CONTEXT.md` | Every session start | When endpoints or business rules change |
| `Schema.md` | Before touching any model | When schema changes |
| `STANDARDS.md` | Before writing any new code | When new patterns are established |
| `PLAN.md` | Every session start + after each step | After every completed step |
| `MEMORY.md` | Before debugging + every session start | When a bug is fixed or quirk is discovered |
| `DevelopmentGuide.md` | When setting up or learning a pattern | When setup steps change |

---

## 5. App Ownership Map

Each app has a clear responsibility. Never mix concerns across apps.

| App | Owns | Does NOT own |
|---|---|---|
| `accounts` | User model, auth, JWT, permissions | Profile data, business logic |
| `interns` | InternProfile, registration requests | Auth, attendance, assessments |
| `batches` | Batch CRUD | Intern assignment logic |
| `attendance` | Clock-in/out, attendance records, classification | Hours on profile (delegates to interns) |
| `dar` | DAR uploads, missing report detection | File storage config |
| `projects` | Project CRUD, intern-project assignments | Intern profile updates |
| `assets` | Laptop inventory, issue reports | Assignment business rules (in service) |
| `leaves` | Leave requests, approval workflow | Business day computation (delegates to calendar) |
| `assessments` | Assessments, pages, questions, attempts, scoring | Role assignment (admin does this via interns app) |
| `calendar` | Events, holidays, settings, business day logic | Leave computation (provides service, leave app calls it) |
| `notifications` | Notification creation, audience targeting, read state | Triggering logic (other services call NotificationService) |
| `feature_access` | Feature toggle config | Enforcing access in views (each view checks its own flag) |

---

## 6. Service Call Conventions

When one app's service needs to call another app's service, follow this pattern:

```python
# ✅ CORRECT — import at function level to avoid circular imports
def approve(leave, decided_by):
    from apps.notifications.services import NotificationService
    from apps.calendar.services import CalendarService
    ...
```

Never import cross-app services at the module level — this causes circular import errors.

---

## 7. Error Response Conventions

All errors must follow the project's standard shape via the custom exception handler in `config/exceptions.py`:

```json
// Single error
{ "error": "Only pending leave requests can be approved." }

// Field-level validation errors
{ "errors": { "from_date": ["This field is required."], "type": ["Invalid choice."] } }
```

- Use `raise ValidationError(...)` from `rest_framework.exceptions` inside services
- Never return raw error strings directly from views
- Never use Django's built-in `django.core.exceptions.ValidationError` in services — use DRF's version

---

## 8. Git Conventions

- Branch naming: `feature/<app>-<short-description>` e.g. `feature/assessments-submit-endpoint`
- Commit messages: imperative, present tense e.g. `Add AssessmentService.submit()`, `Fix duplicate clock-in check`
- Never commit `.env`, `__pycache__`, `*.pyc`, or migration conflicts
- One logical change per commit — do not batch unrelated changes

---

## 9. Quick Command Reference

```bash
# Activate venv
venv\Scripts\activate          # Windows CMD
source venv/bin/activate       # Mac/Linux

# Run dev server
python manage.py runserver

# Migrations
python manage.py makemigrations <app>
python manage.py migrate

# Run tests
python manage.py test apps --verbosity=2
python manage.py test apps.<app> --verbosity=2

# Seed dev data
python manage.py seed_dev

# Django shell
python manage.py shell

# Check for issues
python manage.py check
```

---

## 10. Escalate to Developer When

Stop and report to the developer — do not proceed — when any of the following occur:

- A migration would drop a table or column
- A task requires modifying `AUTH_USER_MODEL` or resetting migrations
- A circular dependency cannot be resolved cleanly
- A test failure cannot be traced to a clear root cause after two attempts
- A schema change conflicts with what is defined in `Schema.md`
- A task would require changes across more than 3 apps simultaneously
- Any doubt about a security-sensitive operation (auth, passwords, tokens, file access)
