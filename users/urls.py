from rest_framework import routers
from users import views

router = routers.DefaultRouter()

router.register("users", views.UserViewSet)

urlpatterns = router.urls
