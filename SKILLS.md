# SKILLS.md — INTERNOVA Capability Map

> Slash commands and automated workflows for the Codex agent.
> Each skill has a trigger command, a step-by-step workflow, and an input/output example.
> Before running any skill, confirm you have read AGENTS.md, CONTEXT.md, and Schema.md.

---

## Skill Index

| Command | Description |
|---|---|
| `/scaffold <app>` | Scaffold a full Django app with all files |
| `/endpoint <app> <method> <path>` | Generate a single endpoint in an existing app |
| `/serializers <app> <model>` | Generate list + detail serializer pair |
| `/refactor-service <app> <view>` | Refactor a view to move logic into services.py |
| `/migrate <app>` | Generate, review, and apply a migration safely |
| `/tests <app> <target>` | Generate tests for an existing view or service |
| `/seed <app>` | Generate or update the seed command for an app |
| `/debug` | Debug a traceback and apply a fix |

---

## /scaffold \<app\>

**When to use:** Starting a new Django app from scratch — generates all required files following INTERNOVA conventions.

### Workflow

```
1. Read Schema.md — identify all tables belonging to this app
2. Read STANDARDS.md — confirm naming conventions
3. Create the app directory structure:
   apps/<app>/
   ├── __init__.py
   ├── admin.py
   ├── apps.py
   ├── models.py
   ├── serializers.py
   ├── views.py
   ├── urls.py
   ├── services.py
   ├── filters.py
   ├── permissions.py
   └── tests/
       ├── __init__.py
       ├── test_models.py
       ├── test_services.py
       └── test_views.py
4. Write models.py — all models for this app, inherit BaseModel, define Meta.db_table, indexes, unique_together
5. Write services.py — stub all service classes and methods needed based on CONTEXT.md
6. Write serializers.py — list + detail pairs for each model
7. Write views.py — ViewSets and any non-standard views
8. Write urls.py — DefaultRouter + any extra paths
9. Write filters.py — FilterSet classes for filterable endpoints
10. Register app in config/settings/base.py LOCAL_APPS
11. Add URL include in config/api_urls.py
12. Run /migrate <app>
13. Write tests — test_models.py, test_services.py, test_views.py
14. Run tests: python manage.py test apps.<app> --verbosity=2
15. Fix until all tests pass
16. Update PLAN.md — mark scaffold complete
```

### Example

**Input:**
```
/scaffold leaves
```

**Output — file tree:**
```
apps/leaves/
├── models.py          → LeaveRequest model, LeaveTypeChoices, LeaveStatusChoices
├── serializers.py     → LeaveRequestListSerializer, LeaveRequestDetailSerializer
├── views.py           → LeaveRequestViewSet with approve/deny actions
├── urls.py            → router.register('leaves', LeaveRequestViewSet)
├── services.py        → LeaveService.approve(), LeaveService.deny()
├── filters.py         → LeaveRequestFilter (type, status, from_date, to_date)
├── permissions.py     → (uses IsAdmin, IsIntern, IsAdminOrSelf from accounts)
└── tests/
    ├── test_models.py   → field defaults, choices validation
    ├── test_services.py → approve/deny logic, notification trigger
    └── test_views.py    → submit, approve, deny, permission checks per role
```

**Key conventions applied:**
- `from_date` / `to_date` — not `start_date` / `end_date`
- `business_days` computed server-side in `LeaveService`, not accepted from client
- Approval/denial goes through `LeaveService` — never direct `status` update in view
- `admin_note` included on deny action

---

## /endpoint \<app\> \<method\> \<path\>

**When to use:** Adding a single new route to an existing app.

### Workflow

```
1. Read CONTEXT.md Section 6 — confirm this endpoint is listed and check its auth level
2. Read Schema.md — confirm the relevant table and fields
3. Determine endpoint type:
   - Standard CRUD action → add to existing ViewSet
   - Custom action → add @action to ViewSet
   - Standalone view → create new APIView or GenericAPIView
4. Write the service method in services.py if business logic is needed
5. Write the view / action
6. Register the URL if it is a standalone view (router handles ViewSet actions)
7. Write tests — success, validation failure, wrong role (403)
8. Run tests: python manage.py test apps.<app> --verbosity=2
9. Update PLAN.md
```

