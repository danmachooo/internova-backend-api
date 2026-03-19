from datetime import date, time
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.assessments.models import Assessment, AssessmentPage, AssessmentQuestion
from apps.assets.models import Laptop
from apps.attendance.models import AttendanceRecord
from apps.attendance.services import AttendanceService
from apps.batches.models import Batch
from apps.calendar.models import CalendarEvent, CalendarSettings
from apps.dar.models import DailyActivityReport
from apps.feature_access.models import FeatureAccessConfig
from apps.interns.models import InternProfile
from apps.notifications.models import Notification
from apps.projects.models import Project


ADMIN_USERS = [
    {
        "email": "superadmin@internova.dev",
        "name": "Super Admin",
        "password": "SuperAdmin123!",
        "role": User.RoleChoices.SUPERADMIN,
    },
    {
        "email": "staffadmin@internova.dev",
        "name": "Staff Admin",
        "password": "StaffAdmin123!",
        "role": User.RoleChoices.STAFFADMIN,
    },
]

BATCHES = [
    {
        "name": "Batch 2026-A",
        "start_date": date(2026, 1, 6),
        "end_date": date(2026, 4, 30),
        "status": Batch.StatusChoices.ACTIVE,
        "progress": 65,
    },
    {
        "name": "Batch 2026-B",
        "start_date": date(2026, 2, 3),
        "end_date": date(2026, 5, 29),
        "status": Batch.StatusChoices.ACTIVE,
        "progress": 42,
    },
    {
        "name": "Batch 2025-Z",
        "start_date": date(2025, 9, 1),
        "end_date": date(2025, 12, 19),
        "status": Batch.StatusChoices.COMPLETED,
        "progress": 100,
    },
]

INTERNS = [
    {
        "email": "alice.backend@internova.dev",
        "name": "Alice Backend",
        "password": "InternPass123!",
        "batch": "Batch 2026-A",
        "school": "Polytechnic University of the Philippines",
        "phone": "09170000001",
        "github_username": "alice-backend",
        "required_hours": Decimal("480.00"),
        "start_date": date(2026, 1, 6),
        "birthdate": date(2002, 1, 14),
        "company_account_email": "alice.backend@company.test",
        "company_account_password": "InitPass#101",
    },
    {
        "email": "brandon.qa@internova.dev",
        "name": "Brandon QA",
        "password": "InternPass123!",
        "batch": "Batch 2026-A",
        "school": "Technological University of the Philippines",
        "phone": "09170000002",
        "github_username": "brandon-qa",
        "required_hours": Decimal("480.00"),
        "start_date": date(2026, 1, 6),
        "birthdate": date(2001, 11, 8),
        "company_account_email": "brandon.qa@company.test",
        "company_account_password": "InitPass#102",
    },
    {
        "email": "charlie.frontend@internova.dev",
        "name": "Charlie Frontend",
        "password": "InternPass123!",
        "batch": "Batch 2026-B",
        "school": "University of the East",
        "phone": "09170000003",
        "github_username": "charlie-frontend",
        "required_hours": Decimal("600.00"),
        "start_date": date(2026, 2, 3),
        "birthdate": date(2002, 6, 19),
        "company_account_email": "charlie.frontend@company.test",
        "company_account_password": "InitPass#103",
    },
    {
        "email": "diana.ba@internova.dev",
        "name": "Diana BA",
        "password": "InternPass123!",
        "batch": "Batch 2026-B",
        "school": "Far Eastern University",
        "phone": "09170000004",
        "github_username": "diana-ba",
        "required_hours": Decimal("520.00"),
        "start_date": date(2026, 2, 3),
        "birthdate": date(2001, 3, 27),
        "company_account_email": "diana.ba@company.test",
        "company_account_password": "InitPass#104",
    },
    {
        "email": "ethan.pm@internova.dev",
        "name": "Ethan PM",
        "password": "InternPass123!",
        "batch": "Batch 2025-Z",
        "school": "Mapua University",
        "phone": "09170000005",
        "github_username": "ethan-pm",
        "required_hours": Decimal("480.00"),
        "start_date": date(2025, 9, 1),
        "birthdate": date(2000, 9, 12),
        "company_account_email": "ethan.pm@company.test",
        "company_account_password": "InitPass#105",
    },
]

