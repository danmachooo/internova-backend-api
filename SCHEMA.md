# INTERNOVA — Schema.md

> Database schema reference for the INTERNOVA Django REST Framework backend.
> All tables use PostgreSQL. UUIDs are used as primary keys on all models except singletons.

---

## Table of Contents

1. [accounts_user](#1-accounts_user)
2. [interns_internprofile](#2-interns_internprofile)
3. [interns_internregistrationrequest](#3-interns_internregistrationrequest)
4. [batches_batch](#4-batches_batch)
5. [attendance_attendancerecord](#5-attendance_attendancerecord)
6. [dar_dailyactivityreport](#6-dar_dailyactivityreport)
7. [projects_project](#7-projects_project)
8. [projects_project_assigned_interns](#8-projects_project_assigned_interns)
9. [assets_laptop](#9-assets_laptop)
10. [assets_laptopissuereport](#10-assets_laptopissuereport)
11. [leaves_leaverequest](#11-leaves_leaverequest)
12. [assessments_assessment](#12-assessments_assessment)
13. [assessments_assessmentpage](#13-assessments_assessmentpage)
14. [assessments_assessmentquestion](#14-assessments_assessmentquestion)
15. [assessments_internattempt](#15-assessments_internattempt)
16. [calendar_calendarevent](#16-calendar_calendarevent)
17. [calendar_holiday](#17-calendar_holiday)
18. [calendar_calendarsettings](#18-calendar_calendarsettings)
19. [notifications_notification](#19-notifications_notification)
20. [notifications_notificationreadstate](#20-notifications_notificationreadstate)
21. [feature_access_featureaccessconfig](#21-feature_access_featureaccessconfig)
22. [Relationship Diagram](#22-relationship-diagram)
23. [Changelog](#23-changelog)

---

## 1. accounts_user

Primary user table. Stores all user types — superadmin, staffadmin, and intern.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| email | VARCHAR(254) | UNIQUE, NOT NULL | Login identifier |
| name | VARCHAR(255) | NOT NULL | Full name |
| password | VARCHAR(128) | NOT NULL | Hashed by Django (PBKDF2) |
| role | VARCHAR(20) | NOT NULL | superadmin \| staffadmin \| intern |
| status | VARCHAR(20) | NOT NULL, default='active' | active \| inactive |
| last_login_at | TIMESTAMPTZ | NULL | Updated on successful login |
| is_active | BOOLEAN | NOT NULL, default=TRUE | Django internal — controls login access |
| is_staff | BOOLEAN | NOT NULL, default=FALSE | Django admin site access |
| created_at | TIMESTAMPTZ | NOT NULL, auto | |
| updated_at | TIMESTAMPTZ | NOT NULL, auto | |

**Indexes:**
- `accounts_user_email_idx` on `email`
- `accounts_user_role_idx` on `role`
- `accounts_user_status_idx` on `status`

---

## 2. interns_internprofile

Extended profile data for users with `role='intern'`. One-to-one with `accounts_user`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| user_id | UUID | FK → accounts_user(id), UNIQUE, NOT NULL, ON DELETE CASCADE | |
| batch_id | UUID | FK → batches_batch(id), NULL, ON DELETE SET NULL | |
| school | VARCHAR(255) | NOT NULL | |
| intern_role | VARCHAR(50) | NULL | Set by admin after reviewing assessment scores. Developer \| Quality Assurance \| Project Manager \| Business Analyst |
| phone | VARCHAR(20) | NOT NULL | |
| github_username | VARCHAR(100) | NULL | Optional GitHub handle |
| required_hours | DECIMAL(6,2) | NOT NULL, default=480.00 | Target OJT hours |
| rendered_hours | DECIMAL(6,2) | NOT NULL, default=0.00 | Stored or computed from attendance |
| start_date | DATE | NOT NULL | |
| birthdate | DATE | NOT NULL | |
| avatar | VARCHAR(255) | NULL | File path: avatars/{user_id}.{ext} |
| company_account_email | VARCHAR(254) | NULL | IT-issued account email (display only, not used for auth) |
| company_account_password | VARCHAR(255) | NULL | IT-issued account password (display only, not used for auth) |
| assessment_required | BOOLEAN | NOT NULL, default=TRUE | Whether intern must complete assessments |
| assessment_completed_at | TIMESTAMPTZ | NULL | Timestamp when intern completed all assessments |
| assessment_score | DECIMAL(5,2) | NULL | Overall average score across all assessment attempts |

**Notes:**
- `intern_role` is NULL until the admin manually assigns it after reviewing assessment results.
- `assessment_score` is an aggregate convenience field. Per-assessment scores live in `assessments_internattempt`.

**Indexes:**
- `interns_profile_user_idx` on `user_id`
- `interns_profile_batch_idx` on `batch_id`
- `interns_profile_role_idx` on `intern_role`

---

## 3. interns_internregistrationrequest

Pending registration requests submitted by prospective interns before approval.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| name | VARCHAR(255) | NOT NULL | |
| email | VARCHAR(254) | NOT NULL | |
| password | VARCHAR(128) | NOT NULL | Hashed on save — used to create User on approval |
| github_username | VARCHAR(100) | NULL | Optional GitHub handle |
| school | VARCHAR(255) | NOT NULL | |
| phone | VARCHAR(20) | NOT NULL | |
| birthdate | DATE | NOT NULL | |
| start_date | DATE | NOT NULL | |
| required_hours | INTEGER | NOT NULL, default=480 | |
| status | VARCHAR(20) | NOT NULL, default='pending' | pending \| approved \| denied |
| created_at | TIMESTAMPTZ | NOT NULL, auto | |
| decided_at | TIMESTAMPTZ | NULL | Set on approve/deny |
| intern_id | UUID | FK → accounts_user(id), NULL, ON DELETE SET NULL | Set on approval |

**Indexes:**
- `interns_reg_status_idx` on `status`
- `interns_reg_email_idx` on `email`

---

## 4. batches_batch

Groups of interns per intake period.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| name | VARCHAR(100) | NOT NULL | e.g. "Batch 2024-A" |
| start_date | DATE | NOT NULL | |
| end_date | DATE | NOT NULL | |
| status | VARCHAR(20) | NOT NULL, default='active' | active \| completed |
| progress | INTEGER | NOT NULL, default=0 | 0–100; computed or stored |

**Indexes:**
- `batches_batch_status_idx` on `status`

---

## 5. attendance_attendancerecord

Daily attendance records per intern.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| intern_id | UUID | FK → accounts_user(id), NOT NULL, ON DELETE CASCADE | |
| date | DATE | NOT NULL | |
| login_time | TIME | NULL | |
| logout_time | TIME | NULL | |
| hours | DECIMAL(5,2) | NOT NULL, default=0.00 | Computed: logout_time - login_time |
| status | VARCHAR(20) | NOT NULL | present \| late \| absent \| overtime \| undertime |

**Constraints:**
- `UNIQUE (intern_id, date)`

**Indexes:**
- `attendance_intern_idx` on `intern_id`
- `attendance_date_idx` on `date`
- `attendance_status_idx` on `status`
- `attendance_intern_date_idx` on `(intern_id, date)`

---

## 6. dar_dailyactivityreport

Daily Activity Report PDF submissions per intern per day.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| intern_id | UUID | FK → accounts_user(id), NOT NULL, ON DELETE CASCADE | |
| date | DATE | NOT NULL | |
| file | VARCHAR(255) | NULL | File path: dar/{intern_id}/{date}_{filename}.pdf |
| upload_time | TIME | NULL | Set on file upload |
| status | VARCHAR(20) | NOT NULL, default='missing' | submitted \| missing |

**Constraints:**
- `UNIQUE (intern_id, date)`

**Indexes:**
- `dar_intern_idx` on `intern_id`
- `dar_date_idx` on `date`
- `dar_status_idx` on `status`

---

## 7. projects_project

Projects assigned to interns.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| name | VARCHAR(255) | NOT NULL | |
| description | TEXT | NOT NULL, default='' | |
| status | VARCHAR(20) | NOT NULL, default='active' | active \| on_hold \| completed |
| start_date | DATE | NOT NULL | |
| end_date | DATE | NOT NULL | |

**Indexes:**
- `projects_status_idx` on `status`

---

## 8. projects_project_assigned_interns

Join table for the ManyToMany between `projects_project` and `accounts_user`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | BIGINT | PK, auto-increment | Django default M2M PK |
| project_id | UUID | FK → projects_project(id), NOT NULL, ON DELETE CASCADE | |
| user_id | UUID | FK → accounts_user(id), NOT NULL, ON DELETE CASCADE | |

**Constraints:**
- `UNIQUE (project_id, user_id)`

---

## 9. assets_laptop

Laptop and device inventory.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| brand | VARCHAR(100) | NOT NULL | e.g. "MacBook Pro 14\"" |
| serial_no | VARCHAR(100) | UNIQUE, NOT NULL | |
| ip_address | INET | NULL | PostgreSQL INET type via GenericIPAddressField |
| assigned_to_id | UUID | FK → accounts_user(id), NULL, ON DELETE SET NULL | NULL = unassigned |
| status | VARCHAR(20) | NOT NULL, default='available' | assigned \| available \| issued |
| accounts | VARCHAR(100) | NOT NULL, default='' | Local/Windows account label |

**Indexes:**
- `assets_laptop_status_idx` on `status`
- `assets_laptop_assigned_idx` on `assigned_to_id`

---

## 10. assets_laptopissuereport

Issue reports filed by interns for their assigned laptop. Accessible via the `laptopIssue` intern feature.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| intern_id | UUID | FK → accounts_user(id), NOT NULL, ON DELETE CASCADE | Intern who filed the report |
| laptop_id | UUID | FK → assets_laptop(id), NOT NULL, ON DELETE CASCADE | |
| description | TEXT | NOT NULL | What happened / what the issue is |
| status | VARCHAR(20) | NOT NULL, default='open' | open \| in_progress \| resolved |
| admin_note | VARCHAR(500) | NULL | Admin response or resolution note |
| resolved_by_id | UUID | FK → accounts_user(id), NULL, ON DELETE SET NULL | Admin who resolved |
| created_at | TIMESTAMPTZ | NOT NULL, auto | |
| resolved_at | TIMESTAMPTZ | NULL | |

**Indexes:**
- `laptop_issue_intern_idx` on `intern_id`
- `laptop_issue_laptop_idx` on `laptop_id`
- `laptop_issue_status_idx` on `status`

---

## 11. leaves_leaverequest

Leave requests submitted by interns.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| intern_id | UUID | FK → accounts_user(id), NOT NULL, ON DELETE CASCADE | |
| from_date | DATE | NOT NULL | Start of leave period |
| to_date | DATE | NOT NULL | End of leave period |
| business_days | INTEGER | NOT NULL, default=0 | Pre-computed business days for the leave period |
| type | VARCHAR(20) | NOT NULL | sick \| vacation \| emergency \| other |
| reason | TEXT | NOT NULL | |
| status | VARCHAR(20) | NOT NULL, default='pending' | pending \| approved \| denied |
| admin_note | VARCHAR(500) | NULL | Admin note on approve/deny decision |
| created_at | TIMESTAMPTZ | NOT NULL, auto | |
| decided_at | TIMESTAMPTZ | NULL | |
| decided_by_id | UUID | FK → accounts_user(id), NULL, ON DELETE SET NULL | Admin who approved/denied |

**Indexes:**
- `leaves_intern_idx` on `intern_id`
- `leaves_status_idx` on `status`
- `leaves_type_idx` on `type`

---

## 12. assessments_assessment

One assessment per skill area (e.g. Frontend, Backend, QA, Business Analysis). Admins create and publish assessments. Interns take all published assessments after their registration is approved.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| title | VARCHAR(255) | NOT NULL | e.g. "Frontend Developer Assessment" |
| description | TEXT | NOT NULL, default='' | |
| is_published | BOOLEAN | NOT NULL, default=FALSE | Only published assessments are visible to interns |
| published_at | TIMESTAMPTZ | NULL | Set when admin publishes |
| updated_at | TIMESTAMPTZ | NOT NULL, auto | |
| created_by_id | UUID | FK → accounts_user(id), NULL, ON DELETE SET NULL | Admin who created it |

**Indexes:**
- `assessment_published_idx` on `is_published`

---

## 13. assessments_assessmentpage

Pages within an assessment. Groups questions into sections for the multi-page quiz UI.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| assessment_id | UUID | FK → assessments_assessment(id), NOT NULL, ON DELETE CASCADE | |
| title | VARCHAR(255) | NOT NULL | e.g. "Security Basics" |
| description | TEXT | NULL | Optional section intro shown to intern |
| order | INTEGER | NOT NULL, default=0 | Display order within the assessment (0-based) |

**Constraints:**
- `UNIQUE (assessment_id, order)`

**Indexes:**
- `assessment_page_assessment_idx` on `assessment_id`
- `assessment_page_order_idx` on `(assessment_id, order)`

---

## 14. assessments_assessmentquestion

Individual multiple-choice questions within a page. Choices stored as a JSONB array of strings.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| page_id | UUID | FK → assessments_assessmentpage(id), NOT NULL, ON DELETE CASCADE | |
| prompt | TEXT | NOT NULL | The question text shown to the intern |
| choices | JSONB | NOT NULL | Array of strings e.g. ["Option A", "Option B", "Option C", "Option D"] |
| correct_index | INTEGER | NOT NULL | Zero-based index into the choices array |
| order | INTEGER | NOT NULL, default=0 | Display order within the page (0-based) |

**Constraints:**
- `UNIQUE (page_id, order)`

**Indexes:**
- `assessment_question_page_idx` on `page_id`

---

## 15. assessments_internattempt

Records an intern's attempt at a single assessment. One attempt per intern per assessment enforced at DB level.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| intern_id | UUID | FK → accounts_user(id), NOT NULL, ON DELETE CASCADE | |
| assessment_id | UUID | FK → assessments_assessment(id), NOT NULL, ON DELETE CASCADE | |
| score | DECIMAL(5,2) | NOT NULL, default=0.00 | Score as a percentage 0.00–100.00 |
| completed | BOOLEAN | NOT NULL, default=FALSE | |
| completed_at | TIMESTAMPTZ | NULL | When intern submitted the attempt |
| created_at | TIMESTAMPTZ | NOT NULL, auto | When attempt was started |

**Constraints:**
- `UNIQUE (intern_id, assessment_id)` — one attempt per intern per assessment

**Indexes:**
- `attempt_intern_idx` on `intern_id`
- `attempt_assessment_idx` on `assessment_id`
- `attempt_completed_idx` on `completed`

---

## 16. calendar_calendarevent

Meetings and presentations on the company calendar.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| title | VARCHAR(255) | NOT NULL | |
| date | DATE | NOT NULL | |
| time | TIME | NOT NULL | |
| type | VARCHAR(20) | NOT NULL | meeting \| presentation |
| description | TEXT | NOT NULL, default='' | |

**Indexes:**
- `calendar_event_date_idx` on `date`

---

## 17. calendar_holiday

Registered public and company holidays.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| date | DATE | UNIQUE, NOT NULL | |
| name | VARCHAR(255) | NOT NULL | e.g. "Christmas Day" |

---

## 18. calendar_calendarsettings

Singleton table. Always contains exactly one row with `id=1`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | INTEGER | PK, default=1 | Singleton — enforce in model save() |
| weekend_days | INTEGER[] | NOT NULL, default='{0,6}' | PostgreSQL array; 0=Sun, 6=Sat |
| updated_at | TIMESTAMPTZ | NOT NULL, auto | |

---

## 19. notifications_notification

System-wide notifications with audience targeting.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| title | VARCHAR(255) | NOT NULL | |
| message | TEXT | NOT NULL | |
| type | VARCHAR(20) | NOT NULL | info \| warning \| success \| error |
| audience | VARCHAR(100) | NOT NULL | all \| admin \| intern \| intern:{uuid} |
| created_at | TIMESTAMPTZ | NOT NULL, auto | |

**Indexes:**
- `notifications_audience_idx` on `audience`
- `notifications_created_idx` on `created_at DESC`

---

## 20. notifications_notificationreadstate

Tracks which users have read which notifications.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK, default=uuid4 | |
| notification_id | UUID | FK → notifications_notification(id), NOT NULL, ON DELETE CASCADE | |
| reader_id | UUID | FK → accounts_user(id), NOT NULL, ON DELETE CASCADE | |
| read_at | TIMESTAMPTZ | NOT NULL, auto | |

**Constraints:**
- `UNIQUE (notification_id, reader_id)`

---

## 21. feature_access_featureaccessconfig

Singleton table. Always contains exactly one row with `id=1`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | INTEGER | PK, default=1 | Singleton — enforce in model save() |
| admin_features | JSONB | NOT NULL | Dict of feature_name: bool for admin roles |
| intern_features | JSONB | NOT NULL | Dict of feature_name: bool for intern role |
| updated_at | TIMESTAMPTZ | NOT NULL, auto | |

**Default values:**
```json
// admin_features
{
  "dashboard": true, "batches": true, "interns": true, "dar": true,
  "assessments": true, "projects": true, "laptops": true, "calendar": true,
  "leaves": true, "notifications": true, "profile": true,
  "adminManagement": false, "featureAccess": false
}

// intern_features
{
  "dashboard": true, "attendance": true, "leave": true, "dar": true,
  "laptopIssue": true, "notifications": true, "profile": true
}
```

---

## 22. Relationship Diagram

```
accounts_user
│
├── (1:1) ──► interns_internprofile
│               └── (N:1) ──► batches_batch
│
├── (1:N) ──► interns_internregistrationrequest
│
├── (1:N) ──► attendance_attendancerecord
│
├── (1:N) ──► dar_dailyactivityreport
│
├── (M:N) ──► projects_project
│               via projects_project_assigned_interns
│
├── (1:N) ──► assets_laptop             (assigned_to_id)
├── (1:N) ──► assets_laptopissuereport  (intern_id)
├── (1:N) ──► assets_laptopissuereport  (resolved_by_id)
│
├── (1:N) ──► leaves_leaverequest       (intern_id)
├── (1:N) ──► leaves_leaverequest       (decided_by_id)
│
├── (1:N) ──► assessments_internattempt
│               └── (N:1) ──► assessments_assessment  (created_by_id → accounts_user)
│                               └── (1:N) ──► assessments_assessmentpage
│                                               └── (1:N) ──► assessments_assessmentquestion
│
└── (1:N) ──► notifications_notificationreadstate
                └── (N:1) ──► notifications_notification


calendar_calendarevent              (standalone)
calendar_holiday                    (standalone)
calendar_calendarsettings           (singleton)
feature_access_featureaccessconfig  (singleton)
```

---

## 23. Django Field Type Mapping

Quick reference — how PostgreSQL types in this schema map to Django model fields.

| PostgreSQL Type | Django Field |
|---|---|
| UUID (PK) | `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` |
| UUID (FK) | `ForeignKey(..., on_delete=...)` |
| VARCHAR(n) | `CharField(max_length=n)` |
| TEXT | `TextField()` |
| INTEGER | `IntegerField()` |
| DECIMAL(x,y) | `DecimalField(max_digits=x, decimal_places=y)` |
| FLOAT | `FloatField()` |
| BOOLEAN | `BooleanField()` |
| DATE | `DateField()` |
| TIME | `TimeField()` |
| TIMESTAMPTZ (auto_now_add) | `DateTimeField(auto_now_add=True)` |
| TIMESTAMPTZ (auto_now) | `DateTimeField(auto_now=True)` |
| TIMESTAMPTZ (nullable) | `DateTimeField(null=True, blank=True)` |
| INET | `GenericIPAddressField(null=True, blank=True)` |
| JSONB | `JSONField()` |
| INTEGER[] | `ArrayField(models.IntegerField())` — requires `django.contrib.postgres` |
| ImageField path | `ImageField(upload_to='...')` |
| FileField path | `FileField(upload_to=callable_or_string)` |

---

## 24. Agent Notes — Per Table

Critical warnings for Codex before touching specific tables.

### accounts_user
- `AUTH_USER_MODEL = 'accounts.User'` — set in `base.py` before first migration. Never change after migrating.
- Never add fields here that belong on `interns_internprofile`. User is shared by all roles.
- `last_login_at` is updated manually in `LoginView` — not by Django's built-in `last_login`.
- `is_active` and `is_staff` are Django internals — do not repurpose them.

### interns_internprofile
- `intern_role` is intentionally NULL — do not add a default. It is set by admin after assessment review.
- `assessment_score` is a denormalized aggregate — always recompute via `AssessmentService._update_intern_aggregate()` after any attempt is submitted. Never update it directly in a view.
- `company_account_password` must never appear in any serializer output. Use `write_only=True` or exclude entirely.
- OneToOne with `accounts_user` — always use `select_related('user')` when listing profiles.

### interns_internregistrationrequest
- `password` is hashed on save — use `make_password()` before storing, not `set_password()` (no User instance yet).
- On approval: create `User` + `InternProfile` in a single `@transaction.atomic` block in `InternService.approve_registration()`.

### attendance_attendancerecord
- `UNIQUE (intern_id, date)` — always check for existing record before clock-in. Return 400 if already clocked in today.
- `hours` and `status` are always computed by `AttendanceService` — never accept from client.
- Classification thresholds: late ≥ 09:00, undertime < 17:00, overtime ≥ 18:00.

### leaves_leaverequest
- Fields are `from_date` / `to_date` — **not** `start_date` / `end_date`. This is a common mistake.
- `business_days` is always computed server-side by `CalendarService.count_business_days()` on submission. Never accept from client.
- `type` is required — choices: `sick`, `vacation`, `emergency`, `other`.
- Approval and denial must go through `LeaveService.approve()` / `LeaveService.deny()` — never update status directly in a view.

### assessments_assessmentquestion
- `correct_index` is **never** included in any serializer returned to interns.
- `choices` is a JSONB list of strings — validate it has at least 2 items and `correct_index` is in range in `model.clean()`.
- `order` is 0-based and unique per page — enforce `UNIQUE (page_id, order)`.

### assessments_internattempt
- `UNIQUE (intern_id, assessment_id)` — return 400 if intern tries to create a second attempt.
- `score` is always computed in `AssessmentService.submit()` — never accept from client.
- `completed` flips to `True` only on submit — never on attempt creation.

### calendar_calendarsettings
- Singleton — always `pk=1`. Enforce in `save()` by setting `self.pk = 1`.
- Use `CalendarSettings.get()` classmethod everywhere — never `CalendarSettings.objects.first()`.
- `weekend_days` uses JS convention (0=Sun, 6=Sat). `CalendarService` normalizes to Python `weekday()` (0=Mon) internally.

### feature_access_featureaccessconfig
- Singleton — always `pk=1`. Same singleton pattern as `CalendarSettings`.
- Always-on features must be enforced server-side: admin → `dashboard`, `profile`, `notifications`, `leaves`; intern → `dashboard`, `profile`, `notifications`.
- Use `update_or_create(pk=1, defaults={...})` — never `.create()`.

### notifications_notification
- `audience` is a plain string — valid values: `all`, `admin`, `intern`, `intern:<uuid>`.
- Read state is tracked in `notifications_notificationreadstate` — never on the notification itself.
- Always go through `NotificationService.push()` — never create notification rows directly in views or services.

---

## 25. Changelog

### v2 — March 2026
- **interns_internprofile** — added `github_username`, `assessment_required`, `assessment_completed_at`, `assessment_score`; `intern_role` is now NULL by default (assigned by admin after assessment review)
- **interns_internregistrationrequest** — added `github_username`; removed old `interns_assessmentresult` table (replaced by the new assessment system)
- **leaves_leaverequest** — renamed `start_date` → `from_date`, `end_date` → `to_date`; added `business_days`, `type`, `admin_note`
- **assets_laptopissuereport** — new table for intern-filed laptop issue reports
- **assessments_assessment** — new table; replaces old singleton AssessmentTemplate; supports multiple assessments per skill area
- **assessments_assessmentpage** — new table
- **assessments_assessmentquestion** — new table
- **assessments_internattempt** — new table; replaces old `interns_assessmentresult`; enforces one attempt per intern per assessment
- **feature_access_featureaccessconfig** — added `assessments` to admin features, `laptopIssue` to intern features