### Example

**Input:**
```
/endpoint attendance POST /api/v1/attendance/clock-in/
```

**Output:**

```python
# apps/attendance/services.py
class AttendanceService:
    @staticmethod
    @transaction.atomic
    def clock_in(intern: User) -> AttendanceRecord:
        today = timezone.now().date()
        if AttendanceRecord.objects.filter(intern=intern, date=today).exists():
            raise ValidationError('You have already clocked in today.')
        login_time = timezone.now().time()
        record = AttendanceRecord.objects.create(
            intern=intern,
            date=today,
            login_time=login_time,
            status=AttendanceService.classify(login_time, None),
        )
        return record

# apps/attendance/views.py
class ClockInView(APIView):
    permission_classes = [IsIntern]

    def post(self, request):
        record = AttendanceService.clock_in(intern=request.user)
        return Response(AttendanceRecordSerializer(record).data, status=status.HTTP_201_CREATED)

# apps/attendance/urls.py (added)
path('attendance/clock-in/', ClockInView.as_view(), name='attendance-clock-in'),
```

**Tests generated:**
```python
test_clock_in_success()              # intern clocks in → 201
test_clock_in_duplicate_fails()      # second clock-in today → 400
test_clock_in_admin_forbidden()      # admin hits clock-in → 403
test_clock_in_status_classified()    # login at 09:15 → status='late'
```

---

## /serializers \<app\> \<model\>

**When to use:** Generating a list + detail serializer pair for a model, following INTERNOVA split-serializer conventions.

### Workflow

```
1. Read Schema.md — identify all fields for this model
2. Identify:
   - Fields safe for list view (lightweight — id, name, status, key FKs)
   - Fields only in detail view (all fields, nested relations)
   - Fields that are write-only (password, company_account_password)
   - Fields that are read-only (computed: hours, status, business_days, score)
   - Fields never exposed to interns (correct_index)
3. Write <Model>ListSerializer — lean, no nested objects
4. Write <Model>DetailSerializer — full fields, SerializerMethodField for computed values
5. If model has role-sensitive fields → write a third admin-only serializer
6. Add validate_<field>() methods for any fields requiring custom validation
7. Update views.py to use get_serializer_class() to switch between list and detail
```

### Example

**Input:**
```
/serializers assessments AssessmentQuestion
```

**Output:**

```python
# apps/assessments/serializers.py

class AssessmentQuestionSerializer(serializers.ModelSerializer):
    """Intern-safe serializer — correct_index excluded."""
    class Meta:
        model = AssessmentQuestion
        fields = ['id', 'prompt', 'choices', 'order']

class AssessmentQuestionAdminSerializer(serializers.ModelSerializer):
    """Admin-only serializer — includes correct_index."""
    class Meta:
        model = AssessmentQuestion
        fields = ['id', 'prompt', 'choices', 'correct_index', 'order']

    def validate_choices(self, value):
        if not isinstance(value, list) or len(value) < 2:
            raise serializers.ValidationError('choices must be a list with at least 2 options.')
        return value

    def validate(self, data):
        choices = data.get('choices', [])
        correct_index = data.get('correct_index', 0)
        if not (0 <= correct_index < len(choices)):
            raise serializers.ValidationError({'correct_index': 'Index is out of range for the choices list.'})
        return data
```

**View integration:**
```python
def get_serializer_class(self):
    if self.request.user.role == RoleChoices.INTERN:
        return AssessmentQuestionSerializer       # hides correct_index
    return AssessmentQuestionAdminSerializer      # includes correct_index
```

---

## /refactor-service \<app\> \<view\>

**When to use:** A view contains business logic that should live in `services.py`.

### Workflow

```
1. Read the target view — identify all logic that is not HTTP handling:
   - ORM queries beyond get_object_or_404
   - Status transitions (e.g. leave.status = 'approved')
   - Computations (e.g. score calculation)
   - Cross-model writes
   - Notification triggers
2. Write tests for the current behavior before changing anything (if tests don't exist)
3. Create or open services.py in the target app
4. Extract the logic into a static method on a Service class
5. Wrap multi-step writes in @transaction.atomic
6. Replace the logic in the view with a single service call
7. Run tests — confirm behavior is unchanged
8. Update MEMORY.md — note what was refactored and why
9. Update PLAN.md
```

