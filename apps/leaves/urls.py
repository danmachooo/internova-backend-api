from rest_framework.routers import DefaultRouter

from apps.leaves.views import LeaveRequestViewSet


router = DefaultRouter()
router.register("leaves", LeaveRequestViewSet, basename="leave")

urlpatterns = router.urls
