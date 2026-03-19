from django.urls import path

from apps.feature_access.views import FeatureAccessView


urlpatterns = [
    path("feature-access/", FeatureAccessView.as_view(), name="feature-access"),
]