### Example

**Input:**
```
/refactor-service leaves LeaveRequestApproveView
```

**Before (view with logic):**
```python
class LeaveRequestApproveView(APIView):
    def post(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk)
        leave.status = 'approved'
        leave.decided_at = timezone.now()
        leave.decided_by = request.user
        leave.save()
        Notification.objects.create(
            title='Leave Approved',
            message=f'Your leave has been approved.',
            audience=f'intern:{leave.intern_id}',
            type='success',
        )
        return Response({'status': 'approved'})
```

**After (view delegates to service):**
```python
# apps/leaves/services.py
class LeaveService:
    @staticmethod
    @transaction.atomic
    def approve(leave: LeaveRequest, decided_by) -> LeaveRequest:
        if leave.status != LeaveStatusChoices.PENDING:
            raise ValidationError('Only pending leave requests can be approved.')
        leave.status = LeaveStatusChoices.APPROVED
        leave.decided_at = timezone.now()
        leave.decided_by = decided_by
        leave.save(update_fields=['status', 'decided_at', 'decided_by'])
        from apps.notifications.services import NotificationService
        NotificationService.push(
            title='Leave Approved',
            message=f'Your leave from {leave.from_date} to {leave.to_date} has been approved.',
            audience=f'intern:{leave.intern_id}',
            type='success',
        )
        return leave

# apps/leaves/views.py
class LeaveRequestViewSet(ModelViewSet):
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        updated = LeaveService.approve(leave=leave, decided_by=request.user)
        return Response(LeaveRequestDetailSerializer(updated).data)
```

---

## /migrate \<app\>

**When to use:** After modifying a model — generates, reviews, and applies a migration safely.

### Workflow

```
1. Confirm you are in the correct venv
2. Run: python manage.py makemigrations <app>
3. Open the generated migration file — read every operation:
   - CreateModel → OK
   - AddField → OK
   - AlterField → OK, confirm it matches Schema.md
   - RenameField → OK, confirm old and new names match Schema.md
   - RemoveField → STOP. Do not proceed. Report to developer.
   - DeleteModel → STOP. Do not proceed. Report to developer.
4. Confirm the migration matches the intended Schema.md change
5. Run: python manage.py migrate
6. Confirm: "OK" with no errors
7. Run: python manage.py check
8. Update PLAN.md
```

### Example

**Input:**
```
/migrate interns
```

**Output — migration review checklist:**
```
Generated: apps/interns/migrations/0003_internprofile_github_username.py

Operations:
  ✅ AddField — interns_internprofile.github_username (VARCHAR 100, nullable) → matches Schema.md
  ✅ No RemoveField or DeleteModel operations

Running: python manage.py migrate
  Applying interns.0003_internprofile_github_username... OK

python manage.py check
  System check identified no issues (0 silenced).

PLAN.md updated — migration step marked complete.
```

**If a dangerous operation is detected:**
```
⛔ STOP — Migration contains RemoveField on interns_internprofile.batch_id.
This was not in the task scope. Do not apply.
Reporting to developer before proceeding.
```

---

## /tests \<app\> \<target\>

**When to use:** Generating tests for an existing view, service, or model that has no or insufficient coverage.

### Workflow

```
1. Read the target file (view, service, or model)
2. Identify all cases to test:
   - Happy path (success)
   - Validation failure (400)
   - Permission denied — wrong role (403)
   - Not found (404)
   - Business rule violations (e.g. duplicate clock-in, already submitted attempt)
3. Write test class in the appropriate test file:
   - Views → tests/test_views.py using APITestCase
   - Services → tests/test_services.py using TestCase
   - Models → tests/test_models.py using TestCase
4. Use force_authenticate — never hardcode tokens
5. Use setUp() to create shared fixtures (users, profiles, batches)
6. Run: python manage.py test apps.<app> --verbosity=2
7. Fix until all pass
8. Update PLAN.md
```