ASSESSMENTS = [
    {
        "title": "Frontend Developer Assessment",
        "description": "HTML, CSS, JavaScript, accessibility, and React fundamentals.",
        "pages": [
            {
                "title": "Core Frontend Concepts",
                "description": "Browser, markup, styling, and UI fundamentals.",
                "questions": [
                    {
                        "prompt": "What does HTML stand for?",
                        "choices": [
                            "HyperText Markup Language",
                            "HighText Markdown Language",
                            "Hyper Transfer Markup Link",
                            "Home Tool Markup Language",
                        ],
                        "correct_index": 0,
                    },
                    {
                        "prompt": "Which CSS property controls the text color?",
                        "choices": ["font-style", "text-color", "color", "foreground"],
                        "correct_index": 2,
                    },
                    {
                        "prompt": "Which JavaScript method converts JSON text into an object?",
                        "choices": ["JSON.stringify()", "JSON.parse()", "JSON.object()", "JSON.decode()"],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "Which HTML element is best for a primary page heading?",
                        "choices": ["<header>", "<title>", "<h1>", "<p>"],
                        "correct_index": 2,
                    },
                    {
                        "prompt": "Which attribute improves image accessibility?",
                        "choices": ["src", "alt", "role", "href"],
                        "correct_index": 1,
                    },
                ],
            },
            {
                "title": "Applied Frontend Skills",
                "description": "Component thinking and modern frontend practice.",
                "questions": [
                    {
                        "prompt": "Which React hook is commonly used for local state?",
                        "choices": ["useMemo", "useRef", "useEffect", "useState"],
                        "correct_index": 3,
                    },
                    {
                        "prompt": "What does responsive design primarily aim to do?",
                        "choices": [
                            "Block mobile devices",
                            "Adapt layouts to different screen sizes",
                            "Use only grid layouts",
                            "Increase JavaScript bundle size",
                        ],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "Which CSS layout system is one-dimensional?",
                        "choices": ["Grid", "Flexbox", "Positioning", "Float"],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "Why use semantic HTML elements?",
                        "choices": [
                            "To reduce bundle size automatically",
                            "To avoid CSS entirely",
                            "To improve meaning and accessibility",
                            "To replace JavaScript",
                        ],
                        "correct_index": 2,
                    },
                    {
                        "prompt": "Which HTTP status indicates a missing resource?",
                        "choices": ["200", "201", "404", "500"],
                        "correct_index": 2,
                    },
                ],
            },
        ],
    },
    {
        "title": "Backend Developer Assessment",
        "description": "Python, Django, APIs, data modeling, and backend fundamentals.",
        "pages": [
            {
                "title": "Backend Foundations",
                "description": "Core server-side concepts and data flow.",
                "questions": [
                    {
                        "prompt": "Which Python data type is immutable?",
                        "choices": ["list", "dict", "set", "tuple"],
                        "correct_index": 3,
                    },
                    {
                        "prompt": "Which HTTP method is typically used to partially update a resource?",
                        "choices": ["GET", "POST", "PATCH", "OPTIONS"],
                        "correct_index": 2,
                    },
                    {
                        "prompt": "What does ORM stand for?",
                        "choices": [
                            "Object Relational Mapper",
                            "Open Resource Method",
                            "Ordered Request Model",
                            "Object Routing Manager",
                        ],
                        "correct_index": 0,
                    },
                    {
                        "prompt": "Which Django file is intended for business logic in this project?",
                        "choices": ["views.py", "serializers.py", "services.py", "urls.py"],
                        "correct_index": 2,
                    },
                    {
                        "prompt": "What status code is appropriate for a successful POST that creates a resource?",
                        "choices": ["200", "201", "204", "302"],
                        "correct_index": 1,
                    },
                ],
            },
            {
                "title": "Applied Backend Practice",
                "description": "API design and persistence concerns.",
                "questions": [
                    {
                        "prompt": "Which DRF class is preferred for standard CRUD endpoints?",
                        "choices": ["APIView", "ModelViewSet", "TemplateView", "FormView"],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "What is the main reason to wrap multi-step writes in transaction.atomic?",
                        "choices": [
                            "To improve admin styling",
                            "To avoid partial writes on failure",
                            "To add indexes automatically",
                            "To disable validation",
                        ],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "Which field type should be used for a UUID primary key in this project?",
                        "choices": ["AutoField", "IntegerField", "UUIDField", "SlugField"],
                        "correct_index": 2,
                    },
                    {
                        "prompt": "Which function should be used instead of datetime.now()?",
                        "choices": ["time.time()", "timezone.now()", "datetime.utcnow()", "localdate()"],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "What is the risk of module-level cross-app service imports?",
                        "choices": [
                            "Pagination errors",
                            "Template rendering issues",
                            "Circular import errors",
                            "Automatic migrations",
                        ],
                        "correct_index": 2,
                    },
                ],
            },
        ],
    },
    {
        "title": "QA Assessment",
        "description": "Testing fundamentals, bug reporting, and quality practices.",
        "pages": [
            {
                "title": "Testing Basics",
                "description": "Quality mindset and defect handling.",
                "questions": [
                    {
                        "prompt": "What is the primary goal of regression testing?",
                        "choices": [
                            "Add new features",
                            "Verify old behavior still works after changes",
                            "Write deployment scripts",
                            "Measure internet speed",
                        ],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "Which test type checks a single unit of logic in isolation?",
                        "choices": ["Unit test", "Smoke test", "Load test", "UAT"],
                        "correct_index": 0,
                    },
                    {
                        "prompt": "A clear bug report should include:",
                        "choices": [
                            "Only the title",
                            "Reproduction steps and expected vs actual result",
                            "Only the stack trace",
                            "The fix implementation",
                        ],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "Which status code usually signals a client-side validation issue?",
                        "choices": ["201", "301", "400", "503"],
                        "correct_index": 2,
                    },
                    {
                        "prompt": "Which is most appropriate for API endpoint tests in this project?",
                        "choices": ["TestCase", "APITestCase", "SimpleTestCase", "LiveServerTestCase"],
                        "correct_index": 1,
                    },
                ],
            },
            {
                "title": "Applied QA Practice",
                "description": "Practical validation and API-focused quality checks.",
                "questions": [
                    {
                        "prompt": "Why use force_authenticate() in DRF tests?",
                        "choices": [
                            "To skip database setup",
                            "To bypass migrations",
                            "To authenticate without hardcoded tokens",
                            "To disable permissions",
                        ],
                        "correct_index": 2,
                    },
                    {
                        "prompt": "Which scenario belongs in endpoint coverage by default?",
                        "choices": [
                            "Happy path only",
                            "Wrong role permission check",
                            "CSS rendering",
                            "Admin theme preview",
                        ],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "What makes a test name most useful?",
                        "choices": [
                            "It is short but vague",
                            "It states subject, condition, and expected result",
                            "It matches the file name only",
                            "It uses abbreviations heavily",
                        ],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "What should happen when a hidden object is requested by an unauthorized user?",
                        "choices": ["200", "201", "403 or 404 depending on queryset exposure", "500"],
                        "correct_index": 2,
                    },
                    {
                        "prompt": "Which is a business-rule violation example?",
                        "choices": [
                            "Duplicate clock-in on the same day",
                            "Opening admin site",
                            "Running makemigrations",
                            "Creating a branch",
                        ],
                        "correct_index": 0,
                    },
                ],
            },
        ],
    },
    {
        "title": "Business Analyst Assessment",
        "description": "Requirements analysis, communication, and delivery planning.",
        "pages": [
            {
                "title": "BA Fundamentals",
                "description": "Requirements and stakeholder communication basics.",
                "questions": [
                    {
                        "prompt": "What is a primary responsibility of a business analyst?",
                        "choices": [
                            "Maintaining server uptime",
                            "Clarifying requirements and stakeholder needs",
                            "Designing laptop inventory labels",
                            "Approving payroll",
                        ],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "Which artifact best lists functional requirements?",
                        "choices": ["User stories", "Color palette", "Stack trace", "DNS record"],
                        "correct_index": 0,
                    },
                    {
                        "prompt": "Why is acceptance criteria important?",
                        "choices": [
                            "It replaces implementation entirely",
                            "It defines how to judge completion",
                            "It disables QA review",
                            "It removes the need for testing",
                        ],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "What should a BA do when requirements conflict?",
                        "choices": [
                            "Ignore the conflict",
                            "Escalate and facilitate clarification",
                            "Delete one requirement silently",
                            "Ship without confirmation",
                        ],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "Which communication quality matters most in requirement writing?",
                        "choices": ["Ambiguity", "Novelty", "Clarity", "Length"],
                        "correct_index": 2,
                    },
                ],
            },
            {
                "title": "Applied BA Skills",
                "description": "Working with teams to shape delivery.",
                "questions": [
                    {
                        "prompt": "A user story commonly follows which format?",
                        "choices": [
                            "As a <user>, I want <goal>, so that <value>",
                            "Bug, fix, done",
                            "GET, POST, PATCH",
                            "Plan, code, deploy",
                        ],
                        "correct_index": 0,
                    },
                    {
                        "prompt": "What helps reduce scope confusion during delivery?",
                        "choices": [
                            "Keeping decisions undocumented",
                            "A shared source of truth and change tracking",
                            "Skipping sprint review",
                            "Hiding requirements from QA",
                        ],
                        "correct_index": 1,
                    },
                    {
                        "prompt": "Which question is best during stakeholder discovery?",
                        "choices": [
                            "What problem are we solving?",
                            "Can we skip validation?",
                            "Should we remove tests?",
                            "Can we launch today without review?",
                        ],
                        "correct_index": 0,
                    },
                    {
                        "prompt": "What is the value of process mapping?",
                        "choices": [
                            "It visualizes the current and future workflow",
                            "It replaces code reviews",
                            "It stores JWT tokens",
                            "It deploys migrations",
                        ],
                        "correct_index": 0,
                    },
                    {
                        "prompt": "Which is a sign of a strong requirement?",
                        "choices": [
                            "It is testable and specific",
                            "It is intentionally vague",
                            "It is hidden from developers",
                            "It only exists verbally",
                        ],
                        "correct_index": 0,
                    },
                ],
            },
        ],
    },
]

