from django.urls import include, path


urlpatterns = [
    path("", include("apps.accounts.urls")),
    path("", include("apps.batches.urls")),
    path("", include("apps.interns.urls")),
    path("", include("apps.assessments.urls")),
    path("", include("apps.attendance.urls")),
    path("", include("apps.dar.urls")),
    path("", include("apps.calendar.urls")),
    path("", include("apps.leaves.urls")),
    path("", include("apps.projects.urls")),
    path("", include("apps.assets.urls")),
    path("", include("apps.notifications.urls")),
    path("", include("apps.feature_access.urls")),
]