### Example

**Input:**
```
/tests assessments InternAttemptViewSet
```

**Output:**
```python
# apps/assessments/tests/test_views.py

class InternAttemptViewSetTests(APITestCase):

    def setUp(self):
        self.intern = User.objects.create_user(
            email='intern@test.com', name='Test Intern',
            password='testpass123', role=RoleChoices.INTERN,
        )
        self.admin = User.objects.create_user(
            email='admin@test.com', name='Admin',
            password='testpass123', role=RoleChoices.STAFFADMIN,
        )
        self.assessment = Assessment.objects.create(
            title='Test Assessment', is_published=True,
        )
        self.page = AssessmentPage.objects.create(
            assessment=self.assessment, title='Page 1', order=0,
        )
        self.q1 = AssessmentQuestion.objects.create(
            page=self.page, prompt='Q1?',
            choices=['A', 'B', 'C', 'D'], correct_index=1, order=0,
        )
        self.q2 = AssessmentQuestion.objects.create(
            page=self.page, prompt='Q2?',
            choices=['A', 'B', 'C', 'D'], correct_index=2, order=1,
        )

    # ── Happy path ─────────────────────────────────────────────────────────
    def test_intern_can_start_attempt(self):
        self.client.force_authenticate(user=self.intern)
        response = self.client.post(reverse('attempt-list'), {'assessment': str(self.assessment.id)})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['completed'])

    def test_intern_can_submit_attempt(self):
        self.client.force_authenticate(user=self.intern)
        attempt = InternAttempt.objects.create(intern=self.intern, assessment=self.assessment)
        answers = [
            {'question_id': str(self.q1.id), 'selected_index': 1},  # correct
            {'question_id': str(self.q2.id), 'selected_index': 0},  # wrong
        ]
        response = self.client.post(
            reverse('attempt-submit', kwargs={'pk': str(attempt.id)}),
            {'answers': answers}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['score']), 50.0)
        self.assertTrue(response.data['completed'])

    # ── Validation failures ─────────────────────────────────────────────────
    def test_duplicate_attempt_fails(self):
        self.client.force_authenticate(user=self.intern)
        self.client.post(reverse('attempt-list'), {'assessment': str(self.assessment.id)})
        response = self.client.post(reverse('attempt-list'), {'assessment': str(self.assessment.id)})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resubmit_completed_attempt_fails(self):
        self.client.force_authenticate(user=self.intern)
        attempt = InternAttempt.objects.create(
            intern=self.intern, assessment=self.assessment,
            completed=True, score=80,
        )
        response = self.client.post(
            reverse('attempt-submit', kwargs={'pk': str(attempt.id)}),
            {'answers': []}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Permission checks ───────────────────────────────────────────────────
    def test_admin_cannot_start_attempt(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse('attempt-list'), {'assessment': str(self.assessment.id)})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_correct_index_not_in_assessment_response(self):
        self.client.force_authenticate(user=self.intern)
        response = self.client.get(reverse('assessment-detail', kwargs={'pk': str(self.assessment.id)}))
        questions = response.data['pages'][0]['questions']
        self.assertNotIn('correct_index', questions[0])
```

---

## /seed \<app\>

**When to use:** Creating or updating the seed data for a specific app inside the `seed_dev` management command.

### Workflow

```
1. Read the existing seed command: apps/<any_app>/management/commands/seed_dev.py
2. Read the mock data in CONTEXT.md Section 12 for the target app
3. Write or update the seed block for this app:
   - Use get_or_create — never create() — seed must be idempotent
   - Reference previously seeded objects by variable, not by hardcoded ID
   - Add a print() confirmation line at the end of each block
4. Add a DEBUG guard at the top of the command if not already present
5. Run: python manage.py seed_dev
6. Confirm output — no errors, no duplicate records
7. Update PLAN.md
```

### Example

**Input:**
```
/seed assessments
```

