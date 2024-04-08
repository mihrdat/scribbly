from rest_framework_nested import routers
from .views import RoomViewSet

router = routers.DefaultRouter()
router.register("rooms", RoomViewSet)

urlpatterns = router.urls
