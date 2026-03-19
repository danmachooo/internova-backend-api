from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import User
from apps.assessments.models import Assessment, AssessmentPage, AssessmentQuestion


class AssessmentQuestionModelTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            name="Admin User",
            password="StrongPass123!",
            role=User.RoleChoices.STAFFADMIN,
        )
        self.assessment = Assessment.objects.create(
            title="Backend Assessment",
            created_by=self.admin,
        )
        self.page = AssessmentPage.objects.create(
            assessment=self.assessment,
            title="Page 1",
            order=0,
        )

    def test_clean_rejects_invalid_correct_index(self):
        question = AssessmentQuestion(
            page=self.page,
            prompt="What is Python?",
            choices=["Snake", "Language"],
            correct_index=2,
            order=0,
        )

        with self.assertRaises(ValidationError):
            question.full_clean()
