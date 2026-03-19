# STANDARDS.md — INTERNOVA Governance

> Architecture patterns, naming conventions, and coding standards for the INTERNOVA Django REST Framework backend.
> Codex enforces these when writing new code and flags violations when reviewing existing code.
> For deep implementation examples, refer to DevelopmentGuide.md.

---

## Table of Contents

1. [Naming Conventions](#1-naming-conventions)
2. [File and Folder Structure](#2-file-and-folder-structure)
3. [Architecture Patterns](#3-architecture-patterns)
4. [Django-Specific Standards](#4-django-specific-standards)
5. [API Design Standards](#5-api-design-standards)
6. [Test Standards](#6-test-standards)
7. [Security Standards](#7-security-standards)
8. [Git and Branching Standards](#8-git-and-branching-standards)
9. [Codex Enforcement Rules](#9-codex-enforcement-rules)

---

## 1. Naming Conventions

### 1.1 Models

- **Class names:** `PascalCase`, singular noun
- **Table names:** `db_table = '<app>_<modelname>'` — always set explicitly

```python
# ✅
class InternProfile(BaseModel):
    class Meta:
        db_table = 'interns_internprofile'

# ❌
class intern_profile(models.Model): ...
class InternProfiles(models.Model): ...
```

---

### 1.2 Model Fields

- **Field names:** `snake_case`
- **FK fields:** suffix `_id` is added automatically by Django — name the field without it
- **Boolean fields:** prefix with `is_` or `has_`
- **DateTime fields:** suffix with `_at`
- **Date fields:** suffix with `_date`

```python
# ✅
is_published = models.BooleanField(default=False)
published_at = models.DateTimeField(null=True)
start_date = models.DateField()
created_by = models.ForeignKey(User, ...)   # Django adds created_by_id in DB

# ❌
published = models.BooleanField()           # ambiguous
publishTime = models.DateTimeField()        # camelCase
startdate = models.DateField()              # no underscore
created_by_id = models.ForeignKey(User, ...) # double _id suffix
```

---

### 1.3 TextChoices Enums

- **Class name:** `<Adjective>Choices` — e.g. `RoleChoices`, `StatusChoices`, `LeaveTypeChoices`
- **Values:** `UPPER_SNAKE_CASE`
- **DB value:** `lowercase`

```python
# ✅
class LeaveTypeChoices(models.TextChoices):
    SICK = 'sick', 'Sick Leave'
    VACATION = 'vacation', 'Vacation'
    EMERGENCY = 'emergency', 'Emergency'
    OTHER = 'other', 'Other'

# ❌
class leave_types(models.TextChoices): ...
class LeaveType(models.TextChoices):
    Sick = 'Sick', 'Sick'   # uppercase DB value, wrong casing
```

---

### 1.4 Serializers

- **Naming:** `<Model><Purpose>Serializer`
- **Purposes:** `List`, `Detail`, `Admin`, `Create`
- Never use a single serializer for all actions on a model with many fields

```python
# ✅
InternListSerializer
InternDetailSerializer
AssessmentQuestionSerializer        # intern-safe
AssessmentQuestionAdminSerializer   # includes correct_index

# ❌
InternSerializer                    # too generic — which one?
InternSerializerV2                  # version suffixes not allowed
```

---

### 1.5 Views and ViewSets

- **ViewSet names:** `<Model>ViewSet`
- **Standalone view names:** `<Action><Model>View` e.g. `ClockInView`, `WeeklyAttendanceSummaryView`
- **Custom action names:** `snake_case` verb e.g. `approve`, `deny`, `publish`, `submit`

```python
# ✅
class LeaveRequestViewSet(ModelViewSet): ...
class ClockInView(APIView): ...

@action(detail=True, methods=['post'])
def approve(self, request, pk=None): ...

# ❌
class LeaveView(ModelViewSet): ...         # too vague
class ApproveLeaveView(APIView): ...       # use action on ViewSet instead
```

---

### 1.6 Services

- **Class names:** `<Model>Service` e.g. `LeaveService`, `AttendanceService`
- **Method names:** verb phrases in `snake_case` e.g. `approve()`, `compute_hours()`, `submit()`
- **Private helpers:** prefix with `_` e.g. `_update_intern_aggregate()`

```python
# ✅
class AssessmentService:
    @staticmethod
    def submit(attempt, answers): ...

    @staticmethod
    def _update_intern_aggregate(intern): ...

# ❌
class AssessmentHelper: ...        # not a service
def assessment_submit(): ...       # function, not a class method
```

---

### 1.7 URLs

- **URL patterns:** `kebab-case`, plural nouns for resources
- **Named URLs:** `<resource>-<action>` e.g. `leave-list`, `leave-detail`, `attendance-clock-in`
- **Base path:** `/api/v1/<resource>/`

```python
# ✅
path('attendance/clock-in/', ClockInView.as_view(), name='attendance-clock-in')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave')

# ❌
path('attendance/clockIn/', ...)        # camelCase in URL
path('attendance/clock_in/', ...)       # underscore in URL
router.register(r'LeaveRequest', ...)   # PascalCase in URL
```

---

### 1.8 Files

- **App files:** always `snake_case` — `models.py`, `serializers.py`, `services.py`, `filters.py`
- **Test files:** `test_<target>.py` — e.g. `test_models.py`, `test_services.py`, `test_views.py`
- **Management commands:** `snake_case` — e.g. `seed_dev.py`
- **Never** create new top-level files outside of established structure without updating AGENTS.md

---

### 1.9 Variables and Parameters

- **Variables:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE` — defined at module level
- **Querysets:** name after the model, plural e.g. `interns`, `leave_requests`

```python
# ✅
leave_requests = LeaveRequest.objects.filter(status='pending')
LATE_THRESHOLD = time(9, 0)

# ❌
leaveRequests = ...     # camelCase
lr = ...                # too abbreviated
```

---

## 2. File and Folder Structure

### 2.1 App Internal Structure

Every app must follow this exact structure. Do not add files outside of it without updating AGENTS.md.

```
apps/<app>/
├── __init__.py
├── admin.py           # Django admin registrations
├── apps.py            # AppConfig
├── models.py          # All models for this app
├── serializers.py     # All serializers for this app
├── views.py           # All views and viewsets
├── urls.py            # Router + urlpatterns
├── services.py        # All business logic
├── filters.py         # django-filter FilterSet classes
├── permissions.py     # App-specific permission classes (if needed)
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_services.py
    └── test_views.py
```

---

### 2.2 Config Structure

```
config/
├── settings/
│   ├── __init__.py
│   ├── base.py        # Shared settings
│   ├── dev.py         # Development overrides
│   └── prod.py        # Production overrides
├── urls.py            # Root URL conf
├── api_urls.py        # All /api/v1/ routes
├── exceptions.py      # Custom exception handler
├── wsgi.py
└── asgi.py
```

---

### 2.3 What Goes Where

| Logic type | File |
|---|---|
| DB field definitions | `models.py` |
| Input validation | `serializers.py` |
| Business logic, DB writes, status transitions | `services.py` |
| HTTP handling (get object, call service, return response) | `views.py` |
| URL registration | `urls.py` |
| QuerySet filtering via query params | `filters.py` |
| Custom permission classes | `permissions.py` or `accounts/permissions.py` |
| Shared permission classes | `apps/accounts/permissions.py` only |

---

## 3. Architecture Patterns

### 3.1 Services Layer — Non-Negotiable

All business logic lives in `services.py`. Views are thin. Serializers only validate.

```python
# ✅ Thin view
class LeaveRequestViewSet(ModelViewSet):
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        updated = LeaveService.approve(leave=leave, decided_by=request.user)
        return Response(LeaveRequestDetailSerializer(updated).data)

# ❌ Fat view
class LeaveRequestViewSet(ModelViewSet):
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'approved'          # ← business logic in view
        leave.decided_at = timezone.now()  # ← business logic in view
        leave.save()
        Notification.objects.create(...)   # ← cross-model write in view
        return Response(...)
```

---

### 3.2 ViewSet Over APIView

Prefer `ModelViewSet` for standard CRUD. Use `APIView` only for standalone endpoints that do not map to a model (e.g. `ClockInView`, `WeeklyAttendanceSummaryView`).

```python
# ✅ Standard CRUD — use ViewSet
class BatchViewSet(ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

# ✅ Non-model endpoint — use APIView
class WeeklyAttendanceSummaryView(APIView):
    def get(self, request): ...

# ❌ Reimplementing CRUD manually in APIView
class BatchView(APIView):
    def get(self, request): ...
    def post(self, request): ...
    def put(self, request, pk): ...
```

---

### 3.3 get_serializer_class for Multiple Serializers

Never use `if/else` inside a view action to pick a serializer. Use `get_serializer_class()`.

```python
# ✅
class InternViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'list':
            return InternListSerializer
        return InternDetailSerializer

# ❌
class InternViewSet(ModelViewSet):
    def retrieve(self, request, pk=None):
        intern = self.get_object()
        serializer = InternDetailSerializer(intern)   # hardcoded in action
        return Response(serializer.data)
```

---

### 3.4 get_queryset for Role Filtering

Never filter by role inside a view action. Always in `get_queryset()`.

```python
# ✅
def get_queryset(self):
    if self.request.user.role == RoleChoices.INTERN:
        return LeaveRequest.objects.filter(intern=self.request.user)
    return LeaveRequest.objects.select_related('intern', 'decided_by').all()

# ❌
def list(self, request):
    if request.user.role == 'intern':
        qs = LeaveRequest.objects.filter(intern=request.user)  # in action
    ...
```

---

### 3.5 perform_create for Injecting Auth User

Never accept `intern`, `sender`, or any user FK from the client request body. Inject from `request.user` in `perform_create()`.

```python
# ✅
def perform_create(self, serializer):
    serializer.save(intern=self.request.user)

# ❌
class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['intern', 'from_date', ...]  # intern accepted from client
```

---

### 3.6 Custom Actions for Workflow Transitions

Use `@action` for state transitions like approve, deny, publish, submit. Never route these through `partial_update`.

```python
# ✅
@action(detail=True, methods=['post'])
def approve(self, request, pk=None): ...

# ❌ — misusing PATCH for a state transition
def partial_update(self, request, pk=None):
    if request.data.get('status') == 'approved':
        # approval logic here — wrong
```

---

## 4. Django-Specific Standards

### 4.1 Always Inherit BaseModel

All models inherit `BaseModel` which provides `id` (UUID), `created_at`, `updated_at`.

```python
# ✅
class LeaveRequest(BaseModel): ...

# ❌
class LeaveRequest(models.Model):
    id = models.AutoField(primary_key=True)  # integer PK — wrong
```

---

### 4.2 Always Define Meta

Every model must define `Meta` with at minimum `db_table` and `ordering`.

```python
class Meta:
    db_table = 'leaves_leaverequest'
    ordering = ['-created_at']
    indexes = [
        models.Index(fields=['status']),
        models.Index(fields=['intern', 'status']),
    ]
```

---

### 4.3 Always Use TextChoices

Never use raw strings for choice fields anywhere in the codebase.

```python
# ✅
if leave.status == LeaveStatusChoices.PENDING: ...

# ❌
if leave.status == 'pending': ...
```

---

### 4.4 Always Use select_related / prefetch_related

Any queryset that accesses related objects must use `select_related` (ForeignKey / OneToOne) or `prefetch_related` (ManyToMany / reverse FK).

```python
# ✅
InternProfile.objects.select_related('user', 'batch').all()
Assessment.objects.prefetch_related('pages__questions').filter(is_published=True)

# ❌
InternProfile.objects.all()  # triggers N+1 when .user is accessed
```

---

### 4.5 Always Use save(update_fields=[...])

All partial updates to existing records must specify `update_fields`. Never call `.save()` with no arguments on an existing record.

```python
# ✅
leave.status = LeaveStatusChoices.APPROVED
leave.save(update_fields=['status', 'decided_at', 'decided_by'])

# ❌
leave.status = LeaveStatusChoices.APPROVED
leave.save()  # saves all fields, triggers all signals
```

---

### 4.6 Always Use timezone.now()

```python
# ✅
from django.utils import timezone
leave.decided_at = timezone.now()

# ❌
from datetime import datetime
leave.decided_at = datetime.now()  # naive datetime, breaks with USE_TZ=True
```

---

### 4.7 Always Use get_object_or_404

```python
# ✅
from django.shortcuts import get_object_or_404
leave = get_object_or_404(LeaveRequest, pk=pk)

# ❌
try:
    leave = LeaveRequest.objects.get(pk=pk)
except LeaveRequest.DoesNotExist:
    return Response({'error': 'Not found'}, status=404)
```

---

### 4.8 Always Use F() for Atomic Numeric Updates

```python
# ✅
from django.db.models import F
InternProfile.objects.filter(pk=pk).update(rendered_hours=F('rendered_hours') + hours)

# ❌
profile = InternProfile.objects.get(pk=pk)
profile.rendered_hours += hours  # race condition
profile.save()
```

---

### 4.9 Always Wrap Multi-Step Writes in @transaction.atomic

```python
# ✅
@staticmethod
@transaction.atomic
def approve_registration(reg_id, decided_by):
    reg = get_object_or_404(InternRegistrationRequest, pk=reg_id)
    user = User.objects.create_user(...)
    InternProfile.objects.create(user=user, ...)
    reg.intern = user
    reg.save(update_fields=['intern', 'status', 'decided_at'])

# ❌ — no transaction, partial write possible if second step fails
def approve_registration(reg_id, decided_by):
    user = User.objects.create_user(...)
    InternProfile.objects.create(user=user, ...)  # if this fails, User is orphaned
```

---

## 5. API Design Standards

### 5.1 URL Structure

```
/api/v1/<resource>/              → list + create
/api/v1/<resource>/{id}/         → retrieve + update + delete
/api/v1/<resource>/{id}/<action>/ → custom action
```

- Resources are **plural**, **kebab-case**
- No verbs in base URLs — verbs go in custom action paths only
- Version prefix `/api/v1/` on all routes

---

### 5.2 HTTP Status Codes

| Situation | Code |
|---|---|
| Successful GET / PATCH / DELETE | 200 |
| Successful POST (resource created) | 201 |
| No content (DELETE with no body) | 204 |
| Validation error | 400 |
| Unauthenticated | 401 |
| Authenticated but forbidden | 403 |
| Resource not found | 404 |
| Business rule violation | 400 |
| Server error | 500 |

```python
# ✅
return Response(serializer.data, status=status.HTTP_201_CREATED)

# ❌
return Response(serializer.data)  # defaults to 200 on POST
```

---

### 5.3 Error Response Shape

All errors use the custom exception handler in `config/exceptions.py`. Two shapes only:

```json
// Single error
{ "error": "Only pending leave requests can be approved." }

// Field-level validation errors
{ "errors": { "from_date": ["This field is required."], "type": ["Invalid choice."] } }
```

- Never return raw strings or unstructured dicts
- Never use DRF's default `{ "detail": "..." }` shape — the custom handler normalizes this

---

### 5.4 Pagination

All list endpoints use `PageNumberPagination` with `PAGE_SIZE = 20` (set in `base.py`).

- Query param: `?page=2`
- Never disable pagination on list endpoints without approval
- Aggregated endpoints (`/summary/weekly/`, `/hours-breakdown/`, `/missing/`) are exempt — they return fixed-size arrays

---

### 5.5 Filtering

All filterable list endpoints use `django-filter` via `FilterSet` classes in `filters.py`.

- Filter params are documented in `CONTEXT.md` per endpoint
- Search uses `?search=<term>` via DRF `SearchFilter`
- Ordering uses `?ordering=<field>` or `?ordering=-<field>` for descending

---

### 5.6 Response Consistency

- List responses always return arrays, never objects
- Detail responses always return objects, never arrays
- Computed fields (progress, business_days, assessment_score) are always included in the response — never require a second request

---

## 6. Test Standards

### 6.1 File Structure

```
apps/<app>/tests/
├── __init__.py
├── test_models.py    → field defaults, constraints, clean() validation, managers
├── test_services.py  → service method logic, transaction behavior, edge cases
└── test_views.py     → HTTP responses, status codes, permission checks, filters
```

---

### 6.2 Test Naming

- **Format:** `test_<subject>_<condition>_<expected_result>`
- Be specific — the test name should make the failure obvious without reading the body

```python
# ✅
def test_clock_in_duplicate_today_returns_400(): ...
def test_approve_leave_denied_status_raises_validation_error(): ...
def test_intern_cannot_access_admin_endpoint(): ...

# ❌
def test_clock_in(): ...          # too vague
def test_leave_approval(): ...    # no condition or expected result
```

---

### 6.3 Required Test Cases Per Endpoint

Every endpoint must have tests for:

| Case | Description |
|---|---|
| Happy path | Success response with correct status code and shape |
| Validation failure | 400 with correct error field |
| Wrong role | 403 for each role that should not have access |
| Not found | 404 when resource does not exist |
| Business rule violation | 400 for domain-specific rejections (duplicate clock-in, resubmit, etc.) |

---

### 6.4 Test Setup Rules

- Always use `setUp()` for shared fixtures — never repeat object creation across tests
- Always use `force_authenticate()` — never hardcode tokens or use `self.client.login()`
- Never use production data or external APIs in tests
- Use `TestCase` for models and services — use `APITestCase` for views

```python
# ✅
class LeaveRequestTests(APITestCase):
    def setUp(self):
        self.intern = User.objects.create_user(
            email='intern@test.com', name='Intern',
            password='pass', role=RoleChoices.INTERN,
        )
        self.client.force_authenticate(user=self.intern)

# ❌
def test_submit_leave(self):
    self.client.login(username='intern@test.com', password='pass')  # session auth
```

---

### 6.5 Run Tests Before Marking Any Task Done

```bash
# Run target app
python manage.py test apps.<app> --verbosity=2

# Run full suite before deployment
python manage.py test apps --verbosity=2
```

A task is not complete until all tests in the target app pass with zero failures.

---

## 7. Security Standards

### 7.1 Sensitive Fields — Never Expose

| Field | Rule |
|---|---|
| `password` | Always `write_only=True` in serializers |
| `company_account_password` | Exclude from all serializer `fields` lists or `write_only=True` |
| `correct_index` | Never include in intern-facing serializers |
| JWT tokens | Never log, store in DB, or return in error responses |

---

### 7.2 Permission Classes — Always Explicit

Every view and ViewSet must declare `permission_classes` explicitly. Never rely on the default from `REST_FRAMEWORK` settings alone.

```python
# ✅
class LeaveRequestViewSet(ModelViewSet):
    permission_classes = [IsAdmin]

    def get_permissions(self):
        if self.action in ('create', 'list'):
            return [IsAdminOrIntern()]
        return [IsAdmin()]

# ❌
class LeaveRequestViewSet(ModelViewSet):
    pass  # relies on global default — easy to misconfigure
```

---

### 7.3 File Upload Validation

All file upload endpoints must validate both `content_type` and `size` in the serializer — never in the view.

```python
# ✅
def validate_file(self, value):
    if value.content_type != 'application/pdf':
        raise serializers.ValidationError('Only PDF files are accepted.')
    if value.size > 10 * 1024 * 1024:
        raise serializers.ValidationError('File size cannot exceed 10MB.')
    return value
```

---

### 7.4 Never Trust Client-Computed Values

The following fields are always computed server-side. If received from the client, ignore them.

| Field | Computed in |
|---|---|
| `hours` | `AttendanceService.compute_hours()` |
| `status` (attendance) | `AttendanceService.classify()` |
| `score` (attempt) | `AssessmentService.submit()` |
| `business_days` (leave) | `CalendarService.count_business_days()` |
| `assessment_score` (profile) | `AssessmentService._update_intern_aggregate()` |

---

### 7.5 Singleton Feature Access Enforcement

Always-on features must be enforced server-side in `FeatureAccessConfig.save()` — never only on the frontend.

```python
# Always-on — admin
ALWAYS_ON_ADMIN = {'dashboard', 'profile', 'notifications', 'leaves'}

# Always-on — intern
ALWAYS_ON_INTERN = {'dashboard', 'profile', 'notifications'}
```

---

## 8. Git and Branching Standards

### 8.1 Branch Naming

```
feature/<app>-<short-description>
bugfix/<app>-<short-description>
refactor/<app>-<short-description>
chore/<description>
```

```bash
# ✅
feature/assessments-submit-endpoint
bugfix/leaves-business-days-computation
refactor/interns-services-layer
chore/update-requirements

# ❌
fix-bug
johns-branch
new-feature-2
```

---

### 8.2 Commit Messages

- **Format:** imperative present tense, 50 chars max for subject
- **Structure:** `<verb> <what>` — no period at end

```bash
# ✅
Add AssessmentService.submit() with server-side scoring
Fix duplicate clock-in check in AttendanceService
Refactor LeaveRequestApproveView to use LeaveService
Add tests for InternAttempt permission checks

# ❌
fixed bug
added new stuff
WIP
Updated code
```

---

### 8.3 What Never to Commit

- `.env` — use `.env.example` with placeholder values
- `__pycache__/`, `*.pyc`, `*.pyo`
- Migration conflicts (`<<<<<<< HEAD` in migration files)
- Hardcoded secrets, tokens, or passwords
- `db.sqlite3` or any local database file

---

### 8.4 Branch Lifecycle

```
main           → production only, never commit directly
develop        → integration branch (if used)
feature/*      → one branch per task, merge via PR
```

- Never push directly to `main`
- Delete feature branches after merge
- One logical change per PR — do not batch unrelated changes

---

## 9. Codex Enforcement Rules

### When Writing New Code

Codex automatically applies all standards above. Before submitting any code:

- [ ] Naming follows Section 1 conventions
- [ ] File is in the correct location per Section 2
- [ ] Business logic is in `services.py` — not in view or serializer
- [ ] `select_related` / `prefetch_related` used on all relational querysets
- [ ] `save(update_fields=[...])` used for all partial updates
- [ ] `timezone.now()` used — not `datetime.now()`
- [ ] `permission_classes` declared explicitly on every view
- [ ] Sensitive fields excluded or `write_only=True`
- [ ] Correct HTTP status codes returned
- [ ] Tests written and passing

### When Reviewing Existing Code

When Codex encounters existing code that violates a standard, it flags it with:

```
⚠️ STANDARDS VIOLATION — <rule reference>
File: <file path>
Line: <line number>
Issue: <description of violation>
Fix: <what should be done>
```

Codex does not silently fix standards violations in existing code without flagging them first. It reports, then asks before fixing.