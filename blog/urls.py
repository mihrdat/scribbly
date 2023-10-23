from rest_framework_nested import routers
from .views import AuthorViewSet, CategoryViewSet, ArticleViewSet

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("categories", CategoryViewSet)
router.register("articles", ArticleViewSet)

urlpatterns = router.urls