PROJECTS = [
    {
        "name": "Atlas Dashboard",
        "description": "Internal reporting dashboard for intern coordinators.",
        "status": Project.StatusChoices.ACTIVE,
        "start_date": date(2026, 3, 1),
        "end_date": date(2026, 5, 30),
        "interns": ["alice.backend@internova.dev", "charlie.frontend@internova.dev"],
    },
    {
        "name": "Pulse API",
        "description": "Backend services for attendance and DAR reporting.",
        "status": Project.StatusChoices.ACTIVE,
        "start_date": date(2026, 3, 3),
        "end_date": date(2026, 6, 15),
        "interns": ["alice.backend@internova.dev", "brandon.qa@internova.dev"],
    },
    {
        "name": "Beacon QA Suite",
        "description": "API and regression test suite improvements.",
        "status": Project.StatusChoices.ON_HOLD,
        "start_date": date(2026, 2, 20),
        "end_date": date(2026, 5, 10),
        "interns": ["brandon.qa@internova.dev", "diana.ba@internova.dev"],
    },
    {
        "name": "Orbit Planning Hub",
        "description": "Requirements tracking and project intake workflows.",
        "status": Project.StatusChoices.COMPLETED,
        "start_date": date(2025, 10, 1),
        "end_date": date(2025, 12, 15),
        "interns": ["ethan.pm@internova.dev", "diana.ba@internova.dev"],
    },
]

