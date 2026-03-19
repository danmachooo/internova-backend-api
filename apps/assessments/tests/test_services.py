from django.test import TestCase

from apps.accounts.models import User
from apps.assessments.models import Assessment, AssessmentPage, AssessmentQuestion, InternAttempt
from apps.assessments.services import AssessmentService
from apps.interns.models import InternProfile


class AssessmentServiceTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            name="Admin User",
            password="StrongPass123!",
            role=User.RoleChoices.STAFFADMIN,
        )
        self.intern = User.objects.create_user(
            email="intern@example.com",
            name="Intern User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )
        InternProfile.objects.create(
            user=self.intern,
            school="Test School",
            phone="09171234567",
            start_date="2026-03-01",
            birthdate="2000-01-01",
        )
        self.assessment = Assessment.objects.create(
            title="Backend Assessment",
            created_by=self.admin,
            is_published=True,
        )
        self.page = AssessmentPage.objects.create(
            assessment=self.assessment,
            title="Page 1",
            order=0,
        )
        self.question_1 = AssessmentQuestion.objects.create(
            page=self.page,
            prompt="Question 1",
            choices=["A", "B", "C"],
            correct_index=1,
            order=0,
        )
        self.question_2 = AssessmentQuestion.objects.create(
            page=self.page,
            prompt="Question 2",
            choices=["A", "B", "C"],
            correct_index=2,
            order=1,
        )

    def test_submit_updates_score_server_side_and_profile_aggregate(self):
        attempt = InternAttempt.objects.create(intern=self.intern, assessment=self.assessment)

        updated = AssessmentService.submit(
            attempt=attempt,
            answers=[
                {"question_id": self.question_1.id, "selected_index": 1},
                {"question_id": self.question_2.id, "selected_index": 0},
            ],
        )

        self.assertEqual(str(updated.score), "50.00")
        self.assertTrue(updated.completed)

        profile = InternProfile.objects.get(user=self.intern)
        self.assertEqual(str(profile.assessment_score), "50.00")
