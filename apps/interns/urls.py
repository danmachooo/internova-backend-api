from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.interns.views import InternRoleListView, InternViewSet, RegistrationViewSet


router = DefaultRouter()
router.register("interns", InternViewSet, basename="intern")
router.register("registrations", RegistrationViewSet, basename="registration")

urlpatterns = [
    path("intern-roles/", InternRoleListView.as_view(), name="intern-role-list"),
]

urlpatterns += router.urls