LAPTOPS = [
    {
        "brand": "Dell Latitude 5440",
        "serial_no": "INT-LAP-001",
        "ip_address": "10.0.10.11",
        "assigned_to": "alice.backend@internova.dev",
        "status": Laptop.StatusChoices.ASSIGNED,
        "accounts": "alice.backend",
    },
    {
        "brand": "Lenovo ThinkPad E14",
        "serial_no": "INT-LAP-002",
        "ip_address": "10.0.10.12",
        "assigned_to": "brandon.qa@internova.dev",
        "status": Laptop.StatusChoices.ASSIGNED,
        "accounts": "brandon.qa",
    },
    {
        "brand": "HP ProBook 440",
        "serial_no": "INT-LAP-003",
        "ip_address": "10.0.10.13",
        "assigned_to": "charlie.frontend@internova.dev",
        "status": Laptop.StatusChoices.ASSIGNED,
        "accounts": "charlie.frontend",
    },
    {
        "brand": "Acer TravelMate P2",
        "serial_no": "INT-LAP-004",
        "ip_address": "10.0.10.14",
        "assigned_to": "diana.ba@internova.dev",
        "status": Laptop.StatusChoices.ISSUED,
        "accounts": "diana.ba",
    },
    {
        "brand": "ASUS ExpertBook B1",
        "serial_no": "INT-LAP-005",
        "ip_address": "10.0.10.15",
        "assigned_to": None,
        "status": Laptop.StatusChoices.AVAILABLE,
        "accounts": "spare-device",
    },
]

