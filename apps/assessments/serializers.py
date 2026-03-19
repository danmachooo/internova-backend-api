from rest_framework import serializers

from apps.accounts.models import User
from apps.assessments.models import (
    Assessment,
    AssessmentPage,
    AssessmentQuestion,
    InternAttempt,
)


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        fields = ("id", "prompt", "choices", "order")


class AssessmentQuestionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        fields = ("id", "prompt", "choices", "correct_index", "order")


class AssessmentPageSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentPage
        fields = ("id", "title", "description", "order", "questions")

    def get_questions(self, obj):
        request = self.context.get("request")
        if request and request.user.role == User.RoleChoices.INTERN:
            serializer_class = AssessmentQuestionSerializer
        else:
            serializer_class = AssessmentQuestionAdminSerializer
        return serializer_class(
            obj.questions.all().order_by("order", "created_at"),
            many=True,
            context=self.context,
        ).data


class AssessmentSerializer(serializers.ModelSerializer):
    pages = AssessmentPageSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = (
            "id",
            "title",
            "description",
            "is_published",
            "published_at",
            "pages",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "published_at", "created_at", "updated_at")


class AssessmentAdminSerializer(serializers.ModelSerializer):
    pages = AssessmentPageSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = (
            "id",
            "title",
            "description",
            "is_published",
            "published_at",
            "created_by",
            "pages",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "published_at", "created_by", "created_at", "updated_at")


class AssessmentPageWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentPage
        fields = ("id", "title", "description", "order")
        read_only_fields = ("id",)


class AssessmentQuestionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        fields = ("id", "prompt", "choices", "correct_index", "order")
        read_only_fields = ("id",)


class InternAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternAttempt
        fields = (
            "id",
            "intern",
            "assessment",
            "score",
            "completed",
            "completed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "intern", "score", "completed", "completed_at", "created_at", "updated_at")


class AnswerItemSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    selected_index = serializers.IntegerField(min_value=0)


class AssessmentSubmitSerializer(serializers.Serializer):
    answers = AnswerItemSerializer(many=True)
