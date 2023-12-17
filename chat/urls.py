from rest_framework_nested import routers
from .views import ChatViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register("chats", ChatViewSet, basename="chats")

chats_router = routers.NestedDefaultRouter(router, "chats", lookup="chat")
chats_router.register("messages", MessageViewSet, basename="chat-messages")

urlpatterns = router.urls + chats_router.urls