CALENDAR_EVENTS = [
    {
        "title": "Orientation Kickoff",
        "date": date(2026, 3, 24),
        "time": time(9, 0),
        "type": CalendarEvent.TypeChoices.MEETING,
        "description": "Welcome session for the current intern cohorts.",
    },
    {
        "title": "Backend Check-in",
        "date": date(2026, 3, 25),
        "time": time(14, 0),
        "type": CalendarEvent.TypeChoices.MEETING,
        "description": "Weekly technical alignment for backend-related work.",
    },
    {
        "title": "Sprint Demo Day",
        "date": date(2026, 3, 27),
        "time": time(15, 0),
        "type": CalendarEvent.TypeChoices.PRESENTATION,
        "description": "Cross-team presentation of weekly output and learnings.",
    },
    {
        "title": "Business Review",
        "date": date(2026, 3, 31),
        "time": time(10, 30),
        "type": CalendarEvent.TypeChoices.PRESENTATION,
        "description": "Stakeholder review of planning and delivery updates.",
    },
]

NOTIFICATIONS = [
    {
        "title": "Welcome to INTERNOVA",
        "message": "Review your dashboard, profile, and active tasks for this week.",
        "type": Notification.TypeChoices.INFO,
        "audience": "all",
    },
    {
        "title": "Admin Weekly Sync",
        "message": "Admin sync starts every Monday at 9:00 AM.",
        "type": Notification.TypeChoices.WARNING,
        "audience": "admin",
    },
    {
        "title": "DAR Reminder",
        "message": "Please upload your Daily Activity Report before 6:00 PM.",
        "type": Notification.TypeChoices.INFO,
        "audience": "intern",
    },
    {
        "title": "Assessment Access Ready",
        "message": "Published assessments are now available in your portal.",
        "type": Notification.TypeChoices.SUCCESS,
        "audience": "intern",
    },
]


