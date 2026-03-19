from rest_framework.routers import DefaultRouter

from apps.batches.views import BatchViewSet


router = DefaultRouter()
router.register("batches", BatchViewSet, basename="batch")

urlpatterns = router.urls
