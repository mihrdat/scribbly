from rest_framework_nested import routers
from .views import RoomViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register("rooms", RoomViewSet)

room_router = routers.NestedDefaultRouter(router, "rooms", lookup="room")
room_router.register("messages", MessageViewSet, basename="room-messages")

urlpatterns = router.urls + room_router.urls
