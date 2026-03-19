from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.assessments.models import Assessment, AssessmentQuestion, InternAttempt
from apps.interns.models import InternProfile


class AssessmentService:
    @staticmethod
    @transaction.atomic
    def submit(*, attempt, answers):
        if attempt.completed:
            raise ValidationError("Completed attempts cannot be resubmitted.")

        question_map = {
            question.id: question
            for question in AssessmentQuestion.objects.filter(
                page__assessment=attempt.assessment
            ).select_related("page")
        }
        if not question_map:
            raise ValidationError("This assessment has no questions.")

        answers_by_question = {}
        for answer in answers:
            question_id = answer["question_id"]
            if question_id in answers_by_question:
                raise ValidationError("Each question can only be answered once.")
            question = question_map.get(question_id)
            if question is None:
                raise ValidationError("Answers must reference questions in this assessment.")
            selected_index = answer["selected_index"]
            if selected_index < 0 or selected_index >= len(question.choices):
                raise ValidationError(
                    {"answers": ["Selected index must point to a valid choice."]}
                )
            answers_by_question[question_id] = selected_index

        total_questions = len(question_map)
        correct_answers = sum(
            1
            for question_id, question in question_map.items()
            if answers_by_question.get(question_id) == question.correct_index
        )
        raw_score = (Decimal(correct_answers) / Decimal(total_questions)) * Decimal("100")
        score = raw_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        attempt.score = score
        attempt.completed = True
        attempt.completed_at = timezone.now()
        attempt.save(update_fields=["score", "completed", "completed_at", "updated_at"])

        AssessmentService._update_intern_aggregate(intern=attempt.intern)
        return attempt

    @staticmethod
    def _update_intern_aggregate(*, intern):
        profile = get_object_or_404(InternProfile.objects.select_related("user"), user=intern)
        completed_attempts = InternAttempt.objects.filter(intern=intern, completed=True)
        published_assessments = Assessment.objects.filter(is_published=True)

        if completed_attempts.exists():
            total_score = sum((attempt.score for attempt in completed_attempts), Decimal("0.00"))
            average_score = (total_score / Decimal(completed_attempts.count())).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
        else:
            average_score = None

        if profile.assessment_required and published_assessments.exists():
            published_ids = set(published_assessments.values_list("id", flat=True))
            completed_ids = set(completed_attempts.values_list("assessment_id", flat=True))
            completed_at = timezone.now() if published_ids.issubset(completed_ids) else None
        else:
            completed_at = None

        profile.assessment_score = average_score
        profile.assessment_completed_at = completed_at
        profile.save(
            update_fields=[
                "assessment_score",
                "assessment_completed_at",
                "updated_at",
            ]
        )
        return profile
