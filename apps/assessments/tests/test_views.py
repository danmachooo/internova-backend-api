from unittest.mock import patch

from django.db import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.assessments.models import Assessment, AssessmentPage, AssessmentQuestion, InternAttempt
from apps.interns.models import InternProfile


class AssessmentViewTests(APITestCase):
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
            description="Test assessment",
            created_by=self.admin,
            is_published=True,
        )
        self.page = AssessmentPage.objects.create(
            assessment=self.assessment,
            title="Page 1",
            description="Intro",
            order=0,
        )
        self.question = AssessmentQuestion.objects.create(
            page=self.page,
            prompt="Question 1",
            choices=["A", "B", "C"],
            correct_index=1,
            order=0,
        )

    def test_correct_index_never_in_intern_response(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.get(reverse("assessment-detail", args=[self.assessment.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        question = response.data["pages"][0]["questions"][0]
        self.assertNotIn("correct_index", question)

    def test_score_computed_server_side(self):
        self.client.force_authenticate(user=self.intern)
        create_response = self.client.post(
            reverse("attempt-list"),
            {"assessment": str(self.assessment.id), "score": "100.00"},
            format="json",
        )
        attempt_id = create_response.data["id"]

        submit_response = self.client.post(
            reverse("attempt-submit", args=[attempt_id]),
            {
                "answers": [
                    {"question_id": str(self.question.id), "selected_index": 1},
                ],
                "score": "0.00",
            },
            format="json",
        )

        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)
        self.assertEqual(submit_response.data["score"], "100.00")

    def test_duplicate_attempt_rejected(self):
        InternAttempt.objects.create(intern=self.intern, assessment=self.assessment)
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(
            reverse("attempt-list"),
            {"assessment": str(self.assessment.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "You already started this assessment.")

    @patch("apps.assessments.views.InternAttempt.objects.create")
    def test_duplicate_attempt_race_returns_400(self, mock_create):
        mock_create.side_effect = IntegrityError("duplicate key value violates unique constraint")
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(
            reverse("attempt-list"),
            {"assessment": str(self.assessment.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "You already started this assessment.")

    def test_resubmit_rejected(self):
        attempt = InternAttempt.objects.create(
            intern=self.intern,
            assessment=self.assessment,
            completed=True,
        )
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(
            reverse("attempt-submit", args=[attempt.id]),
            {
                "answers": [
                    {"question_id": str(self.question.id), "selected_index": 1},
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Completed attempts cannot be resubmitted.")

    def test_admin_cannot_start_attempt(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("attempt-list"),
            {"assessment": str(self.assessment.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
