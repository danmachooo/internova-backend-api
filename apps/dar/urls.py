from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.dar.views import DARViewSet


router = DefaultRouter()
router.register("dar", DARViewSet, basename="dar")

urlpatterns = [
]

urlpatterns += router.urls
