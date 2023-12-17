from rest_framework_nested import routers
from .views import ChatViewSet

router = routers.DefaultRouter()
router.register("chats", ChatViewSet, basename="chats")

urlpatterns = router.urls
