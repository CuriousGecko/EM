from access.api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'business-elements', views.BusinessElementViewSet)
router.register(r'rules', views.AccessRuleViewSet)

urlpatterns = router.urls