class Command(BaseCommand):
    help = "Seed development data for INTERNOVA."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise CommandError("seed_dev can only run in DEBUG mode.")

        self.stdout.write(self.style.NOTICE("Seeding INTERNOVA development data..."))

        admin_users = self.seed_admin_users()
        batches = self.seed_batches()
        interns = self.seed_interns(batches=batches)
        self.seed_assessments(created_by=admin_users["superadmin"])
        self.seed_attendance(interns=interns)
        self.seed_dar_records(interns=interns)
        self.seed_projects(interns=interns)
        self.seed_laptops(interns=interns)
        self.seed_calendar_events()
        self.seed_calendar_settings()
        self.seed_feature_access()
        self.seed_notifications()

        self.stdout.write(self.style.SUCCESS("seed_dev completed successfully."))

    @staticmethod
    def apply_updates(instance, values):
        changed_fields = []
        for field_name, expected_value in values.items():
            if getattr(instance, field_name) != expected_value:
                setattr(instance, field_name, expected_value)
                changed_fields.append(field_name)
        return changed_fields

    def seed_admin_users(self):
        seeded_users = {}
        for admin_data in ADMIN_USERS:
            user, _ = User.objects.get_or_create(
                email=admin_data["email"],
                defaults={
                    "name": admin_data["name"],
                    "role": admin_data["role"],
                    "status": User.StatusChoices.ACTIVE,
                },
            )
            changed_fields = self.apply_updates(
                user,
                {
                    "name": admin_data["name"],
                    "role": admin_data["role"],
                    "status": User.StatusChoices.ACTIVE,
                },
            )
            if not user.check_password(admin_data["password"]):
                user.set_password(admin_data["password"])
                changed_fields.append("password")
            if changed_fields:
                user.save(update_fields=[*set(changed_fields + ["is_active", "is_staff", "updated_at"])])
            seeded_users[user.role] = user

        self.stdout.write("  OK Seeded 2 admin users")
        return seeded_users

    def seed_batches(self):
        batches = {}
        for batch_data in BATCHES:
            batch, _ = Batch.objects.get_or_create(
                name=batch_data["name"],
                defaults={
                    "start_date": batch_data["start_date"],
                    "end_date": batch_data["end_date"],
                    "status": batch_data["status"],
                    "progress": batch_data["progress"],
                },
            )
            changed_fields = self.apply_updates(
                batch,
                {
                    "start_date": batch_data["start_date"],
                    "end_date": batch_data["end_date"],
                    "status": batch_data["status"],
                    "progress": batch_data["progress"],
                },
            )
            if changed_fields:
                batch.save(update_fields=[*changed_fields, "updated_at"])
            batches[batch.name] = batch

        self.stdout.write("  OK Seeded 3 batches")
        return batches

    def seed_interns(self, *, batches):
        interns = {}
        for intern_data in INTERNS:
            user, _ = User.objects.get_or_create(
                email=intern_data["email"],
                defaults={
                    "name": intern_data["name"],
                    "role": User.RoleChoices.INTERN,
                    "status": User.StatusChoices.ACTIVE,
                },
            )
            user_changed_fields = self.apply_updates(
                user,
                {
                    "name": intern_data["name"],
                    "role": User.RoleChoices.INTERN,
                    "status": User.StatusChoices.ACTIVE,
                },
            )
            if not user.check_password(intern_data["password"]):
                user.set_password(intern_data["password"])
                user_changed_fields.append("password")
            if user_changed_fields:
                user.save(
                    update_fields=[*set(user_changed_fields + ["is_active", "is_staff", "updated_at"])]
                )

            profile, _ = InternProfile.objects.get_or_create(
                user=user,
                defaults={
                    "batch": batches[intern_data["batch"]],
                    "school": intern_data["school"],
                    "phone": intern_data["phone"],
                    "github_username": intern_data["github_username"],
                    "required_hours": intern_data["required_hours"],
                    "start_date": intern_data["start_date"],
                    "birthdate": intern_data["birthdate"],
                    "company_account_email": intern_data["company_account_email"],
                    "company_account_password": intern_data["company_account_password"],
                    "assessment_required": True,
                },
            )
            profile_changed_fields = self.apply_updates(
                profile,
                {
                    "batch": batches[intern_data["batch"]],
                    "school": intern_data["school"],
                    "phone": intern_data["phone"],
                    "github_username": intern_data["github_username"],
                    "required_hours": intern_data["required_hours"],
                    "start_date": intern_data["start_date"],
                    "birthdate": intern_data["birthdate"],
                    "company_account_email": intern_data["company_account_email"],
                    "company_account_password": intern_data["company_account_password"],
                    "assessment_required": True,
                },
            )
            if profile_changed_fields:
                profile.save(update_fields=[*profile_changed_fields, "updated_at"])
            interns[user.email] = user

        self.stdout.write("  OK Seeded 5 interns with profiles")
        return interns

    def seed_assessments(self, *, created_by):
        for assessment_data in ASSESSMENTS:
            assessment, _ = Assessment.objects.get_or_create(
                title=assessment_data["title"],
                defaults={
                    "description": assessment_data["description"],
                    "is_published": True,
                    "published_at": timezone.now(),
                    "created_by": created_by,
                },
            )
            assessment_changed_fields = self.apply_updates(
                assessment,
                {
                    "description": assessment_data["description"],
                    "is_published": True,
                    "created_by": created_by,
                },
            )
            if assessment.published_at is None:
                assessment.published_at = timezone.now()
                assessment_changed_fields.append("published_at")
            if assessment_changed_fields:
                assessment.save(update_fields=[*set(assessment_changed_fields + ["updated_at"])])

            for page_order, page_data in enumerate(assessment_data["pages"]):
                page, _ = AssessmentPage.objects.get_or_create(
                    assessment=assessment,
                    order=page_order,
                    defaults={
                        "title": page_data["title"],
                        "description": page_data["description"],
                    },
                )
                page_changed_fields = self.apply_updates(
                    page,
                    {
                        "title": page_data["title"],
                        "description": page_data["description"],
                    },
                )
                if page_changed_fields:
                    page.save(update_fields=[*page_changed_fields, "updated_at"])

                for question_order, question_data in enumerate(page_data["questions"]):
                    question, _ = AssessmentQuestion.objects.get_or_create(
                        page=page,
                        order=question_order,
                        defaults={
                            "prompt": question_data["prompt"],
                            "choices": question_data["choices"],
                            "correct_index": question_data["correct_index"],
                        },
                    )
                    question_changed_fields = self.apply_updates(
                        question,
                        {
                            "prompt": question_data["prompt"],
                            "choices": question_data["choices"],
                            "correct_index": question_data["correct_index"],
                        },
                    )
                    if question_changed_fields:
                        question.save(update_fields=[*question_changed_fields, "updated_at"])

        self.stdout.write("  OK Seeded 4 published assessments with pages and questions")

    def seed_attendance(self, *, interns):
        attendance_schedule = {
            "alice.backend@internova.dev": [
                (time(8, 45), time(17, 15)),
                (time(8, 55), time(17, 30)),
                (time(8, 50), time(18, 5)),
                (time(8, 40), time(17, 0)),
                (time(9, 5), time(17, 10)),
            ],
            "brandon.qa@internova.dev": [
                (time(9, 10), time(17, 5)),
                (time(9, 0), time(17, 20)),
                (time(8, 58), time(16, 30)),
                (time(8, 47), time(17, 0)),
                (time(8, 50), time(18, 15)),
            ],
            "charlie.frontend@internova.dev": [
                (time(8, 30), time(17, 0)),
                (time(8, 35), time(17, 10)),
                (time(9, 20), time(17, 25)),
                (time(8, 45), time(16, 40)),
                (time(8, 55), time(17, 0)),
            ],
            "diana.ba@internova.dev": [
                (time(8, 50), time(17, 5)),
                (time(8, 45), time(18, 0)),
                (time(8, 40), time(17, 30)),
                (time(9, 2), time(17, 0)),
                (time(8, 35), time(17, 45)),
            ],
            "ethan.pm@internova.dev": [
                (time(8, 55), time(17, 0)),
                (time(8, 50), time(17, 5)),
                (time(8, 45), time(17, 15)),
                (time(8, 42), time(18, 10)),
                (time(9, 0), time(16, 45)),
            ],
        }
        attendance_dates = [
            date(2026, 3, 16),
            date(2026, 3, 17),
            date(2026, 3, 18),
            date(2026, 3, 19),
            date(2026, 3, 20),
        ]

        for email, schedule in attendance_schedule.items():
            intern = interns[email]
            for record_date, (login_time, logout_time) in zip(attendance_dates, schedule):
                hours = AttendanceService.compute_hours(
                    login_time=login_time,
                    logout_time=logout_time,
                )
                status = AttendanceService.classify(
                    login_time=login_time,
                    logout_time=logout_time,
                )
                record, _ = AttendanceRecord.objects.get_or_create(
                    intern=intern,
                    date=record_date,
                    defaults={
                        "login_time": login_time,
                        "logout_time": logout_time,
                        "hours": hours,
                        "status": status,
                    },
                )
                changed_fields = self.apply_updates(
                    record,
                    {
                        "login_time": login_time,
                        "logout_time": logout_time,
                        "hours": hours,
                        "status": status,
                    },
                )
                if changed_fields:
                    record.save(update_fields=[*changed_fields, "updated_at"])

        for intern in interns.values():
            AttendanceService._sync_rendered_hours(intern=intern)

        self.stdout.write("  OK Seeded 25 attendance records across 5 days")

    def seed_dar_records(self, *, interns):
        for dar_data in [
            {
                "email": "alice.backend@internova.dev",
                "date": date(2026, 3, 19),
                "filename": "alice-dar.pdf",
                "upload_time": time(17, 12),
            },
            {
                "email": "brandon.qa@internova.dev",
                "date": date(2026, 3, 19),
                "filename": "brandon-dar.pdf",
                "upload_time": time(17, 18),
            },
            {
                "email": "charlie.frontend@internova.dev",
                "date": date(2026, 3, 19),
                "filename": "charlie-dar.pdf",
                "upload_time": time(17, 9),
            },
            {
                "email": "diana.ba@internova.dev",
                "date": date(2026, 3, 19),
                "filename": "diana-dar.pdf",
                "upload_time": time(17, 25),
            },
        ]:
            intern = interns[dar_data["email"]]
            file_path = f"dar/{intern.id}/{dar_data['date']}_{dar_data['filename']}"
            report, _ = DailyActivityReport.objects.get_or_create(
                intern=intern,
                date=dar_data["date"],
                defaults={
                    "file": file_path,
                    "upload_time": dar_data["upload_time"],
                    "status": DailyActivityReport.StatusChoices.SUBMITTED,
                },
            )
            changed_fields = self.apply_updates(
                report,
                {
                    "file": file_path,
                    "upload_time": dar_data["upload_time"],
                    "status": DailyActivityReport.StatusChoices.SUBMITTED,
                },
            )
            if changed_fields:
                report.save(update_fields=[*changed_fields, "updated_at"])

        self.stdout.write("  OK Seeded 4 DAR records")

    def seed_projects(self, *, interns):
        for project_data in PROJECTS:
            project, _ = Project.objects.get_or_create(
                name=project_data["name"],
                defaults={
                    "description": project_data["description"],
                    "status": project_data["status"],
                    "start_date": project_data["start_date"],
                    "end_date": project_data["end_date"],
                },
            )
            changed_fields = self.apply_updates(
                project,
                {
                    "description": project_data["description"],
                    "status": project_data["status"],
                    "start_date": project_data["start_date"],
                    "end_date": project_data["end_date"],
                },
            )
            if changed_fields:
                project.save(update_fields=[*changed_fields, "updated_at"])
            project.assigned_interns.set([interns[email] for email in project_data["interns"]])

        self.stdout.write("  OK Seeded 4 projects with assignments")

    def seed_laptops(self, *, interns):
        for laptop_data in LAPTOPS:
            assigned_to = interns.get(laptop_data["assigned_to"]) if laptop_data["assigned_to"] else None
            laptop, _ = Laptop.objects.get_or_create(
                serial_no=laptop_data["serial_no"],
                defaults={
                    "brand": laptop_data["brand"],
                    "ip_address": laptop_data["ip_address"],
                    "assigned_to": assigned_to,
                    "status": laptop_data["status"],
                    "accounts": laptop_data["accounts"],
                },
            )
            changed_fields = self.apply_updates(
                laptop,
                {
                    "brand": laptop_data["brand"],
                    "ip_address": laptop_data["ip_address"],
                    "assigned_to": assigned_to,
                    "status": laptop_data["status"],
                    "accounts": laptop_data["accounts"],
                },
            )
            if changed_fields:
                laptop.save(update_fields=[*changed_fields, "updated_at"])

        self.stdout.write("  OK Seeded 5 laptops")

    def seed_calendar_events(self):
        for event_data in CALENDAR_EVENTS:
            event, _ = CalendarEvent.objects.get_or_create(
                title=event_data["title"],
                date=event_data["date"],
                time=event_data["time"],
                defaults={
                    "type": event_data["type"],
                    "description": event_data["description"],
                },
            )
            changed_fields = self.apply_updates(
                event,
                {
                    "type": event_data["type"],
                    "description": event_data["description"],
                },
            )
            if changed_fields:
                event.save(update_fields=[*changed_fields, "updated_at"])

        self.stdout.write("  OK Seeded 4 calendar events")

    def seed_calendar_settings(self):
        calendar_settings = CalendarSettings.get()
        if calendar_settings.weekend_days != [0, 6]:
            calendar_settings.weekend_days = [0, 6]
            calendar_settings.save(update_fields=["weekend_days", "updated_at"])

        self.stdout.write("  OK Seeded CalendarSettings singleton")

    def seed_feature_access(self):
        feature_access = FeatureAccessConfig.get()
        expected_admin = dict(FeatureAccessConfig.DEFAULT_ADMIN_FEATURES)
        expected_intern = dict(FeatureAccessConfig.DEFAULT_INTERN_FEATURES)
        changed_fields = self.apply_updates(
            feature_access,
            {
                "admin_features": expected_admin,
                "intern_features": expected_intern,
            },
        )
        if changed_fields:
            feature_access.save(update_fields=[*changed_fields, "updated_at"])

        self.stdout.write("  OK Seeded FeatureAccessConfig singleton")

    def seed_notifications(self):
        for notification_data in NOTIFICATIONS:
            notification, _ = Notification.objects.get_or_create(
                title=notification_data["title"],
                audience=notification_data["audience"],
                defaults={
                    "message": notification_data["message"],
                    "type": notification_data["type"],
                },
            )
            changed_fields = self.apply_updates(
                notification,
                {
                    "message": notification_data["message"],
                    "type": notification_data["type"],
                },
            )
            if changed_fields:
                notification.save(update_fields=[*changed_fields, "updated_at"])

        self.stdout.write("  OK Seeded 4 notifications")
