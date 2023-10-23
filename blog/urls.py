from rest_framework_nested import routers
from .views import AuthorViewSet, CategoryViewSet

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("categories", CategoryViewSet)

urlpatterns = router.urls
