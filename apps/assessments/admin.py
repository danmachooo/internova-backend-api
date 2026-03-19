from django.contrib import admin

from apps.assessments.models import (
    Assessment,
    AssessmentPage,
    AssessmentQuestion,
    InternAttempt,
)


class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion
    extra = 0


class AssessmentPageInline(admin.TabularInline):
    model = AssessmentPage
    extra = 0


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at", "created_by")
    list_filter = ("is_published",)
    search_fields = ("title", "description")
    inlines = [AssessmentPageInline]


@admin.register(AssessmentPage)
class AssessmentPageAdmin(admin.ModelAdmin):
    list_display = ("assessment", "title", "order")
    list_filter = ("assessment",)
    inlines = [AssessmentQuestionInline]


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ("page", "order", "correct_index")
    list_filter = ("page__assessment",)
    search_fields = ("prompt",)


@admin.register(InternAttempt)
class InternAttemptAdmin(admin.ModelAdmin):
    list_display = ("intern", "assessment", "score", "completed", "completed_at")
    list_filter = ("completed", "assessment")