**Output:**
```python
# apps/accounts/management/commands/seed_dev.py (assessments block)

from apps.assessments.models import Assessment, AssessmentPage, AssessmentQuestion

ASSESSMENT_DATA = [
    {
        'title': 'Frontend Developer Assessment',
        'description': 'HTML, CSS, JavaScript, and React basics.',
        'pages': [
            {
                'title': 'Core Concepts',
                'description': 'Fundamental frontend knowledge.',
                'questions': [
                    {'prompt': 'What does CSS stand for?', 'choices': ['Cascading Style Sheets', 'Computer Style Sheets', 'Creative Style System', 'Coded Style Syntax'], 'correct_index': 0},
                    {'prompt': 'Which hook manages state in React?', 'choices': ['useEffect', 'useState', 'useRef', 'useContext'], 'correct_index': 1},
                ],
            },
            {
                'title': 'Practical Skills',
                'description': 'Applied frontend development.',
                'questions': [
                    {'prompt': 'What is the CSS box model?', 'choices': ['A layout method', 'Content + Padding + Border + Margin', 'A flex container', 'A grid system'], 'correct_index': 1},
                ],
            },
        ],
    },
    # ... Backend, QA, Business Analyst assessments follow same structure
]

def seed_assessments(admin_user):
    for assessment_data in ASSESSMENT_DATA:
        pages_data = assessment_data.pop('pages')
        assessment, created = Assessment.objects.get_or_create(
            title=assessment_data['title'],
            defaults={**assessment_data, 'is_published': True, 'created_by': admin_user},
        )
        for page_order, page_data in enumerate(pages_data):
            questions_data = page_data.pop('questions')
            page, _ = AssessmentPage.objects.get_or_create(
                assessment=assessment,
                order=page_order,
                defaults={**page_data},
            )
            for q_order, q_data in enumerate(questions_data):
                AssessmentQuestion.objects.get_or_create(
                    page=page,
                    order=q_order,
                    defaults={**q_data},
                )
    print(f'  ✅ Seeded {len(ASSESSMENT_DATA)} assessments')
```

**Guard at top of command:**
```python
def handle(self, *args, **kwargs):
    if not settings.DEBUG:
        raise CommandError('seed_dev can only run in DEBUG mode.')
    ...
```

---

## /debug

**When to use:** A traceback or unexpected behavior needs to be diagnosed and fixed.

### Workflow

```
1. Read the full traceback — identify:
   - Exception type
   - Exact file and line number
   - The call chain leading to the error
2. Check MEMORY.md — has this error or a similar one occurred before?
3. Categorize the error:
   - ImportError / CircularImport → check cross-app service imports (use function-level imports)
   - IntegrityError → check unique constraints or NOT NULL violations
   - ValidationError → check serializer or service validation logic
   - PermissionDenied → check permission class applied to the view
   - DoesNotExist → replace with get_object_or_404
   - AttributeError on None → missing related object or null FK not handled
   - MigrationError → check migration file for conflicts or missing dependencies
4. Identify the root cause — do not patch symptoms
5. Apply the fix
6. Run tests: python manage.py test apps.<app> --verbosity=2
7. Confirm fix does not break other tests
8. Update MEMORY.md with the bug description and fix
9. Update PLAN.md
```

### Example

**Input:**
```
/debug

ImportError: cannot import name 'NotificationService' from partially initialized module
'apps.notifications.services' (most likely due to a circular import)
  File "apps/leaves/services.py", line 2, in <module>
    from apps.notifications.services import NotificationService
```

**Diagnosis:**
```
Root cause: Module-level cross-app import causes circular dependency.
apps/leaves/services.py imports from apps/notifications/services.py at the top of the file.
If notifications imports from leaves (directly or transitively), this creates a cycle.
```

**Fix:**
```python
# ❌ BEFORE — module-level import
from apps.notifications.services import NotificationService

class LeaveService:
    @staticmethod
    def approve(leave, decided_by):
        NotificationService.push(...)

# ✅ AFTER — function-level import
class LeaveService:
    @staticmethod
    def approve(leave, decided_by):
        from apps.notifications.services import NotificationService
        NotificationService.push(...)
```

**MEMORY.md entry added:**
```
[FIXED] Circular import between apps/leaves/services.py and apps/notifications/services.py.
Fix: move NotificationService import inside the function body in LeaveService.approve().
Pattern applies to all cross-app service imports in this project.
```