from rest_framework.routers import DefaultRouter

from apps.assets.views import LaptopIssueReportViewSet, LaptopViewSet


router = DefaultRouter()
router.register("laptops", LaptopViewSet, basename="laptop")
router.register("laptop-issues", LaptopIssueReportViewSet, basename="laptop-issue")

urlpatterns = router.urls
